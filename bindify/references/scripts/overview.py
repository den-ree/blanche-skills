#!/usr/bin/env python3
"""Generate a history-first Bindify CTO dashboard."""

from __future__ import annotations

import argparse
import json
import webbrowser
from pathlib import Path
from typing import Any

from bindify_parse import scan_bindify


def render_html(data: dict[str, Any]) -> str:
    payload = json.dumps(data)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bindify Overview</title>
<style>
:root {{
  --bg: #f4f5f7;
  --card: #fff;
  --text: #1a1d23;
  --muted: #5c6570;
  --border: #e2e6ea;
  --accent: #2563eb;
  --merged: #166534;
  --proposed: #a16207;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.55; }}
header {{
  position: sticky; top: 0; z-index: 10;
  background: var(--card); border-bottom: 1px solid var(--border);
  padding: .9rem 1.25rem;
}}
header h1 {{ margin: 0; font-size: 1.15rem; }}
.breadcrumb {{ margin: .2rem 0 0; font-size: .85rem; color: var(--muted); }}
.breadcrumb a {{ color: var(--accent); text-decoration: none; }}
.breadcrumb a:hover {{ text-decoration: underline; }}
main {{ max-width: 1280px; margin: 0 auto; padding: 1.25rem 1.25rem 3rem; }}
.intent {{ margin: 0 0 .9rem; color: var(--muted); font-size: .9rem; }}
section {{
  background: #f8fafc; border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1rem .9rem; margin-bottom: 1rem;
}}
section h2 {{ margin: 0; font-size: 1.12rem; font-weight: 650; border: none; padding: 0; }}
.page-head {{
  margin-bottom: .9rem; padding-bottom: .75rem; border-bottom: 1px dashed #dbe3ea;
}}
.kind-line, .board-card .kind, .history-card .kind {{
  display: block; margin-top: .15rem; font-size: .68rem; font-weight: 700;
  letter-spacing: .07em; text-transform: uppercase; color: #64748b;
}}
.kind-line {{ margin: .28rem 0 0; }}
section h3 {{
  margin: 1rem 0 .55rem; padding-top: .75rem; border-top: 1px dashed #dbe3ea;
  font-size: .68rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; color: #64748b;
}}
.home-band {{ margin-top: .85rem; padding-top: .85rem; border-top: 1px dashed #dbe3ea; }}
.home-band:first-child {{ margin-top: 0; padding-top: 0; border-top: none; }}
.home-band > .layer-label {{ padding-top: 0; margin-bottom: .55rem; }}
.stack {{ display: flex; flex-direction: column; gap: .5rem; }}
.muted {{ color: var(--muted); font-size: .85rem; }}
.badge {{
  display: inline-block; padding: .12rem .5rem; border-radius: 999px;
  font-size: .7rem; font-weight: 600; text-transform: uppercase;
}}
.badge-merged {{ background: #dcfce7; color: var(--merged); }}
.badge-in-progress {{ background: #ffedd5; color: #c2410c; }}
.badge-pr-open {{ background: #dbeafe; color: #1d4ed8; }}
.badge-proposed {{ background: #fef3c7; color: var(--proposed); }}
.badge-done {{ background: #dcfce7; color: var(--merged); }}
.badge-default {{ background: #f3f4f6; color: #6b7280; }}
.board-card, .history-card, .active-card, .change-step {{
  background: #fff; border: 1px solid #d5dee7; border-radius: 10px;
  padding: .65rem .75rem .55rem; box-shadow: 0 1px 2px rgba(16,24,40,.05); text-align: left;
}}
.history-card, button.board-card {{ font: inherit; color: inherit; width: 100%; cursor: pointer; }}
button.board-card:hover {{
  border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.14);
}}
.history-card:hover, .history-card.selected {{
  border-color: #059669; box-shadow: 0 0 0 3px rgba(5,150,105,.16);
}}
.board-card.is-missing {{ opacity: .62; cursor: default; }}
.history-card h3, .board-card .name, .active-title {{
  display: block; margin: .15rem 0 .3rem; font-size: .92rem; font-weight: 650;
  line-height: 1.35; letter-spacing: 0; text-transform: none; color: var(--text); border: none; padding: 0;
}}
.card-meta {{ display: flex; gap: .5rem; align-items: center; flex-wrap: wrap; }}
ul.compact {{ margin: .35rem 0; padding-left: 1.15rem; }}
ul.compact li {{ margin: .2rem 0; font-size: .9rem; }}
.ref-chip {{
  display: inline-block; padding: .28rem .6rem; margin: .15rem .3rem .15rem 0;
  border-radius: 8px; font-size: .78rem; font-weight: 600; text-decoration: none;
  background: #fff; color: #1e293b; border: 1px solid #d5dee7;
  box-shadow: 0 1px 2px rgba(16,24,40,.04);
}}
.ref-chip:hover {{
  text-decoration: none; border-color: #94a3b8; box-shadow: 0 0 0 3px rgba(148,163,184,.2);
}}
.ref-arch:hover {{ border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.14); }}
.ref-history:hover {{ border-color: #059669; box-shadow: 0 0 0 3px rgba(5,150,105,.16); }}
.chip-row {{ margin: .35rem 0; }}
.arch-impact {{ margin: .4rem 0; font-size: .85rem; }}
.arch-impact .note {{ color: var(--muted); }}
.active-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: .75rem; }}
.active-note {{ margin: .35rem 0 .15rem; }}
.detail-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: .75rem; flex-wrap: wrap; }}
.open-editor {{ font-size: .78rem; color: var(--muted); }}
details {{ margin: .85rem 0 0; padding-top: .7rem; border-top: 1px dashed #dbe3ea; }}
details summary {{
  cursor: pointer; font-size: .68rem; font-weight: 700; letter-spacing: .07em;
  text-transform: uppercase; color: #64748b;
}}
details ul.compact {{ list-style: none; padding-left: 0; }}
details ul.compact li {{
  background: #fff; border: 1px solid #d5dee7; border-radius: 8px;
  padding: .4rem .6rem; margin: .35rem 0; box-shadow: 0 1px 2px rgba(16,24,40,.04);
}}
#graph {{ width: 100%; height: 280px; border: 1px solid var(--border); border-radius: 8px; background: #fafbfc; }}
.file-changes {{ font-size: .82rem; color: var(--muted); }}
code, .path-chip {{
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .78em; background: #f3f4f6; padding: .05rem .28rem; border-radius: 4px;
}}
.path-chip {{
  font: inherit; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .78em; border: 1px solid transparent; cursor: pointer; color: inherit;
}}
.path-chip:hover {{ border-color: #93c5fd; background: #eff6ff; }}
.path-chip.copied {{ background: #dcfce7; border-color: #86efac; }}
.prose p {{ margin: .45rem 0; }}
.prose ul.compact {{ margin: .2rem 0 .7rem; }}
.prose strong {{ font-weight: 650; }}
.arch-diagram, .arch-nested {{ position: relative; }}
.arch-diagram {{
  background: #f8fafc; border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1rem .85rem;
}}
.arch-arrows {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible; }}
.arch-system {{ display: flex; justify-content: center; position: relative; z-index: 1; }}
.layer-band {{
  display: grid; grid-template-columns: 108px 1fr; gap: .65rem; align-items: start;
  margin-top: .7rem; padding-top: .7rem; border-top: 1px dashed #dbe3ea;
  position: relative; z-index: 1;
}}
.layer-label {{
  font-size: .68rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
  color: #64748b; padding-top: .65rem;
}}
.layer-nodes, .standards-nodes {{ display: flex; flex-wrap: wrap; gap: .5rem; }}
.arch-card {{
  font: inherit; color: inherit; appearance: none;
  background: #fff; border: 1px solid #d5dee7; border-radius: 10px;
  padding: .5rem .7rem .45rem; min-width: 132px; max-width: 210px; cursor: pointer;
  box-shadow: 0 1px 2px rgba(16,24,40,.05); text-align: left;
}}
.arch-card:hover, .arch-card.hot, .arch-card.link,
.arch-card.modified, .arch-card.created, .arch-card.touches {{
  border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.14);
}}
.arch-card.dim {{ opacity: .35; }}
.impact-tag {{
  display: inline-block; margin-top: .28rem; font-size: .62rem; font-weight: 700;
  letter-spacing: .06em; text-transform: uppercase; color: #1d4ed8;
}}
.split-board {{
  position: relative; display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(300px, .78fr);
  background: #f8fafc; border: 1px solid var(--border); border-radius: 12px;
}}
.split-arch, .split-history {{ position: relative; z-index: 1; padding: 1rem; }}
.split-arch {{ border-right: 1px dashed #dbe3ea; }}
.split-label {{ padding-top: 0; margin: 0 0 .55rem; }}
.tone-arch {{ color: #2563eb; }}
.tone-history {{ color: #059669; }}
.tone-active {{ color: #c2410c; }}
.layer-label.tone-arch::before, .layer-label.tone-history::before, .layer-label.tone-active::before {{
  content: ""; display: inline-block; width: .45rem; height: .45rem; margin-right: .4rem;
  border: 2px solid currentColor; border-radius: 2px; vertical-align: 1px;
}}
.active-card {{ cursor: pointer; width: 100%; }}
.active-card:hover, .active-card.selected {{
  border-color: #c2410c; box-shadow: 0 0 0 3px rgba(194,65,12,.16);
}}
.history-card.linked {{ border-color: #059669; box-shadow: 0 0 0 3px rgba(5,150,105,.16); }}
.history-card.dim {{ opacity: .4; }}
.split-board > .history-links {{ z-index: 0; }}
@media (max-width: 900px) {{
  .split-board {{ grid-template-columns: 1fr; }}
  .split-arch {{ border-right: none; border-bottom: 1px dashed #dbe3ea; }}
}}
.arch-card .name {{ display: block; font-weight: 650; font-size: .86rem; line-height: 1.3; }}
.arch-card .kind {{ display: block; margin-top: .15rem; font-size: .68rem; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
.arch-card.system {{ min-width: 220px; border-color: #c7d2fe; background: #eef2ff; }}
.standards-row {{ margin-top: .85rem; position: relative; z-index: 1; }}
.inline-ref {{ display: inline-flex; vertical-align: middle; margin: .1rem .15rem; }}
.change-group {{ margin: .35rem 0 .8rem; }}
.change-steps {{ display: flex; flex-direction: column; gap: .45rem; margin-top: .45rem; }}
.change-step {{
  display: grid; grid-template-columns: auto 1fr; gap: .6rem; align-items: start;
}}
.change-step.note {{ grid-template-columns: 1fr; }}
.step-pill {{
  font: inherit; font-size: .68rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  color: #1e3a8a; background: #fff; border: 1px solid #d5dee7;
  border-radius: 999px; padding: .28rem .55rem; white-space: nowrap;
  box-shadow: inset 3px 0 0 #2563eb, 0 1px 2px rgba(16,24,40,.04);
}}
button.step-pill {{ cursor: pointer; }}
button.step-pill:hover {{ border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.14); }}
.step-copy {{ font-size: .9rem; line-height: 1.45; padding-top: .12rem; }}
.uml {{
  background: #fff; border: 1px solid #d5dee7; border-radius: 10px;
  padding: .85rem 1rem .7rem; overflow-x: auto;
  box-shadow: 0 1px 2px rgba(16,24,40,.05);
}}
.uml-caption {{
  font-size: .68rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  color: #64748b; margin: .35rem 0 .25rem;
}}
.uml-row {{ display: flex; align-items: center; gap: .35rem; margin: .4rem 0; flex-wrap: nowrap; }}
.uml-box {{
  background: #fff; border: 1.5px solid #1e293b; border-radius: 2px;
  min-width: 128px; max-width: 240px; box-shadow: 2px 2px 0 rgba(15,23,42,.05);
}}
button.uml-box {{ font: inherit; color: inherit; cursor: pointer; text-align: left; padding: 0; }}
button.uml-box:hover {{ border-color: #2563eb; }}
.uml-box .stereo {{
  font-size: .65rem; font-style: italic; color: #64748b; text-align: center;
  padding: .22rem .45rem 0;
}}
.uml-box .uname {{
  font-size: .8rem; font-weight: 650; text-align: center;
  padding: .28rem .55rem .4rem;
}}
.uml-box .stereo + .uname {{ border-top: 1px solid #e2e8f0; margin: .18rem .35rem 0; }}
.uml-edge {{ display: flex; align-items: center; gap: .15rem; min-width: 84px; color: #1e293b; }}
.uml-line {{ flex: 1; border-top: 1.5px solid #1e293b; min-width: 22px; }}
.uml-label {{ font-size: .65rem; font-style: italic; color: #475569; white-space: nowrap; }}
.uml-head {{
  width: 0; height: 0; border-top: 5px solid transparent; border-bottom: 5px solid transparent;
  border-left: 8px solid #1e293b;
}}
.uml-link {{
  display: grid; grid-template-columns: 92px 40px minmax(180px, 320px);
  align-items: start; gap: .15rem .4rem; margin: .55rem 0;
}}
.uml-action {{
  padding-top: .55rem; text-align: right; font-size: .68rem; font-weight: 700;
  letter-spacing: .06em; text-transform: uppercase; color: #64748b;
}}
.uml-pointer {{ min-width: 0; width: 40px; padding-top: .85rem; }}
.uml-pointer .uml-line {{ min-width: 0; }}
.uml-note {{ display: block; font-size: .72rem; color: var(--muted); font-weight: 450; margin-top: .15rem; }}
</style>
</head>
<body>
<header>
  <h1>Bindify Overview</h1>
  <nav class="breadcrumb" id="breadcrumb"></nav>
</header>
<main id="app"></main>
<script>
const DATA = {payload};

function el(tag, attrs, children) {{
  attrs = attrs || {{}};
  children = children || [];
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {{
    if (k === "className") node.className = v;
    else if (k === "textContent") node.textContent = v;
    else if (k === "innerHTML") node.innerHTML = v;
    else if (k === "onclick") node.onclick = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2).toLowerCase(), v);
    else node.setAttribute(k, v);
  }}
  for (const c of [].concat(children)) {{
    if (c == null) continue;
    node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  }}
  return node;
}}

function ref(refId) {{
  const r = DATA.refs[refId];
  if (!r) return el("span", {{ className: "muted", textContent: refId }});
  const cls = "ref-chip ref-" + (r.kind === "external" ? "external" : r.kind);
  if (r.external) {{
    return el("a", {{ className: cls, href: r.route, target: "_blank", rel: "noopener",
      textContent: r.label }});
  }}
  const a = el("a", {{ className: cls, href: r.route, textContent: r.label }});
  a.onclick = e => {{ e.preventDefault(); navigate(r.route); }};
  return a;
}}

function badge(status) {{
  const cls = {{
    merged: "badge-merged", "in-progress": "badge-in-progress", "pr-open": "badge-pr-open",
    proposed: "badge-proposed", done: "badge-done", passed: "badge-done",
  }}[status] || "badge-default";
  return el("span", {{ className: "badge " + cls, textContent: status }});
}}

function isFilePath(text) {{
  return /[/\\\\]/.test(text) || /\\.[a-z0-9]{{1,6}}$/i.test(text);
}}

function copyText(text, node) {{
  const done = () => {{
    if (!node) return;
    node.classList.add("copied");
    const previous = node.textContent;
    node.dataset.label = node.dataset.label || previous;
    node.textContent = "Copied";
    setTimeout(() => {{
      node.classList.remove("copied");
      node.textContent = node.dataset.label;
    }}, 900);
  }};
  const fallback = () => {{
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.select();
    try {{ document.execCommand("copy"); done(); }} catch (err) {{}}
    area.remove();
  }};
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(text).then(done).catch(fallback);
  }} else {{
    fallback();
  }}
}}

function appendFormatted(parent, text) {{
  const pattern = /\\*\\*([^*]+)\\*\\*/g;
  let last = 0;
  let match;
  while ((match = pattern.exec(text))) {{
    if (match.index > last) parent.appendChild(document.createTextNode(text.slice(last, match.index)));
    parent.appendChild(el("strong", {{ textContent: match[1] }}));
    last = match.index + match[0].length;
  }}
  if (last < text.length) parent.appendChild(document.createTextNode(text.slice(last)));
}}

function pathChip(text) {{
  const chip = el("button", {{
    className: "path-chip", type: "button", textContent: text, title: "Copy " + text,
  }});
  chip.onclick = event => {{
    event.preventDefault();
    event.stopPropagation();
    copyText(text, chip);
  }};
  return chip;
}}

function renderInline(parent, segments) {{
  if (!segments) return;
  const list = Array.isArray(segments) ? segments : [{{ type: "text", text: String(segments) }}];
  for (const seg of list) {{
    if (!seg) continue;
    if (seg.type === "ref") {{
      const wrap = el("span", {{ className: "inline-ref" }});
      wrap.appendChild(ref(seg.ref_id));
      wrap.onclick = e => e.stopPropagation();
      parent.appendChild(wrap);
    }} else if (seg.type === "code") {{
      parent.appendChild(isFilePath(seg.text) ? pathChip(seg.text) : el("code", {{ textContent: seg.text }}));
    }} else if (seg.text) {{
      appendFormatted(parent, seg.text);
    }}
  }}
}}

function renderBlocks(parent, blocks) {{
  if (!blocks) return;
  if (!Array.isArray(blocks) || !blocks.length || !blocks[0] || !blocks[0].type) {{
    const paragraph = el("p");
    renderInline(paragraph, blocks);
    parent.appendChild(paragraph);
    return;
  }}
  for (const block of blocks) {{
    if (block.type === "ul") {{
      const list = richBullets(block.items);
      if (list) parent.appendChild(list);
    }} else {{
      const paragraph = el("p");
      renderInline(paragraph, block.segments);
      parent.appendChild(paragraph);
    }}
  }}
}}

function richBullets(items) {{
  if (!items || !items.length) return null;
  return el("ul", {{ className: "compact" }}, items.map(item => {{
    const li = el("li");
    if (typeof item === "string") li.textContent = item;
    else renderInline(li, item);
    return li;
  }}));
}}

function bullets(items) {{
  return richBullets(items);
}}

function setBreadcrumb(parts) {{
  const nav = document.getElementById("breadcrumb");
  nav.innerHTML = "";
  parts.forEach((p, i) => {{
    if (i) nav.appendChild(document.createTextNode(" › "));
    if (p.href) {{
      const a = el("a", {{ href: p.href, textContent: p.label }});
      a.onclick = e => {{ e.preventDefault(); navigate(p.href); }};
      nav.appendChild(a);
    }} else {{
      nav.appendChild(el("span", {{ textContent: p.label }}));
    }}
  }});
}}

function navigate(hash) {{
  if (!hash || hash === "#") {{ location.hash = "#/"; return; }}
  if (!hash.startsWith("#")) hash = "#" + hash;
  location.hash = hash;
}}

function parseRoute() {{
  const h = location.hash.replace(/^#/, "") || "/";
  const parts = h.split("/").filter(Boolean);
  return {{ parts }};
}}

function tidyNote(text) {{
  let sentence = text.replace(/\\s*;\\s*/g, ". ").replace(/\\s+/g, " ").trim();
  sentence = sentence.replace(/\\.\\s+([a-z])/g, (_, ch) => ". " + ch.toUpperCase());
  if (sentence && !/[.!?]$/.test(sentence)) sentence += ".";
  return sentence;
}}

function activeTitle(item) {{
  const planRef = DATA.refs[item.plan_ref_id];
  return planRef && planRef.label
    ? planRef.label.replace(/^(Brief|Plan|Proposal|Updates|Verify) · /, "")
    : (item.name || "").replace(/-/g, " ");
}}

function renderActiveWork(item, selected) {{
  const card = el("div", {{ className: "active-card" + (selected ? " selected" : "") }});
  card.dataset.active = item.name || "";
  const head = el("div", {{ className: "active-head" }});
  head.appendChild(el("div", {{ className: "active-title", textContent: activeTitle(item) }}));
  const badges = el("div", {{ className: "card-meta" }});
  if (item.status) badges.appendChild(badge(item.status));
  if (item.phase && item.phase !== item.status) badges.appendChild(badge(item.phase));
  head.appendChild(badges);
  card.appendChild(head);

  const notes = Array.isArray(item.notes) ? item.notes : [];
  const linked = notes.filter(seg => seg.type === "ref");
  const sentence = tidyNote(notes.filter(seg => seg.type !== "ref").map(seg => seg.text || "").join(" "));
  if (sentence) card.appendChild(el("p", {{ className: "muted active-note", textContent: sentence }}));

  const chips = el("div", {{ className: "chip-row" }});
  if (item.plan_ref_id) chips.appendChild(ref(item.plan_ref_id));
  linked.forEach(seg => chips.appendChild(ref(seg.ref_id)));
  if (chips.childNodes.length) card.appendChild(chips);
  card.onclick = event => {{
    if (event.target.closest("a, button")) return;
    const current = (location.hash.match(/^#\\/active\\/([^/]+)/) || [])[1];
    navigate(current === item.name ? "#/" : "#/active/" + item.name);
  }};
  return card;
}}

function homeBand(label, content, tone) {{
  const band = el("div", {{ className: "home-band" }});
  band.appendChild(el("div", {{
    className: "layer-label" + (tone ? " " + tone : ""), textContent: label,
  }}));
  band.appendChild(content);
  return band;
}}

function historyCard(item, selected) {{
  const card = el("div", {{ className: "history-card" + (selected ? " selected" : "") }});
  card.dataset.slug = item.slug;
  const meta = el("div", {{ className: "card-meta" }});
  meta.appendChild(el("span", {{ className: "kind", textContent: item.date }}));
  if (item.status) meta.appendChild(badge(item.status));
  card.appendChild(meta);
  card.appendChild(el("h3", {{ textContent: item.title }}));
  if (selected) {{
    const entry = DATA.history_entries[item.slug];
    const paragraphs = entry && entry.body && entry.body.length ? entry.body : [];
    if (paragraphs.length) paragraphs.forEach(text => card.appendChild(el("p", {{ textContent: text }})));
    else card.appendChild(bullets(item.summaries));
    const chips = el("div", {{ className: "chip-row" }});
    if (entry && entry.plan_ref_id) chips.appendChild(ref(entry.plan_ref_id));
    if (entry && entry.updates_ref_id) chips.appendChild(ref(entry.updates_ref_id));
    if (entry && entry.pr_ref_id) chips.appendChild(ref(entry.pr_ref_id));
    if (chips.childNodes.length) card.appendChild(chips);
  }}
  card.onclick = event => {{
    if (event.target.closest("a, button")) return;
    const current = (location.hash.match(/^#\\/history\\/([^/]+)/) || [])[1];
    navigate(current === item.slug ? "#/" : "#/history/" + item.slug);
  }};
  return card;
}}

function renderBoard(root, slug, activeName) {{
  slug = slug || "";
  activeName = activeName || "";
  const entry = slug ? DATA.history_entries[slug] : null;
  if (slug && !entry) {{ renderNotFound(root); return; }}
  const activeItem = activeName
    ? (DATA.active_work || []).find(item => item.name === activeName)
    : null;
  if (activeName && !activeItem) {{ renderNotFound(root); return; }}
  if (entry) setBreadcrumb([{{ label: "Timeline", href: "#/" }}, {{ label: entry.title }}]);
  else if (activeItem) setBreadcrumb([{{ label: "Timeline", href: "#/" }}, {{ label: activeTitle(activeItem) }}]);
  else setBreadcrumb([{{ label: "Timeline", href: "#/" }}]);
  if (DATA.intent) root.appendChild(el("p", {{ className: "intent", textContent: DATA.intent }}));

  const board = el("div", {{ className: "split-board" }});
  if (slug) board.dataset.slug = slug;
  if (activeName) board.dataset.active = activeName;
  board.appendChild(svgEl("svg", {{ class: "arch-arrows history-links" }}));

  const left = el("div", {{ className: "split-arch" }});
  left.appendChild(el("div", {{ className: "layer-label split-label tone-arch", textContent: "Architecture" }}));
  left.appendChild(renderArchitecture({{ nested: true }}));
  board.appendChild(left);

  const right = el("div", {{ className: "split-history" }});
  if (DATA.active_work.length) {{
    const stack = el("div", {{ className: "stack" }});
    for (const item of DATA.active_work) stack.appendChild(renderActiveWork(item, item.name === activeName));
    right.appendChild(homeBand("Active work", stack, "tone-active"));
  }}
  const history = el("div", {{ className: "stack" }});
  if (!DATA.timeline.length) {{
    history.appendChild(el("p", {{ className: "muted", textContent: "No history entries yet." }}));
  }}
  for (const item of DATA.timeline) history.appendChild(historyCard(item, item.slug === slug));
  right.appendChild(homeBand("History", history, "tone-history"));
  board.appendChild(right);
  root.appendChild(board);

  const paint = () => paintHistoryLinks(board);
  requestAnimationFrame(() => {{
    paint();
    const selectedCard = board.querySelector(".history-card.selected");
    if (selectedCard) selectedCard.scrollIntoView({{ block: "nearest" }});
    requestAnimationFrame(paint);
  }});
  if (window.__bindifyRelayout) window.removeEventListener("resize", window.__bindifyRelayout);
  window.__bindifyRelayout = paint;
  window.addEventListener("resize", paint);
}}

function nodeLabel(node) {{
  const r = DATA.refs[node.ref_id];
  return (r && r.label) || node.id.split("/").pop();
}}

function archCard(node, extraClass) {{
  const card = el("button", {{ className: "arch-card" + (extraClass ? " " + extraClass : ""), type: "button" }});
  card.dataset.id = node.id;
  card.appendChild(el("span", {{ className: "name", textContent: nodeLabel(node) }}));
  card.appendChild(el("span", {{ className: "kind", textContent: node.type.replace("-", " ") }}));
  card.onclick = () => navigate("#/arch/" + node.id);
  return card;
}}

function renderArchitecture(options) {{
  options = options || {{}};
  const arch = DATA.architecture || {{ nodes: [], edges: [], layers: [] }};
  const panel = el("div", {{ className: options.nested ? "arch-nested" : "arch-diagram" }});
  const svg = svgEl("svg", {{ class: "arch-arrows" }});
  panel.appendChild(svg);

  const layerOf = {{}};
  const layerOrder = [];
  for (const layer of arch.layers || []) {{
    const id = layer.ref_id.replace(/^arch\\//, "");
    layerOf[id] = layer.layer;
    if (!layerOrder.includes(layer.layer)) layerOrder.push(layer.layer);
  }}
  const byId = Object.fromEntries((arch.nodes || []).map(n => [n.id, n]));
  const systems = (arch.nodes || []).filter(n => n.type === "system" && !layerOf[n.id]);
  const standards = (arch.nodes || []).filter(n =>
    !layerOf[n.id] && (n.type === "standard" || n.type === "pattern" || n.id.startsWith("standards/"))
  );

  if (systems.length) {{
    const row = el("div", {{ className: "arch-system" }});
    systems.forEach(n => row.appendChild(archCard(n, "system")));
    panel.appendChild(row);
  }}
  for (const layer of layerOrder) {{
    const band = el("div", {{ className: "layer-band" }});
    band.appendChild(el("div", {{ className: "layer-label", textContent: layer }}));
    const nodes = el("div", {{ className: "layer-nodes" }});
    for (const layerItem of arch.layers) {{
      if (layerItem.layer !== layer) continue;
      const id = layerItem.ref_id.replace(/^arch\\//, "");
      if (byId[id]) nodes.appendChild(archCard(byId[id]));
    }}
    band.appendChild(nodes);
    panel.appendChild(band);
  }}
  if (standards.length) {{
    const band = el("div", {{ className: "layer-band standards-row" }});
    band.appendChild(el("div", {{ className: "layer-label", textContent: "Standards" }}));
    const nodes = el("div", {{ className: "standards-nodes" }});
    standards.forEach(n => nodes.appendChild(archCard(n)));
    band.appendChild(nodes);
    panel.appendChild(band);
  }}
  panel.appendChild(el("p", {{
    className: "muted arch-hint",
    textContent: "Hover a box to see what it depends on. Click to open it.",
  }}));
  wireDiagram(panel);
  return panel;
}}

function svgEl(name, attrs) {{
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [k, v] of Object.entries(attrs || {{}})) node.setAttribute(k, v);
  return node;
}}

function clearArrows(panel) {{
  const svg = panel.querySelector("svg.arch-arrows");
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  panel.querySelectorAll(".arch-card").forEach(card => card.classList.remove("hot", "link", "dim"));
}}

function drawArrows(panel, sourceId, targets) {{
  const svg = panel.querySelector("svg.arch-arrows");
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const box = panel.getBoundingClientRect();
  svg.setAttribute("viewBox", "0 0 " + box.width + " " + box.height);
  const marker = svgEl("marker", {{
    id: "arch-arrow", markerWidth: "8", markerHeight: "8", refX: "7", refY: "3", orient: "auto",
  }});
  marker.appendChild(svgEl("path", {{ d: "M0,0 L7,3 L0,6 Z", fill: "#2563eb" }}));
  const defs = svgEl("defs");
  defs.appendChild(marker);
  svg.appendChild(defs);
  const src = panel.querySelector('.arch-card[data-id="' + sourceId + '"]');
  if (!src) return;
  const a = src.getBoundingClientRect();
  for (const targetId of targets) {{
    const dst = panel.querySelector('.arch-card[data-id="' + targetId + '"]');
    if (!dst) continue;
    const b = dst.getBoundingClientRect();
    const x1 = a.left + a.width / 2 - box.left;
    const y1 = a.bottom - box.top - 2;
    const x2 = b.left + b.width / 2 - box.left;
    const y2 = b.top - box.top + 2;
    svg.appendChild(svgEl("path", {{
      d: "M" + x1 + "," + y1 + " C" + x1 + "," + ((y1 + y2) / 2) + " " + x2 + "," + ((y1 + y2) / 2) + " " + x2 + "," + y2,
      fill: "none", stroke: "#2563eb", "stroke-width": "1.5", "marker-end": "url(#arch-arrow)",
    }}));
  }}
}}

function wireDiagram(panel) {{
  const depends = {{}};
  for (const edge of (DATA.architecture.edges || [])) {{
    if (edge.relation !== "depends-on" && edge.relation !== "follows") continue;
    if (!depends[edge.source]) depends[edge.source] = [];
    depends[edge.source].push(edge.target);
  }}
  panel.querySelectorAll(".arch-card").forEach(card => {{
    card.onmouseenter = () => {{
      const board = panel.closest(".split-board");
      if (board && (board.dataset.slug || board.dataset.active)) return;
      const targets = depends[card.dataset.id] || [];
      panel.querySelectorAll(".arch-card").forEach(other => {{
        other.classList.remove("hot", "link", "dim");
        if (!targets.length) return;
        if (other === card) other.classList.add("hot");
        else if (targets.includes(other.dataset.id)) other.classList.add("link");
        else other.classList.add("dim");
      }});
      if (targets.length) drawArrows(panel, card.dataset.id, targets);
      else clearArrows(panel);
    }};
    card.onmouseleave = () => {{
      const board = panel.closest(".split-board");
      if (board && (board.dataset.slug || board.dataset.active)) return;
      clearArrows(panel);
    }};
  }});
}}

function historyImpacts(slug) {{
  const entry = DATA.history_entries[slug];
  if (!entry) return [];
  const rank = {{ modified: 3, created: 2, touches: 1 }};
  const byId = {{}};
  for (const impact of entry.arch_impacts || []) {{
    const id = String(impact.ref_id || "").replace(/^arch\\//, "");
    if (!id) continue;
    const prev = byId[id];
    if (!prev || (rank[impact.action] || 0) > (rank[prev.action] || 0)) {{
      byId[id] = {{ id: id, action: impact.action || "modified" }};
    }}
  }}
  return Object.values(byId);
}}

function activeImpacts(name) {{
  const rank = {{ modified: 3, created: 2, touches: 1 }};
  const byId = {{}};
  for (const [key, step] of Object.entries(DATA.views.steps || {{}})) {{
    if (key.indexOf(name + "/") !== 0) continue;
    for (const link of step.architecture_links || []) {{
      const id = String(link.ref_id || "").replace(/^arch\\//, "");
      if (!id) continue;
      const prev = byId[id];
      if (!prev || (rank[link.action] || 0) > (rank[prev.action] || 0)) {{
        byId[id] = {{ id: id, action: link.action || "modified" }};
      }}
    }}
  }}
  return Object.values(byId).filter(impact => impact.action === "created" || impact.action === "modified");
}}

function relatedHistory(impacts) {{
  const shell = "modules/flutter-app-shell";
  const ids = impacts.map(impact => impact.id).filter(id => id !== shell);
  const slugs = [];
  for (const [slug, entry] of Object.entries(DATA.history_entries || {{}})) {{
    let shared = 0;
    const seen = {{}};
    for (const impact of entry.arch_impacts || []) {{
      if (impact.action !== "modified" && impact.action !== "created") continue;
      const id = String(impact.ref_id || "").replace(/^arch\\//, "");
      if (!id || id === shell || seen[id] || ids.indexOf(id) === -1) continue;
      seen[id] = true;
      shared += 1;
    }}
    if (shared >= 2) slugs.push(slug);
  }}
  return slugs;
}}

function paintHistoryLinks(board) {{
  if (!board.isConnected) return;
  const svg = board.querySelector(":scope > svg.history-links");
  if (!svg) return;
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  board.querySelectorAll(".impact-tag").forEach(node => node.remove());
  board.querySelectorAll(".arch-card").forEach(card => {{
    card.classList.remove("hot", "link", "dim", "modified", "touches", "created");
  }});
  board.querySelectorAll(".history-card").forEach(card => card.classList.remove("dim", "linked"));
  const slug = board.dataset.slug || "";
  const activeName = board.dataset.active || "";
  const hint = board.querySelector(".arch-hint");
  if (activeName) {{
    if (hint) hint.textContent = "Amber is this work. Blue is the architecture it changes. Green is history that changed the same parts.";
    const impacts = activeImpacts(activeName);
    const byId = {{}};
    impacts.forEach(impact => {{ byId[impact.id] = impact; }});
    board.querySelectorAll(".arch-card").forEach(card => {{
      const impact = byId[card.dataset.id];
      if (impact) {{
        card.classList.add(impact.action);
        card.appendChild(el("span", {{ className: "impact-tag", textContent: impact.action }}));
      }} else if (impacts.length) {{
        card.classList.add("dim");
      }}
    }});
    const related = relatedHistory(impacts);
    board.querySelectorAll(".history-card").forEach(card => {{
      if (related.indexOf(card.dataset.slug) !== -1) card.classList.add("linked");
      else if (related.length) card.classList.add("dim");
    }});
    const source = board.querySelector(".active-card.selected .active-title") || board.querySelector(".active-card.selected");
    if (!source) return;
    const box = board.getBoundingClientRect();
    svg.setAttribute("viewBox", "0 0 " + box.width + " " + box.height);
    const defs = svgEl("defs");
    [["hist-link", "#2563eb"], ["hist-history", "#059669"]].forEach(([id, color]) => {{
      const marker = svgEl("marker", {{
        id: id, markerWidth: "8", markerHeight: "8", refX: "7", refY: "3", orient: "auto",
      }});
      marker.appendChild(svgEl("path", {{ d: "M0,0 L7,3 L0,6 Z", fill: color }}));
      defs.appendChild(marker);
    }});
    svg.appendChild(defs);
    const origin = source.getBoundingClientRect();
    const x1 = origin.left - box.left;
    const y1 = origin.top + origin.height / 2 - box.top;
    impacts.forEach(impact => {{
      const target = board.querySelector('.arch-card[data-id="' + impact.id + '"]');
      if (!target) return;
      const edge = target.getBoundingClientRect();
      const x2 = edge.right - box.left;
      const y2 = edge.top + edge.height / 2 - box.top;
      const mid = (x1 + x2) / 2;
      svg.appendChild(svgEl("path", {{
        d: "M" + x1 + "," + y1 + " C" + mid + "," + y1 + " " + mid + "," + y2 + " " + x2 + "," + y2,
        fill: "none", stroke: "#2563eb", "stroke-width": "1.6", "marker-end": "url(#hist-link)",
      }}));
    }});
    const hx1 = origin.left + origin.width / 2 - box.left;
    const hy1 = origin.bottom - box.top;
    related.forEach(relatedSlug => {{
      const card = board.querySelector('.history-card[data-slug="' + relatedSlug + '"]');
      if (!card) return;
      const title = card.querySelector("h3") || card;
      const edge = title.getBoundingClientRect();
      const x2 = edge.left + edge.width / 2 - box.left;
      const y2 = edge.top - box.top;
      const mid = (hy1 + y2) / 2;
      svg.appendChild(svgEl("path", {{
        d: "M" + hx1 + "," + hy1 + " C" + hx1 + "," + mid + " " + x2 + "," + mid + " " + x2 + "," + y2,
        fill: "none", stroke: "#059669", "stroke-width": "1.6", "marker-end": "url(#hist-history)",
      }}));
    }});
    return;
  }}
  if (!slug) {{
    if (hint) hint.textContent = "Select active work or an update to see what it changed.";
    return;
  }}
  if (hint) hint.textContent = "Green is the open update. Blue is the architecture it changed.";
  const impacts = historyImpacts(slug);
  const byId = {{}};
  impacts.forEach(impact => {{ byId[impact.id] = impact; }});
  board.querySelectorAll(".arch-card").forEach(card => {{
    const impact = byId[card.dataset.id];
    if (impact) {{
      card.classList.add(impact.action);
      card.appendChild(el("span", {{ className: "impact-tag", textContent: impact.action }}));
    }} else if (impacts.length) {{
      card.classList.add("dim");
    }}
  }});
  const source = board.querySelector(".history-card.selected h3") || board.querySelector(".history-card.selected");
  if (!source || !impacts.length) return;
  const box = board.getBoundingClientRect();
  svg.setAttribute("viewBox", "0 0 " + box.width + " " + box.height);
  const defs = svgEl("defs");
  const marker = svgEl("marker", {{
    id: "hist-link", markerWidth: "8", markerHeight: "8", refX: "7", refY: "3", orient: "auto",
  }});
  marker.appendChild(svgEl("path", {{ d: "M0,0 L7,3 L0,6 Z", fill: "#2563eb" }}));
  defs.appendChild(marker);
  svg.appendChild(defs);
  const origin = source.getBoundingClientRect();
  const x1 = origin.left - box.left;
  const y1 = origin.top + origin.height / 2 - box.top;
  impacts.forEach(impact => {{
    const target = board.querySelector('.arch-card[data-id="' + impact.id + '"]');
    if (!target) return;
    const edge = target.getBoundingClientRect();
    const x2 = edge.right - box.left;
    const y2 = edge.top + edge.height / 2 - box.top;
    const mid = (x1 + x2) / 2;
    svg.appendChild(svgEl("path", {{
      d: "M" + x1 + "," + y1 + " C" + mid + "," + y1 + " " + mid + "," + y2 + " " + x2 + "," + y2,
      fill: "none", stroke: "#2563eb", "stroke-width": "1.6", "marker-end": "url(#hist-link)",
    }}));
  }});
}}

function renderHistoryEntry(root, slug) {{
  const entry = DATA.history_entries[slug];
  if (!entry) {{ renderNotFound(root); return; }}
  setBreadcrumb([
    {{ label: "Timeline", href: "#/" }},
    {{ label: entry.title }},
  ]);
  const sec = el("section");
  const hdr = el("div", {{ className: "detail-header page-head" }});
  const left = el("div");
  left.appendChild(el("h2", {{ textContent: entry.title }}));
  const meta = el("div", {{ className: "card-meta" }});
  meta.appendChild(el("span", {{ className: "muted", textContent: entry.date }}));
  if (entry.status) meta.appendChild(badge(entry.status));
  if (entry.merge) meta.appendChild(el("span", {{ className: "muted", textContent: entry.merge }}));
  left.appendChild(meta);
  const links = el("div", {{ className: "chip-row" }});
  if (entry.plan_ref_id) links.appendChild(ref(entry.plan_ref_id));
  if (entry.updates_ref_id) links.appendChild(ref(entry.updates_ref_id));
  if (entry.pr_ref_id) links.appendChild(ref(entry.pr_ref_id));
  left.appendChild(links);
  hdr.appendChild(left);
  hdr.appendChild(el("a", {{
    className: "open-editor", href: "file://" + entry.path, textContent: "Open in editor",
  }}));
  sec.appendChild(hdr);

  if (entry.body && entry.body.length) {{
    entry.body.forEach(p => sec.appendChild(el("p", {{ textContent: p }})));
  }} else {{
    sec.appendChild(el("h3", {{ textContent: "What changed" }}));
    sec.appendChild(bullets(entry.what_changed));
    sec.appendChild(el("h3", {{ textContent: "User impact" }}));
    sec.appendChild(bullets(entry.user_impact));
  }}

  sec.appendChild(el("h3", {{ textContent: "Architecture" }}));
  const impacts = el("div", {{ className: "stack" }});
  for (const impact of entry.arch_impacts || []) {{
    const row = el("div", {{ className: "board-card" }});
    row.appendChild(el("span", {{ className: "kind", textContent: impact.action }}));
    const line = el("div", {{ className: "chip-row" }});
    line.appendChild(ref(impact.ref_id));
    row.appendChild(line);
    if (impact.note) row.appendChild(el("p", {{ className: "muted", textContent: impact.note }}));
    impacts.appendChild(row);
  }}
  sec.appendChild(impacts);

  if (entry.follow_ups && entry.follow_ups.length) {{
    sec.appendChild(el("h3", {{ textContent: "Follow-ups" }}));
    sec.appendChild(bullets(entry.follow_ups));
  }}

  const evCount = (entry.evidence || []).length;
  if (evCount) {{
    const det = el("details");
    det.appendChild(el("summary", {{ textContent: "Evidence (" + evCount + " links)" }}));
    const ul = el("ul", {{ className: "compact" }});
    for (const ev of entry.evidence) {{
      const li = el("li");
      li.appendChild(ref(ev.ref_id));
      if (ev.note) li.appendChild(el("span", {{ className: "muted", textContent: " — " + ev.note }}));
      ul.appendChild(li);
    }}
    det.appendChild(ul);
    sec.appendChild(det);
  }}
  root.appendChild(sec);
}}

function renderPlan(root, planName) {{
  const plan = DATA.views.plans[planName];
  if (!plan) {{ renderNotFound(root); return; }}
  setBreadcrumb([
    {{ label: "Timeline", href: "#/" }},
    {{ label: planName }},
  ]);
  const sec = el("section");
  const hdr = el("div", {{ className: "page-head card-meta" }});
  hdr.appendChild(el("h2", {{ textContent: planName }}));
  hdr.appendChild(badge(plan.phase));
  if (plan.verify_status) hdr.appendChild(badge(plan.verify_status));
  sec.appendChild(hdr);
  const stack = el("div", {{ className: "stack" }});
  for (const s of plan.steps || []) {{
    const card = el(s.logged ? "button" : "div", {{
      className: "board-card" + (s.logged ? "" : " is-missing"),
    }});
    if (s.logged) card.type = "button";
    card.appendChild(el("span", {{ className: "kind", textContent: (s.logged ? "Done" : "Planned") + " · Step " + s.id }}));
    card.appendChild(el("span", {{ className: "name", textContent: s.title }}));
    if (s.logged) card.onclick = () => navigate("#/step/" + planName + "/" + s.id);
    stack.appendChild(card);
  }}
  sec.appendChild(stack);
  root.appendChild(sec);
}}

function displayStep(stepId) {{
  const number = Number(stepId);
  return "Step " + (Number.isFinite(number) ? String(number) : stepId);
}}

function umlBox(name, stereo, note) {{
  const box = el("div", {{ className: "uml-box" }});
  if (stereo) box.appendChild(el("div", {{ className: "stereo", textContent: "«" + stereo + "»" }}));
  box.appendChild(el("div", {{ className: "uname", textContent: name }}));
  if (note) box.appendChild(el("div", {{ className: "uml-note", textContent: note }}));
  return box;
}}

function umlArrow(label) {{
  const edge = el("div", {{ className: "uml-edge" }});
  edge.appendChild(el("span", {{ className: "uml-line" }}));
  if (label) edge.appendChild(el("span", {{ className: "uml-label", textContent: "«" + label + "»" }}));
  edge.appendChild(el("span", {{ className: "uml-line" }}));
  edge.appendChild(el("span", {{ className: "uml-head" }}));
  return edge;
}}

function renderImpactDiagram(step, stepId) {{
  const flows = step.impact_flows || [];
  const links = step.architecture_links || [];
  if (!flows.length && !links.length) return null;
  const panel = el("div", {{ className: "uml" }});
  if (flows.length) {{
    panel.appendChild(el("div", {{ className: "uml-caption", textContent: "Flow" }}));
    for (const flow of flows) {{
      const row = el("div", {{ className: "uml-row" }});
      row.appendChild(umlBox(flow.from));
      row.appendChild(umlArrow(""));
      row.appendChild(umlBox(flow.to));
      panel.appendChild(row);
    }}
  }}
  if (links.length) {{
    for (const link of links) {{
      const row = el("div", {{ className: "uml-link" }});
      row.appendChild(el("div", {{ className: "uml-action", textContent: link.action }}));
      const pointer = el("div", {{ className: "uml-edge uml-pointer" }});
      pointer.appendChild(el("span", {{ className: "uml-line" }}));
      pointer.appendChild(el("span", {{ className: "uml-head" }}));
      row.appendChild(pointer);
      const target = DATA.refs[link.ref_id];
      const cell = el("div");
      const box = el("button", {{ className: "uml-box", type: "button" }});
      box.appendChild(el("div", {{ className: "uname", textContent: target ? target.label : link.ref_id }}));
      if (target && target.route) box.onclick = () => navigate(target.route);
      cell.appendChild(box);
      const rawNote = (link.note || "").replace(/`/g, "");
      const note = rawNote.length > 90 ? rawNote.slice(0, 87) + "…" : rawNote;
      if (note) cell.appendChild(el("div", {{ className: "uml-note", textContent: note }}));
      row.appendChild(cell);
      panel.appendChild(row);
    }}
  }}
  return panel;
}}

function trimChangeText(text) {{
  return text.replace(/^\\s+|\\s+$/g, "").replace(/\\s{{2,}}/g, " ");
}}

function parseChange(segments) {{
  const parts = (segments || []).map(seg => ({{ ...seg }}));
  if (parts[0] && parts[0].type === "text") {{
    parts[0].text = parts[0].text.replace(/^\\d{{4}}-\\d{{2}}-\\d{{2}}\\s+—\\s+/, "");
  }}
  let stepId = "";
  let sourceRef = "";
  for (const part of parts) {{
    if (!sourceRef && part.type === "ref" && /^plan-artifact\\//.test(part.ref_id)) sourceRef = part.ref_id;
    if (!stepId && part.type === "text") {{
      const match = part.text.match(/Step-(\\d+)/i);
      if (match) {{
        stepId = match[1];
        part.text = part.text.replace(/\\s*Step-\\d+\\s*(?:—|-|–)?\\s*/i, " ");
      }}
    }}
  }}
  const body = parts.filter(part => {{
    if (part.type === "ref" && part.ref_id === sourceRef) return false;
    if (part.type === "text") part.text = trimChangeText(part.text);
    return part.type === "ref" || part.type === "code" || part.text;
  }});
  return {{ stepId, sourceRef, body }};
}}

function stepPill(stepId, sourceRef) {{
  const plan = (sourceRef || "").split("/")[1] || "";
  const padded = stepId.padStart(3, "0");
  const label = "Step " + padded;
  const key = plan + "/" + padded;
  const canOpen = plan && DATA.views.steps && DATA.views.steps[key];
  const pill = el(canOpen ? "button" : "span", {{ className: "step-pill", textContent: label }});
  if (canOpen) {{
    pill.type = "button";
    pill.onclick = e => {{ e.stopPropagation(); navigate("#/step/" + plan + "/" + padded); }};
  }}
  return pill;
}}

function renderChangeLog(entries) {{
  const parsed = entries.map(parseChange);
  const groups = [];
  const bySource = {{}};
  for (const item of parsed) {{
    const key = item.sourceRef || "";
    if (!bySource[key]) {{
      bySource[key] = {{ sourceRef: item.sourceRef, items: [] }};
      groups.push(bySource[key]);
    }}
    bySource[key].items.push(item);
  }}
  const wrap = el("div");
  for (const group of groups) {{
    const block = el("div", {{ className: "change-group" }});
    if (group.sourceRef) {{
      const source = el("div", {{ className: "chip-row" }});
      source.appendChild(ref(group.sourceRef));
      block.appendChild(source);
    }}
    const steps = group.items.filter(item => item.stepId).sort((a, b) => Number(a.stepId) - Number(b.stepId));
    const notes = group.items.filter(item => !item.stepId);
    const list = el("div", {{ className: "change-steps" }});
    for (const item of steps.concat(notes)) {{
      const row = el("div", {{ className: "change-step" + (item.stepId ? "" : " note") }});
      if (item.stepId) row.appendChild(stepPill(item.stepId, group.sourceRef));
      const copy = el("div", {{ className: "step-copy" }});
      renderInline(copy, item.body);
      row.appendChild(copy);
      list.appendChild(row);
    }}
    block.appendChild(list);
    wrap.appendChild(block);
  }}
  return wrap;
}}

function renderStep(root, planName, stepId) {{
  const key = planName + "/" + stepId;
  const step = DATA.views.steps[key];
  if (!step) {{ renderNotFound(root); return; }}
  setBreadcrumb([
    {{ label: "Timeline", href: "#/" }},
    {{ label: planName, href: "#/plan/" + planName }},
    {{ label: displayStep(stepId) }},
  ]);
  const sec = el("section");
  const head = el("div", {{ className: "page-head" }});
  head.appendChild(el("h2", {{ textContent: displayStep(stepId) + ": " + step.title }}));
  if (step.timestamp) head.appendChild(el("p", {{ className: "kind-line", textContent: step.timestamp }}));
  sec.appendChild(head);
  const summary = el("div", {{ className: "prose" }});
  if (step.summary && step.summary.length && Array.isArray(step.summary[0])) {{
    const list = richBullets(step.summary);
    if (list) summary.appendChild(list);
  }} else {{
    renderBlocks(summary, step.summary);
  }}
  sec.appendChild(summary);
  if (step.file_changes && step.file_changes.length) {{
    const det = el("details");
    det.appendChild(el("summary", {{ textContent: step.file_changes.length + " file changes" }}));
    det.appendChild(richBullets(step.file_changes));
    sec.appendChild(det);
  }}
  const diagram = renderImpactDiagram(step, stepId);
  if (diagram) {{
    sec.appendChild(el("h3", {{ textContent: "Impact & connections" }}));
    sec.appendChild(diagram);
  }} else if (step.impact && step.impact.length) {{
    sec.appendChild(el("h3", {{ textContent: "Impact & connections" }}));
    const impact = el("p", {{ className: "muted" }});
    renderInline(impact, step.impact);
    sec.appendChild(impact);
  }}
  root.appendChild(sec);
}}

function renderArch(root, archId) {{
  const obj = DATA.views.arch[archId];
  if (!obj) {{ renderNotFound(root); return; }}
  setBreadcrumb([
    {{ label: "Timeline", href: "#/" }},
    {{ label: obj.id.split("/").pop() }},
  ]);
  const sec = el("section");
  const archRef = DATA.refs[obj.ref_id];
  const head = el("div", {{ className: "page-head" }});
  head.appendChild(el("h2", {{
    className: "tone-arch", textContent: (archRef && archRef.label) || obj.id.split("/").pop(),
  }}));
  head.appendChild(el("p", {{ className: "kind-line",
    textContent: obj.type + " · " + obj.status + (obj.layer ? " · " + obj.layer : "") }}));
  sec.appendChild(head);
  const responsibility = el("div", {{ className: "prose" }});
  renderBlocks(responsibility, obj.responsibility);
  sec.appendChild(responsibility);
  if (obj.change_log && obj.change_log.length) {{
    sec.appendChild(el("h3", {{ textContent: "Recent changes" }}));
    sec.appendChild(renderChangeLog(obj.change_log));
  }}
  root.appendChild(sec);
}}

function renderFile(root, fileKey) {{
  const view = DATA.views.files[fileKey];
  if (!view) {{
    const refObj = Object.values(DATA.refs).find(r => r.id === "file/" + fileKey);
    if (refObj) {{
      setBreadcrumb([{{ label: "Timeline", href: "#/" }}, {{ label: refObj.label }}]);
      root.appendChild(el("section", {{}}, [
        el("p", {{ textContent: refObj.label }}),
        el("a", {{ href: "file://" + refObj.path, textContent: "Open in editor" }}),
      ]));
      return;
    }}
    renderNotFound(root); return;
  }}
  setBreadcrumb([{{ label: "Timeline", href: "#/" }}, {{ label: view.title }}]);
  const sec = el("section");
  const head = el("div", {{ className: "page-head" }});
  head.appendChild(el("h2", {{ textContent: view.title }}));
  sec.appendChild(head);
  for (const s of view.sections || []) {{
    sec.appendChild(el("h3", {{ textContent: s.heading }}));
    sec.appendChild(bullets(s.bullets));
  }}
  sec.appendChild(el("a", {{ href: "file://" + view.path, textContent: "Open in editor", className: "open-editor" }}));
  root.appendChild(sec);
}}

function renderNotFound(root) {{
  setBreadcrumb([{{ label: "Timeline", href: "#/" }}, {{ label: "Not found" }}]);
  root.appendChild(el("section", {{}}, [
    el("p", {{ textContent: "Page not found." }}),
    el("a", {{ href: "#/", textContent: "Back to timeline" }}),
  ]));
}}

function route() {{
  const app = document.getElementById("app");
  app.innerHTML = "";
  const {{ parts }} = parseRoute();
  if (!parts.length) {{ renderBoard(app, ""); return; }}
  if (parts[0] === "history" && parts[1]) {{ renderBoard(app, decodeURIComponent(parts[1])); return; }}
  if (parts[0] === "active" && parts[1]) {{ renderBoard(app, "", decodeURIComponent(parts[1])); return; }}
  if (parts[0] === "plan" && parts[1]) {{ renderPlan(app, parts[1]); return; }}
  if (parts[0] === "step" && parts[1] && parts[2]) {{ renderStep(app, parts[1], parts[2]); return; }}
  if (parts[0] === "arch" && parts[1]) {{
    renderArch(app, parts.slice(1).join("/")); return;
  }}
  if (parts[0] === "file" && parts[1]) {{
    renderFile(app, parts.slice(1).join("--")); return;
  }}
  renderNotFound(app);
}}

window.addEventListener("hashchange", route);
route();
</script>
</body>
</html>"""


def resolve_bindify_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    parent = Path(__file__).resolve().parent.parent
    if (parent / "history").is_dir() or (parent / "architecture").is_dir():
        return parent
    raise SystemExit(
        "Pass --bindify-root pointing at the tracking folder (.bindify/ or bindify/)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Bindify history-first dashboard")
    parser.add_argument("--bindify-root", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    bindify_root = resolve_bindify_root(args.bindify_root)
    output = args.output or bindify_root / "overview.html"

    data = scan_bindify(bindify_root)
    output.write_text(render_html(data), encoding="utf-8")
    print(f"Wrote {output}")
    print(f"  History entries: {len(data['timeline'])}")
    print(f"  Active work: {len(data['active_work'])}")
    print(f"  Refs: {len(data['refs'])}")

    if not args.no_open:
        webbrowser.open(output.as_uri())


if __name__ == "__main__":
    main()
