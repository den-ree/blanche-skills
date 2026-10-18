"""Parse .bindify markdown into a history-first data model."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FRONTMATTER_RE = re.compile(r"^\*\*([^:]+):\*\*\s*(.+)$", re.MULTILINE)
STEP_HEADING_RE = re.compile(r"^### Step-(\d+):\s*(.+)$", re.MULTILINE)
UPDATE_ENTRY_RE = re.compile(
    r"^## \[([^\]]+)\] Step-(\d+):\s*(.+)$", re.MULTILINE
)
UPDATE_MERGE_RE = re.compile(
    r"^## \[([^\]]+)\] (.+)$", re.MULTILINE
)
HISTORY_INDEX_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$", re.MULTILINE)
BACKTICK_PATH_RE = re.compile(r"`([^`]+)`")
ARCH_IMPACT_RE = re.compile(
    r"^-\s*`(\w+)`\s*(.+)$", re.MULTILINE
)
EVIDENCE_STEP_RE = re.compile(
    r"^-\s*Step updates:\s*`([^`#]+)(?:#([^`]+))?`\s*—\s*(.+)$", re.MULTILINE
)
EVIDENCE_PLAIN_RE = re.compile(
    r"^-\s*(\w+):\s*`([^`]+)`\s*(?:—\s*(.+))?$", re.MULTILINE
)


@dataclass
class Ref:
    id: str
    path: str
    label: str
    kind: str
    route: str
    external: bool = False


@dataclass
class PlanRow:
    name: str
    status: str
    notes: str
    path: str = ""


@dataclass
class StepUpdate:
    step_id: str
    title: str
    timestamp: str = ""
    summary: list = field(default_factory=list)
    impact: list = field(default_factory=list)
    file_changes: list = field(default_factory=list)
    architecture_ref_ids: list[str] = field(default_factory=list)
    architecture_links: list = field(default_factory=list)
    impact_flows: list = field(default_factory=list)
    has_impact: bool = False
    has_architecture: bool = False


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    return {
        m.group(1).strip(): m.group(2).strip().strip("`")
        for m in FRONTMATTER_RE.finditer(text)
    }


def extract_section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_subsection(text: str, heading: str) -> str:
    pattern = rf"^### {re.escape(heading)}\s*\n(.*?)(?=^### |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def wiki_links(text: str) -> list[tuple[str, str]]:
    return [
        (m.group(1).strip(), (m.group(2) or m.group(1)).strip())
        for m in WIKI_LINK_RE.finditer(text)
    ]


INLINE_TOKEN_RE = re.compile(
    r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]|`([^`]+)`"
)


def rich_segments(text: str, source: Path | None, index: "RefIndex") -> list[dict[str, str]]:
    """Split markdown into text, code, and resolved object refs."""
    if not text or not text.strip():
        return []
    segments: list[dict[str, str]] = []
    pos = 0
    for match in INLINE_TOKEN_RE.finditer(text):
        if match.start() > pos:
            segments.append({"type": "text", "text": text[pos:match.start()]})
        code = match.group(3)
        if code is not None:
            ref = None
            if "/" in code or code.endswith(".md"):
                ref = index.get_by_path(code, source)
            if ref:
                segments.append({"type": "ref", "ref_id": ref.id})
            else:
                segments.append({"type": "code", "text": code})
        else:
            target = match.group(1).strip()
            ref = index.get_by_path(target, source) if source else None
            if ref is None:
                ref = index.get_arch(target, source or index.bindify_root / "architecture" / "_map.md")
            if ref:
                segments.append({"type": "ref", "ref_id": ref.id})
            else:
                segments.append({"type": "text", "text": (match.group(2) or target).strip()})
        pos = match.end()
    if pos < len(text):
        segments.append({"type": "text", "text": text[pos:]})
    return [segment for segment in segments if segment.get("text") or segment.get("ref_id")]


def markdown_blocks(text: str, source: Path | None, index: "RefIndex") -> list[dict[str, Any]]:
    """Keep paragraphs and bullet lists instead of flattening markdown into one line."""
    blocks: list[dict[str, Any]] = []
    paragraph: list[str] = []
    bullets: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        segments = rich_segments(" ".join(paragraph), source, index)
        paragraph.clear()
        if segments:
            blocks.append({"type": "p", "segments": segments})

    def flush_bullets() -> None:
        if not bullets:
            return
        items = [rich_segments(line, source, index) for line in bullets]
        bullets.clear()
        blocks.append({"type": "ul", "items": items})

    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line == "---" or line.startswith("#"):
            flush_paragraph()
            flush_bullets()
            continue
        if line.startswith(("- ", "* ")):
            flush_paragraph()
            bullets.append(line[2:].strip())
            continue
        flush_bullets()
        paragraph.append(line)
    flush_paragraph()
    flush_bullets()
    return blocks


def bullet_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            lines.append(stripped[2:].strip())
        elif stripped.startswith("* "):
            lines.append(stripped[2:].strip())
    return lines


def normalize_arch_id(path: Path, bindify_root: Path) -> str:
    try:
        rel = path.relative_to(bindify_root / "architecture")
        return rel.with_suffix("").as_posix()
    except ValueError:
        return path.stem


def rel_to_bindify(path: Path, bindify_root: Path) -> str:
    return path.relative_to(bindify_root).as_posix()


def resolve_path(bindify_root: Path, raw: str, source: Path | None = None) -> Path | None:
    raw = raw.strip().split("#")[0]
    if raw.startswith("http"):
        return None
    if not raw.endswith(".md"):
        raw = f"{raw}.md"
    if raw.startswith(("architecture/", "development/", "docs/", "history/")):
        candidate = bindify_root / raw
    elif source is not None:
        candidate = (source.parent / raw).resolve()
    else:
        candidate = (bindify_root / raw).resolve()
    return candidate if candidate.exists() else None


def plan_name_from_path(path: Path) -> str:
    if path.name in ("plan.md", "brief.md", "proposal.md", "updates.md", "verify.md"):
        return path.parent.name
    return path.stem


def file_kind(path: Path, bindify_root: Path) -> str:
    rel = rel_to_bindify(path, bindify_root)
    if rel.startswith("history/entries/"):
        return "history"
    if rel.startswith("history/"):
        return "history-index"
    if "/plans/" in rel:
        name = path.name.replace(".md", "")
        return {"brief": "brief", "proposal": "proposal", "plan": "plan",
                "updates": "updates", "verify": "verify"}.get(name, "plan")
    if rel.startswith("architecture/"):
        return "arch"
    if rel.endswith("coordinator.md"):
        return "coordinator"
    if rel.startswith("docs/"):
        return "doc"
    return "file"


def humanize(stem: str) -> str:
    text = stem.replace("-", " ").replace("_", " ").strip()
    text = re.sub(r"\bapi\b", "API", text, flags=re.I)
    text = re.sub(r"\bui\b", "UI", text, flags=re.I)
    text = re.sub(r"\bspm\b", "SPM", text, flags=re.I)
    text = re.sub(r"\bcefr\b", "CEFR", text, flags=re.I)
    text = re.sub(r"\bmvp\b", "MVP", text, flags=re.I)
    return text[:1].upper() + text[1:] if text else text


def friendly_label(path: Path, bindify_root: Path) -> str:
    kind = file_kind(path, bindify_root)
    if kind == "arch":
        return humanize(path.stem)
    if kind in ("plan", "brief", "proposal", "updates", "verify"):
        plan = humanize(plan_name_from_path(path))
        kind_label = {
            "plan": "Plan",
            "brief": "Brief",
            "proposal": "Proposal",
            "updates": "Updates",
            "verify": "Verify",
        }.get(path.stem.replace(".md", ""), humanize(path.stem))
        return f"{kind_label} · {plan}"
    if kind == "history":
        return path.stem.split("-", 3)[-1].replace("-", " ") if "-" in path.stem else path.stem
    if kind == "coordinator":
        return f"{path.parent.name} coordinator"
    if kind == "doc":
        return path.stem.replace("-", " ")
    return path.stem


def route_for_path(path: Path, bindify_root: Path) -> str:
    kind = file_kind(path, bindify_root)
    rel = rel_to_bindify(path, bindify_root)
    if kind == "arch":
        return f"#/arch/{normalize_arch_id(path, bindify_root)}"
    if kind in ("plan", "brief", "proposal", "updates", "verify"):
        return f"#/plan/{plan_name_from_path(path)}"
    if kind == "history":
        slug = path.stem
        if re.match(r"\d{4}-\d{2}-\d{2}-", slug):
            slug = slug[11:]
        return f"#/history/{slug}"
    if kind == "coordinator":
        return f"#/file/{rel.replace('/', '--')}"
    if kind == "doc":
        return f"#/file/{rel.replace('/', '--')}"
    return f"#/file/{rel.replace('/', '--')}"


def step_label(step_id: str, title: str) -> str:
    return f"Step-{step_id}: {title}"


def step_route(plan_name: str, step_id: str) -> str:
    return f"#/step/{plan_name}/{step_id}"


class RefIndex:
    def __init__(self, bindify_root: Path) -> None:
        self.bindify_root = bindify_root
        self.refs: dict[str, Ref] = {}
        self._path_to_id: dict[str, str] = {}

    def add(self, path: Path, ref_id: str, label: str | None = None, kind: str | None = None,
            route: str | None = None, external: bool = False) -> Ref:
        rel = rel_to_bindify(path, self.bindify_root) if path else ""
        kind = kind or (file_kind(path, self.bindify_root) if path else "external")
        label = label or (friendly_label(path, self.bindify_root) if path else ref_id)
        route = route or (route_for_path(path, self.bindify_root) if path else "")
        ref = Ref(id=ref_id, path=str(path) if path else "", label=label, kind=kind,
                  route=route, external=external)
        self.refs[ref_id] = ref
        if path:
            self._path_to_id[rel] = ref_id
        return ref

    def add_external(self, ref_id: str, label: str, url: str) -> Ref:
        ref = Ref(id=ref_id, path=url, label=label, kind="external",
                  route=url, external=True)
        self.refs[ref_id] = ref
        return ref

    def get_by_path(self, raw_path: str, source: Path | None = None) -> Ref | None:
        resolved = resolve_path(self.bindify_root, raw_path, source)
        if not resolved:
            return None
        rel = rel_to_bindify(resolved, self.bindify_root)
        if rel in self._path_to_id:
            return self.refs[self._path_to_id[rel]]
        ref_id = rel.replace("/", "--")
        return self.add(resolved, ref_id)

    def get_arch(self, wiki_target: str, source: Path) -> Ref | None:
        resolved = resolve_path(self.bindify_root, wiki_target, source)
        if not resolved:
            stem = Path(wiki_target.split("#", 1)[0]).stem
            matches = [
                path for path in (self.bindify_root / "architecture").rglob("*.md")
                if path.stem == stem
            ]
            resolved = matches[0] if len(matches) == 1 else None
        if not resolved:
            return None
        arch_id = normalize_arch_id(resolved, self.bindify_root)
        ref_id = f"arch/{arch_id}"
        if ref_id in self.refs:
            return self.refs[ref_id]
        return self.add(resolved, ref_id, label=resolved.stem, kind="arch",
                        route=f"#/arch/{arch_id}")

    def get_step(self, plan_name: str, step_id: str, title: str) -> Ref:
        ref_id = f"step/{plan_name}/{step_id}"
        if ref_id in self.refs:
            return self.refs[ref_id]
        return Ref(id=ref_id, path="", label=step_label(step_id, title), kind="step",
                   route=step_route(plan_name, step_id))

    def build_from_tree(self) -> None:
        for path in sorted(self.bindify_root.rglob("*.md")):
            if ".obsidian" in path.parts:
                continue
            rel = rel_to_bindify(path, self.bindify_root)
            kind = file_kind(path, self.bindify_root)
            if kind == "arch":
                arch_id = normalize_arch_id(path, self.bindify_root)
                self.add(path, f"arch/{arch_id}")
            elif kind == "history":
                slug = path.stem
                if re.match(r"\d{4}-\d{2}-\d{2}-", slug):
                    slug = slug[11:]
                self.add(path, f"history/{slug}", route=f"#/history/{slug}")
            elif kind in ("plan", "brief", "proposal", "updates", "verify"):
                plan = plan_name_from_path(path)
                self.add(path, f"plan-artifact/{plan}/{path.stem.replace('.md', '')}")
            elif kind == "coordinator":
                self.add(path, f"file/{rel.replace('/', '--')}")
            elif kind == "doc":
                self.add(path, f"file/{rel.replace('/', '--')}")


FLOW_RE = re.compile(r"`([^`]+)`\s*(?:→|->)\s*`([^`]+)`")


def parse_architecture_links(section_text: str, source: Path, index: RefIndex) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        action_match = re.match(r"`(\w+)`\s*(.*)", line[2:])
        if not action_match:
            continue
        action = action_match.group(1)
        rest = action_match.group(2)
        note = ""
        if " — " in rest:
            wiki_part, note = rest.split(" — ", 1)
        else:
            wiki_part = rest
        for target, _ in wiki_links(wiki_part):
            ref = index.get_arch(target, source)
            if not ref:
                continue
            key = (action, ref.id)
            if key in seen:
                continue
            seen.add(key)
            links.append({"action": action, "ref_id": ref.id, "note": note.strip()})
    return links


def parse_impact_flows(impact: str) -> list[dict[str, str]]:
    flows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for match in FLOW_RE.finditer(impact or ""):
        pair = (match.group(1).strip(), match.group(2).strip())
        if pair in seen or not pair[0] or not pair[1]:
            continue
        seen.add(pair)
        flows.append({"from": pair[0], "to": pair[1]})
    return flows


def parse_updates_full(updates_path: Path, plan_name: str, index: RefIndex) -> list[StepUpdate]:
    if not updates_path.exists():
        return []
    text = read_text(updates_path)
    entries: list[StepUpdate] = []
    for match in UPDATE_ENTRY_RE.finditer(text):
        start = match.start()
        next_match = UPDATE_ENTRY_RE.search(text, match.end())
        end = next_match.start() if next_match else len(text)
        block = text[start:end]
        step_id = match.group(2)
        title = match.group(3).strip()
        summary = extract_subsection(block, "Summary")
        summary_items = [
            rich_segments(line.strip()[2:].strip() if line.strip().startswith(("- ", "* ")) else line.strip(), updates_path, index)
            for line in (summary or "").splitlines()
            if line.strip()
        ]
        file_changes = bullet_lines(extract_subsection(block, "File Changes"))
        impact = extract_subsection(block, "Impact & Connections")
        impact_line = " ".join(line.strip("- ").strip() for line in impact.splitlines() if line.strip())
        arch_section = extract_subsection(block, "Architecture")
        arch_links = parse_architecture_links(arch_section, updates_path, index)
        index.get_step(plan_name, step_id, title)
        entries.append(
            StepUpdate(
                step_id=step_id,
                title=title,
                timestamp=match.group(1),
                summary=summary_items,
                impact=rich_segments(impact_line[:700], updates_path, index),
                file_changes=[rich_segments(line, updates_path, index) for line in file_changes],
                architecture_ref_ids=[link["ref_id"] for link in arch_links],
                architecture_links=arch_links,
                impact_flows=parse_impact_flows(impact),
                has_impact=bool(impact.strip()),
                has_architecture=bool(arch_section.strip()),
            )
        )
    return entries


def parse_plan_steps(plan_path: Path) -> list[dict[str, str]]:
    if not plan_path.exists():
        return []
    text = read_text(plan_path)
    return [
        {"id": m.group(1), "title": m.group(2).strip()}
        for m in STEP_HEADING_RE.finditer(text)
    ]


def detect_phase(plan_dir: Path) -> tuple[str, str]:
    has_brief = (plan_dir / "brief.md").exists()
    has_proposal = (plan_dir / "proposal.md").exists()
    has_plan = (plan_dir / "plan.md").exists()
    has_updates = (plan_dir / "updates.md").exists()
    has_verify = (plan_dir / "verify.md").exists()
    status = ""
    if has_proposal:
        status = parse_frontmatter(read_text(plan_dir / "proposal.md")).get("Status", "")
    if has_verify:
        verify_status = parse_frontmatter(read_text(plan_dir / "verify.md")).get("Status", "")
        if verify_status == "passed":
            return "done", verify_status
    if has_verify:
        return "verify", status or "in review"
    if has_updates:
        return "executing", status or "executing"
    if has_plan:
        return "plan", status or "approved"
    if has_proposal:
        return "proposal", status or "proposed"
    if has_brief:
        return "brief", status or "draft"
    return "unknown", status


def parse_coordinator_plans(coordinator_path: Path) -> tuple[str, list[PlanRow]]:
    text = read_text(coordinator_path)
    meta = parse_frontmatter(text)
    intent = ""
    for line in extract_section(text, "Intent").splitlines():
        line = line.strip()
        if line:
            intent = line
            break
    plans: list[PlanRow] = []
    for line in extract_section(text, "Plans").splitlines():
        if not line.strip().startswith("|") or "---" in line:
            continue
        if re.match(r"^\|\s*Plan\s*\|", line):
            continue
        raw = line.strip().strip("|")
        placeholders: dict[str, str] = {}

        def link_replacer(m: re.Match[str]) -> str:
            key = f"__LINK_{len(placeholders)}__"
            name = (m.group(2) or Path(m.group(1)).parent.name).strip()
            placeholders[key] = name
            placeholders[f"{key}__WIKI"] = m.group(0)
            return key

        sanitized = WIKI_LINK_RE.sub(link_replacer, raw)
        cols = [c.strip() for c in sanitized.split("|")]
        if len(cols) < 3:
            continue
        plan_name = placeholders.get(cols[0], cols[0]).strip("`")
        notes = cols[2]
        for key, wiki in list(placeholders.items()):
            if key.endswith("__WIKI"):
                notes = notes.replace(key[: -len("__WIKI")], wiki)
        plans.append(
            PlanRow(
                name=plan_name,
                status=cols[1].strip("`"),
                notes=notes,
                path=str(coordinator_path.parent / "plans" / plan_name),
            )
        )
    return intent, plans


def history_entry_slug(path: Path) -> str:
    slug = path.stem
    if re.match(r"\d{4}-\d{2}-\d{2}-", slug):
        return slug[11:]
    return slug


HISTORY_SECTION_STATUS = {
    "In progress": "in-progress",
    "In review": "pr-open",
    "Done": "merged",
}
HISTORY_SECTION_RE = re.compile(
    r"^## (In progress|In review|Done)\s*$", re.MULTILINE
)
HISTORY_ITEM_RE = re.compile(
    r"^- \[\[([^\]|]+)(?:\|([^\]]+))?\]\](?:\s+—\s+(.+))?$"
)


def parse_yaml_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    data: dict[str, Any] = {}
    key: str | None = None
    for line in text[4:end].splitlines():
        if line.startswith("  - ") and key:
            item = line[4:].strip().strip('"').strip("'")
            bucket = data.get(key)
            if isinstance(bucket, list):
                bucket.append(item)
            continue
        if ":" not in line or line.startswith(" "):
            continue
        raw_key, _, raw_value = line.partition(":")
        key = raw_key.strip()
        value = raw_value.strip()
        if value == "[]" or value == "":
            data[key] = []
            if value == "[]":
                key = None
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key] = value
        key = None
    return data, text[end + 5 :]


def yaml_wiki_targets(value: Any) -> list[str]:
    values = value if isinstance(value, list) else [value]
    targets: list[str] = []
    for item in values:
        if not item:
            continue
        links = wiki_links(str(item))
        targets.extend(target for target, _ in links)
        if not links:
            targets.append(str(item).strip())
    return [target for target in targets if target]


def history_card_body(body: str) -> list[str]:
    paragraphs: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        text = " ".join(buffer).strip()
        buffer.clear()
        if text:
            paragraphs.append(text)

    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^(Touches|Modified|Created)\b", stripped):
            flush()
            continue
        if not stripped or stripped.startswith("#"):
            flush()
            continue
        buffer.append(stripped)
    flush()
    return paragraphs


def parse_history_index(bindify_root: Path, index: RefIndex) -> list[dict[str, Any]]:
    index_path = bindify_root / "history" / "index.md"
    if not index_path.exists():
        return []
    text = read_text(index_path)
    if HISTORY_SECTION_RE.search(text):
        return parse_status_history_index(text, index_path, bindify_root, index)
    return parse_legacy_history_index(text, index_path, bindify_root, index)


def parse_status_history_index(
    text: str, index_path: Path, bindify_root: Path, index: RefIndex
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    matches = list(HISTORY_SECTION_RE.finditer(text))
    for i, match in enumerate(matches):
        status = HISTORY_SECTION_STATUS[match.group(1)]
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        for line in text[match.end() : end].splitlines():
            item_match = HISTORY_ITEM_RE.match(line.strip())
            if not item_match:
                continue
            target, title, _tail = item_match.groups()
            entry_path = resolve_path(bindify_root, target, index_path)
            slug = history_entry_slug(entry_path) if entry_path else ""
            date = ""
            if entry_path and re.match(r"\d{4}-\d{2}-\d{2}-", entry_path.stem):
                date = entry_path.stem[:10]
            entry_ref_id = ""
            if entry_path and slug:
                entry_ref_id = f"history/{slug}"
                index.add(entry_path, entry_ref_id, route=f"#/history/{slug}")
            items.append({
                "date": date,
                "title": (title or target).strip(),
                "status": status,
                "summaries": [],
                "slug": slug,
                "entry_ref_id": entry_ref_id,
                "plan_ref_ids": [],
                "doc_ref_ids": [],
            })
    return items


def parse_legacy_history_index(
    text: str, index_path: Path, bindify_root: Path, index: RefIndex
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    matches = list(HISTORY_INDEX_RE.finditer(text))
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        summaries: list[str] = []
        status = ""
        entry_ref_id = ""
        plan_ref_ids: list[str] = []
        doc_ref_ids: list[str] = []
        for line in bullet_lines(block):
            if line.startswith("Status:"):
                status = line.split(":", 1)[1].strip().strip("`")
            elif line.startswith("Summary:"):
                summaries.append(line.split(":", 1)[1].strip())
            elif line.startswith("Entry:"):
                for target, _ in wiki_links(line):
                    entry_path = resolve_path(bindify_root, target, index_path)
                    if entry_path:
                        slug = history_entry_slug(entry_path)
                        entry_ref_id = f"history/{slug}"
                        index.add(entry_path, entry_ref_id, route=f"#/history/{slug}")
            elif line.startswith("Plans:"):
                for path_match in BACKTICK_PATH_RE.finditer(line):
                    ref = index.get_by_path(path_match.group(1), index_path)
                    if ref:
                        plan_ref_ids.append(ref.id)
            elif line.startswith("Features/Docs:"):
                for path_match in BACKTICK_PATH_RE.finditer(line):
                    ref = index.get_by_path(path_match.group(1), index_path)
                    if ref:
                        doc_ref_ids.append(ref.id)
        slug = entry_ref_id.replace("history/", "") if entry_ref_id else ""
        items.append({
            "date": match.group(1),
            "title": match.group(2).strip(),
            "status": status,
            "summaries": summaries,
            "slug": slug,
            "entry_ref_id": entry_ref_id,
            "plan_ref_ids": plan_ref_ids,
            "doc_ref_ids": doc_ref_ids,
        })
    return items


def parse_arch_impact_line(line: str, source: Path, index: RefIndex) -> dict[str, Any] | None:
    m = re.match(r"`(\w+)`\s*(.+)", line)
    if not m:
        return None
    action = m.group(1)
    rest = m.group(2)
    note = ""
    if " — " in rest:
        wiki_part, note = rest.split(" — ", 1)
    else:
        wiki_part = rest
    ref_id = ""
    for target, _ in wiki_links(wiki_part):
        ref = index.get_arch(target, source)
        if ref:
            ref_id = ref.id
    if not ref_id:
        return None
    return {"action": action, "ref_id": ref_id, "note": note.strip()}


def parse_history_card(path: Path, index: RefIndex, yaml: dict[str, Any], body: str) -> dict[str, Any]:
    slug = history_entry_slug(path)
    title = slug
    for line in body.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    paragraphs = history_card_body(body)
    arch_impacts: list[dict[str, Any]] = []
    for action in ("touches", "modified", "created"):
        for target in yaml_wiki_targets(yaml.get(action, [])):
            ref = index.get_arch(target, path)
            if ref:
                arch_impacts.append({"action": action, "ref_id": ref.id, "note": ""})

    plan_targets = yaml_wiki_targets(yaml.get("plan", ""))
    updates_targets = yaml_wiki_targets(yaml.get("updates", ""))
    plan_ref = index.get_by_path(plan_targets[0], path) if plan_targets else None
    updates_ref = index.get_by_path(updates_targets[0], path) if updates_targets else None

    pr_ref_id = ""
    pr_url = str(yaml.get("pr") or "")
    if pr_url.startswith("http"):
        pr_number = re.search(r"/pull/(\d+)", pr_url)
        pr_ref_id = f"external/pr-{slug}"
        index.add_external(pr_ref_id, f"#{pr_number.group(1)}" if pr_number else "PR", pr_url)

    return {
        "slug": slug,
        "title": title,
        "status": str(yaml.get("status") or ""),
        "date": str(yaml.get("date") or ""),
        "merge": str(yaml.get("merge") or ""),
        "body": paragraphs,
        "what_changed": paragraphs,
        "user_impact": [],
        "arch_impacts": arch_impacts,
        "evidence": [],
        "follow_ups": [],
        "related_ref_ids": [],
        "pr_ref_id": pr_ref_id,
        "plan_ref_id": plan_ref.id if plan_ref else "",
        "updates_ref_id": updates_ref.id if updates_ref else "",
        "path": str(path),
    }


def parse_history_entry(path: Path, index: RefIndex) -> dict[str, Any]:
    text = read_text(path)
    yaml, body = parse_yaml_frontmatter(text)
    if yaml.get("type") == "history":
        return parse_history_card(path, index, yaml, body)
    meta = parse_frontmatter(text)
    slug = history_entry_slug(path)
    h1 = text.splitlines()[0].lstrip("# ").strip() if text else slug
    title = h1.replace("History Summary — ", "").strip() if h1.startswith("History Summary") else h1

    what_changed = bullet_lines(extract_section(text, "What Changed"))
    user_impact = bullet_lines(extract_section(text, "User / Feature Impact"))
    follow_ups = bullet_lines(extract_section(text, "Follow-ups"))

    arch_impacts: list[dict[str, Any]] = []
    for line in bullet_lines(extract_section(text, "Architecture Impact")):
        item = parse_arch_impact_line(line, path, index)
        if item:
            arch_impacts.append(item)

    evidence: list[dict[str, Any]] = []
    evidence_section = extract_section(text, "Evidence")
    plan_name = plan_name_from_path(
        resolve_path(index.bindify_root, meta.get("Plan", meta.get("Primary Plan", "")), path)
        or path
    )
    for line in bullet_lines(evidence_section):
        step_m = re.match(
            r"Step updates:\s*`([^`#]+)(?:#([^`]+))?`\s*—\s*(.+)", line
        )
        if step_m:
            raw_path = step_m.group(1)
            anchor = step_m.group(2) or ""
            note = step_m.group(3).strip()
            step_id = ""
            if anchor:
                step_match = re.search(r"step-(\d+)", anchor, re.I)
                if step_match:
                    step_id = step_match.group(1)
            updates_path = resolve_path(index.bindify_root, raw_path, path)
            if updates_path and step_id:
                for entry in parse_updates_full(updates_path, plan_name, index):
                    if entry.step_id == step_id:
                        ref = index.get_step(plan_name, step_id, entry.title)
                        evidence.append({"ref_id": ref.id, "note": note})
                        break
            continue
        plain_m = re.match(r"(\w+):\s*`([^`]+)`\s*(?:—\s*(.+))?$", line)
        if plain_m:
            ref = index.get_by_path(plain_m.group(2), path)
            if ref:
                evidence.append({
                    "ref_id": ref.id,
                    "note": (plain_m.group(3) or "").strip(),
                })

    related: list[str] = []
    for line in bullet_lines(extract_section(text, "Related Features and Docs")):
        for path_match in BACKTICK_PATH_RE.finditer(line):
            ref = index.get_by_path(path_match.group(1), path)
            if ref:
                related.append(ref.id)

    pr_ref_id = ""
    pr_field = meta.get("PR", "")
    pr_link = MD_LINK_RE.search(pr_field)
    if pr_link:
        pr_ref_id = f"external/pr-{slug}"
        index.add_external(pr_ref_id, pr_link.group(1), pr_link.group(2))

    plan_ref = index.get_by_path(meta.get("Plan", meta.get("Primary Plan", "")), path)
    updates_ref = index.get_by_path(meta.get("Updates Log", ""), path)

    return {
        "slug": slug,
        "title": title,
        "status": meta.get("Status", ""),
        "date": meta.get("Date", ""),
        "merge": meta.get("Merge", ""),
        "what_changed": what_changed,
        "user_impact": user_impact,
        "arch_impacts": arch_impacts,
        "evidence": evidence,
        "body": [],
        "follow_ups": follow_ups,
        "related_ref_ids": related,
        "pr_ref_id": pr_ref_id,
        "plan_ref_id": plan_ref.id if plan_ref else "",
        "updates_ref_id": updates_ref.id if updates_ref else "",
        "path": str(path),
    }


def parse_architecture(bindify_root: Path, index: RefIndex) -> tuple[list[dict], list[dict], list[dict]]:
    arch_root = bindify_root / "architecture"
    nodes: list[dict] = []
    edges: list[dict] = []
    layers: list[dict] = []

    map_path = arch_root / "_map.md"
    if map_path.exists():
        layers_section = extract_section(read_text(map_path), "Layers")
        for line in layers_section.splitlines():
            line = line.strip()
            if line.startswith("- **"):
                layer_match = re.match(r"- \*\*([^*]+)\*\* — (.+)", line)
                if layer_match:
                    layer_name = layer_match.group(1)
                    for target, _ in wiki_links(layer_match.group(2)):
                        ref = index.get_arch(target, map_path)
                        if ref:
                            layers.append({"layer": layer_name, "ref_id": ref.id})

    relation_sections = {
        "Depends on": "depends-on",
        "Used by": "used-by",
        "Standards & patterns": "follows",
    }

    for path in sorted(arch_root.rglob("*.md")):
        if path.name == "_map.md":
            continue
        text = read_text(path)
        meta = parse_frontmatter(text)
        node_id = normalize_arch_id(path, bindify_root)
        ref_id = f"arch/{node_id}"
        index.add(path, ref_id)

        responsibility = extract_section(text, "Responsibility")
        change_log = bullet_lines(extract_section(text, "Change log"))
        recent_changes = list(reversed(change_log))[:6]

        nodes.append({
            "id": node_id,
            "ref_id": ref_id,
            "type": meta.get("type", "unknown"),
            "status": meta.get("status", ""),
            "layer": meta.get("layer", ""),
            "responsibility": markdown_blocks(responsibility, path, index),
            "change_log_count": len(change_log),
            "change_log": [rich_segments(line, path, index) for line in recent_changes],
        })

        for section, relation in relation_sections.items():
            for target, _ in wiki_links(extract_section(text, section)):
                resolved = resolve_path(bindify_root, target, path)
                if resolved:
                    target_id = normalize_arch_id(resolved, bindify_root)
                    edges.append({"source": node_id, "target": target_id, "relation": relation})

    return nodes, edges, layers


def file_view(path: Path, bindify_root: Path, index: RefIndex) -> dict[str, Any]:
    text = read_text(path)
    title = text.splitlines()[0].lstrip("# ").strip() if text else path.name
    sections: list[dict[str, Any]] = []
    for heading in ("Intent", "What Changed", "User / Feature Impact", "Approach", "Responsibility"):
        body = extract_section(text, heading)
        if body:
            sections.append({
                "heading": heading,
                "bullets": [rich_segments(line, path, index) for line in bullet_lines(body)[:8]],
            })
    if not sections:
        sections.append({
            "heading": "Preview",
            "bullets": [rich_segments(line, path, index) for line in bullet_lines(text)[:6]],
        })
    return {"title": title, "path": str(path), "sections": sections}


def scan_bindify(bindify_root: Path) -> dict[str, Any]:
    bindify_root = bindify_root.resolve()
    index = RefIndex(bindify_root)
    index.build_from_tree()

    timeline = parse_history_index(bindify_root, index)
    history_entries: dict[str, dict] = {}
    covered_plans: set[str] = set()

    entries_dir = bindify_root / "history" / "entries"
    if entries_dir.exists():
        for entry_path in sorted(entries_dir.glob("*.md")):
            entry = parse_history_entry(entry_path, index)
            history_entries[entry["slug"]] = entry
            for item in timeline:
                if item.get("slug") == entry["slug"] and not item.get("summaries"):
                    item["summaries"] = entry.get("body") or []
            plan_ref = index.refs.get(entry.get("plan_ref_id", ""))
            if plan_ref and plan_ref.path:
                covered_plans.add(plan_name_from_path(Path(plan_ref.path)))

    coordinator_path = bindify_root / "development" / "features" / "learning-core" / "coordinator.md"
    intent, all_plans = parse_coordinator_plans(coordinator_path) if coordinator_path.exists() else ("", [])

    active_work: list[dict[str, Any]] = []
    plan_views: dict[str, dict] = {}
    step_views: dict[str, dict] = {}

    features_dir = bindify_root / "development" / "features"
    if features_dir.exists():
        for coordinator in sorted(features_dir.glob("*/coordinator.md")):
            _, plans = parse_coordinator_plans(coordinator)
            for plan_row in plans:
                plan_dir = Path(plan_row.path)
                plan_name = plan_row.name
                phase, phase_status = detect_phase(plan_dir)
                planned = parse_plan_steps(plan_dir / "plan.md")
                logged = parse_updates_full(plan_dir / "updates.md", plan_name, index)
                logged_ids = {s.step_id for s in logged}

                if plan_name not in covered_plans:
                    plan_ref = index.get_by_path(
                        f"development/features/{coordinator.parent.name}/plans/{plan_name}/brief.md"
                    ) or index.refs.get(f"plan-artifact/{plan_name}/brief")
                    active_work.append({
                        "name": plan_name,
                        "status": plan_row.status,
                        "phase": phase,
                        "notes": rich_segments(plan_row.notes[:240], coordinator, index),
                        "plan_ref_id": plan_ref.id if plan_ref else f"plan-artifact/{plan_name}/brief",
                    })

                plan_views[plan_name] = {
                    "name": plan_name,
                    "phase": phase,
                    "status": phase_status or plan_row.status,
                    "verify_status": parse_frontmatter(read_text(plan_dir / "verify.md")).get("Status", "")
                    if (plan_dir / "verify.md").exists() else "",
                    "steps": [
                        {
                            "id": s["id"],
                            "title": s["title"],
                            "logged": s["id"] in logged_ids,
                            "step_ref_id": f"step/{plan_name}/{s['id']}",
                        }
                        for s in planned
                    ],
                }
                for step in logged:
                    key = f"{plan_name}/{step.step_id}"
                    step_views[key] = asdict(step)

    arch_nodes, arch_edges, arch_layers = parse_architecture(bindify_root, index)

    arch_views = {
        n["id"]: {
            "id": n["id"],
            "ref_id": n["ref_id"],
            "type": n["type"],
            "status": n["status"],
            "layer": n["layer"],
            "responsibility": n["responsibility"],
            "change_log": n["change_log"],
        }
        for n in arch_nodes
    }

    file_views: dict[str, dict] = {}
    for ref_id, ref_obj in index.refs.items():
        if ref_obj.kind in ("coordinator", "doc") and ref_obj.path:
            key = rel_to_bindify(Path(ref_obj.path), bindify_root).replace("/", "--")
            file_views[key] = file_view(Path(ref_obj.path), bindify_root, index)

    return {
        "bindify_root": str(bindify_root),
        "intent": intent,
        "timeline": timeline,
        "history_entries": history_entries,
        "active_work": active_work,
        "refs": {rid: asdict(r) for rid, r in index.refs.items()},
        "views": {
            "plans": plan_views,
            "steps": step_views,
            "arch": arch_views,
            "files": file_views,
        },
        "architecture": {
            "nodes": arch_nodes,
            "edges": arch_edges,
            "layers": arch_layers,
        },
    }
