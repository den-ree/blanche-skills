# Command: log-pr

Read a pull request — the unit of change — and write an architecture-aware log: what the PR did, what it
affects elsewhere, which architecture objects it moves, and how well it aligns with the project's standards and
patterns. This happens alongside the root history layer, where `generate-history-summary` produces the concise
human/UI digest and `log-pr` records the detailed PR-alignment evidence. It is followed by `publish-bindify-pr`.

`log-pr` does not change product code. It reads a PR that already exists and produces bindify artifacts.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `PR` | yes | PR number or URL |
| `BASE` | no | Base branch for diff fallback (default: repo default branch) |
| `STEPS_FILE` | no | Repo-relative path to the iterate-mode steps file attached to / referenced by the PR |
| `CATEGORY` | no | `features` \| `fixes` \| `refactor` \| `chore` — infer from PR if omitted |
| `FEATURE_NAME` | no | Feature folder the PR belongs to — infer from branch/labels/linked plan if omitted |
| `PLAN_NAME` | no | Plan folder the PR implements, if any |

---

## Ingestion — use the richest source available, fall back in order

1. **gh CLI / GitHub API (preferred).** Pull PR metadata, file set, and diff:
   ```bash
   gh pr view <PR> --json title,body,author,commits,files,baseRefName,headRefName,labels,url
   gh pr diff <PR>
   ```
   Captures discussion, intent, and the authoritative file/diff set.
2. **iterate-mode steps file.** If `STEPS_FILE` is given (the final iteration document the executor attached to
   the PR), read it as the authoritative record of *what was intended* step by step.
3. **git diff vs base (offline fallback).** If gh is unavailable:
   ```bash
   git diff <BASE>...<head-branch> --stat
   git diff <BASE>...<head-branch>
   ```

Prefer 1 for metadata + alignment, 2 for intent, 3 only when 1 is impossible. State in the log which sources
were used.

---

## Procedure

1. **Resolve placement.** Determine `CATEGORY` / `FEATURE_NAME` / `PLAN_NAME` from PR labels, branch name, or a
   linked plan. If a plan exists, the log appends to that plan's `updates.md`; if the PR is a standalone fix,
   route it to `development/fixes/<feature>/hotfixes.md` instead.
2. **Read the architecture skeleton.** Load `.bindify/architecture/_map.md` and the objects the diff plausibly
   touches, so impact and alignment are grounded in real objects.
3. **Summarize the change** in the impact-aware `updates.md` format from `summarize-work-for-updates`:
   - Summary, File Changes, Key Components.
   - **Impact & Connections** — abstract ripple effects, not a file list.
   - **Architecture** — `[[wiki-links]]` to objects, tagged `created` / `modified` / `touches`.
4. **Write the Alignment assessment** (a section unique to PR logs — see format below): which
   `standard` / `pattern` objects the PR follows, where it deviates, and a qualitative rating.
5. **Update the architecture graph.** Invoke `scan-architecture` in `fill` mode with this PR's changes as
   `SOURCE_REFS`, so missing objects are created and changed objects get change-log lines + edges.
6. **Refresh links.** Run `update-links` for the affected folder.
7. **Check root history state.** If a PR exists and no root history summary has been created yet, suggest or run
   `generate-history-summary` in `pr-open` mode so the outcome appears in `.bindify/history/`.
8. **Hand off.** Report the log path and the affected architecture objects; suggest `publish-bindify-pr` to open
   the PR against the `.bindify` submodule.

---

## Alignment assessment format

Append this block inside the PR's `updates.md` entry, after **Architecture**:

```markdown
### Alignment
- **Follows:** [[architecture/standards/<pattern>]] — how the PR conforms
- **Deviates:** [[architecture/standards/<pattern>]] — where and why it diverges (or "none")
- **New convention:** <any pattern the PR introduces that should become a `standard` object> (or "none")
- **Rating:** `aligned` | `mostly aligned` | `diverges` — one-line justification
```

Base the rating on evidence from the diff and the standard/pattern objects, not vibes. If the codebase has no
`standard`/`pattern` objects yet, note that and recommend a `scan-architecture bootstrap` first.

---

## Hard rules

- **Read-only on product code.** Never push code or edit the product source from this command.
- **`updates.md` / `hotfixes.md` are append-only.** Add one PR entry; never rewrite history.
- **Ground alignment in objects**, not opinion — cite the `standard`/`pattern` object you measured against.
- **Repo-relative paths only.** No absolute paths in markdown.
- If feature/plan placement is ambiguous, stop and ask before writing.

---

## Acceptance criteria

- A single impact-aware entry is appended for the PR, including non-empty Impact & Connections, Architecture,
  and Alignment sections.
- `scan-architecture fill` has run; objects the PR touched exist and carry a change-log line citing the PR.
- The log states which ingestion sources were used.

---

## Related

- `[[references/commands/summarize-work-for-updates.md]]`
- `[[references/commands/generate-history-summary.md]]`
- `[[references/commands/scan-architecture.md]]`
- `[[references/commands/publish-bindify-pr.md]]`
- `[[references/commands/log-hotfix.md]]`
