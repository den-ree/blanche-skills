# Command: regenerate-overview

Build the history dashboard from the tracking vault. Architecture stays on the left, history and active work on the right, and selecting either draws lines to the objects it changed.

---

## When to use

- After `generate-history-summary` (that command runs this)
- After manual edits to tracking `history/`, `architecture/`, or an active plan
- When the user asks to open or refresh the overview page

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `BINDIFY_TRACKING_PATH` | no | Tracking root; auto-detect `.bindify/` then `bindify/` if omitted |
| `OPEN` | no | If true, open `overview.html` in the browser after write |

---

## Procedure

1. Resolve the tracking root (`.bindify/` then `bindify/`). Stop if neither exists.
2. Run the skill script, not a copy inside the tracking repo:

   ```bash
   python3 <skill>/references/scripts/overview.py --bindify-root <tracking-root> --no-open
   ```

   `<skill>` is the installed bindify skill directory (the folder that contains this command file's `../scripts/`).

3. If `OPEN` is true, open `<tracking-root>/overview.html` in the browser. Omit `--no-open` only when the user asked to view the page.
4. Report the counts the script prints: history entries, active work, refs.

---

## Output

- `<tracking-root>/overview.html` — static dashboard. Markdown under `history/`, `architecture/`, and plan docs stays the source of truth.

The page reads a history card's `touches` / `modified` / `created` properties as lines from that update to architecture. Active work lines come from the current plan's step Architecture sections. Those sections must use `` `created` `` / `` `modified` `` / `` `touches` `` plus a wikilink, or the diagram has nothing to draw.

---

## Hard rules

- Do not commit `overview.html` unless the tracking repo already tracks it.
- Prefer `--no-open` in agent runs unless the user asked to view the page.
- Do not look in the tracking repo for this script. It lives in the skill.

---

## Related

- `[[references/commands/generate-history-summary.md]]`
- `[[references/scripts/overview.py]]`
- `[[references/scripts/bindify_parse.py]]`
