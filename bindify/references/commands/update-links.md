# Command: update-links

Maintain Obsidian-friendly links across bindify markdown files by normalizing inline `[[wiki-links]]` and, for non-history files, `## Related` backlinks.

Works for:
- flat active WIP: `wip-docs/`
- nested durable plans: `development/<category>/<feature>/plans/<plan>/` inside `.bindify/` or `bindify/`
- root history: tracking `history/` (cards + index)

---

## When to use

- After any command writes or updates a bindify / WIP markdown file
- When file relationships changed and backlinks need refresh
- When manually repairing plan-folder or `wip-docs/` navigation
- After migrating `wip-docs/` into the Bindify tracking repo
- After creating or refreshing history cards

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `PLAN_FOLDER_PATH` | yes | Repo-relative path to `wip-docs/`, a nested plan folder under Bindify `development/`, or tracking `history/` |
| `CHANGED_FILES` | no | List of recently edited markdown files for targeted link repair |

---

## Procedure

1. Discover markdown files
   - Read all `.md` files under `PLAN_FOLDER_PATH`
   - If path is `wip-docs/`, include `coordinator.md` in the same flat folder
   - If path is a nested plan folder, also include sibling `../../coordinator.md` and related `fixes/*/hotfixes.md` when explicitly referenced
   - If path is tracking `history/`, include `history/index.md` and every `history/entries/*.md`

2. Branch on history cards vs other files
   - A **history card** is any `history/entries/*.md` with frontmatter `type: history` (or under `history/entries/` by path).
   - For history cards, follow **History card rules** below and skip the generic `## Related` rebuild.
   - For `history/index.md`, only ensure aliased entry links resolve; do not add a `## Related` dump.
   - For all other files, continue with steps 3–5.

3. Normalize inline links (non-history)
   - Detect file mentions and add `[[...]]` links when obvious and safe
   - Keep existing manual link text intact
   - For flat `wip-docs/`, prefer same-folder targets: `[[brief.md]]`, `[[proposal.md]]`, `[[plan.md]]`, `[[updates.md]]`, `[[verify.md]]`, `[[coordinator.md]]`
   - For nested Bindify plans, prefer relative targets: `[[plan.md]]`, `[[../coordinator.md]]` as appropriate

4. Rebuild `## Related` section (non-history only)
   - Ensure each non-history file has one `## Related` section
   - List inbound/outbound linked docs as bullet links
   - Keep section at the bottom of file
   - Never add `## Related` to history cards or rebuild path dumps into them

5. Preserve manual edits
   - Do not rewrite body sections unrelated to linking
   - Do not remove manually added links unless broken

6. Save updates
   - Update only files needing link changes

---

## History card rules

For each `history/entries/*.md`:

1. Read YAML properties: `plan`, `updates`, `touches`, `modified`, `created` (wikilink strings or lists).
2. Ensure the body connection lines use aliased wikilinks for the same targets:
   - Property `touches: ["[[session-store]]"]` ↔ body `Touches [[session-store|Session store]].`
   - Same pairing for `modified` / `created`.
3. Prefer human labels in aliases (`Session store`), ids in the link target (`session-store`).
4. Keep property lists and body aliases synchronized — if one side gains or loses a target, update the other.
5. Do **not** add a `## Related` section. Do **not** insert path rows into the body.
6. Leave `pr` / `merge` as plain URL strings in properties (not wikilinks).
7. After migration, if `plan` / `updates` still point at `wip-docs/`, rewrite them to the durable `development/...` destinations (see `log-pr`).

---

## Linking rules

- Prefer relative wiki-link targets
- Keep one link format consistently across the folder
- Avoid duplicate entries in `## Related` (non-history files)
- Keep link labels human-readable
- After migration, rewrite any leftover `wip-docs/` path references to the durable Bindify destinations

---

## Guardrails

- Never alter execution logs or checklist content except link markup
- Never remove historical entries from `updates.md` or `hotfixes.md`
- Never add `## Related` path lists to history cards
- If target file is ambiguous, stop and ask

---

## Acceptance criteria

- All changed plan/WIP files contain valid wiki-links where needed
- Every updated non-history file has a `## Related` section
- History cards keep property link lists and body aliases on the same targets, with no `## Related` dump
- Cross-file navigation is consistent and non-duplicative for flat WIP, nested plans, and history
