# Command: update-links

Maintain Obsidian-friendly links across bindify markdown files by normalizing inline `[[wiki-links]]` and `## Related` backlinks.

Works for both:
- flat active WIP: `wip-docs/`
- nested durable plans: `development/<category>/<feature>/plans/<plan>/` inside `.bindify/` or `bindify/`

---

## When to use

- After any command writes or updates a bindify / WIP markdown file
- When file relationships changed and backlinks need refresh
- When manually repairing plan-folder or `wip-docs/` navigation
- After migrating `wip-docs/` into the Bindify tracking repo

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `PLAN_FOLDER_PATH` | yes | Repo-relative path to `wip-docs/` **or** a nested plan folder under Bindify `development/` |
| `CHANGED_FILES` | no | List of recently edited markdown files for targeted link repair |

---

## Procedure

1. Discover markdown files
   - Read all `.md` files under `PLAN_FOLDER_PATH`
   - If path is `wip-docs/`, include `coordinator.md` in the same flat folder
   - If path is a nested plan folder, also include sibling `../../coordinator.md` and related `fixes/*/hotfixes.md` when explicitly referenced

2. Normalize inline links
   - Detect file mentions and add `[[...]]` links when obvious and safe
   - Keep existing manual link text intact
   - For flat `wip-docs/`, prefer same-folder targets: `[[brief.md]]`, `[[proposal.md]]`, `[[plan.md]]`, `[[updates.md]]`, `[[verify.md]]`, `[[coordinator.md]]`
   - For nested Bindify plans, prefer relative targets: `[[plan.md]]`, `[[../coordinator.md]]` as appropriate

3. Rebuild `## Related` section
   - Ensure each file has one `## Related` section
   - List inbound/outbound linked docs as bullet links
   - Keep section at the bottom of file

4. Preserve manual edits
   - Do not rewrite body sections unrelated to linking
   - Do not remove manually added links unless broken

5. Save updates
   - Update only files needing link changes

---

## Linking rules

- Prefer relative wiki-link targets
- Keep one link format consistently across the folder
- Avoid duplicate entries in `## Related`
- Keep link labels human-readable
- After migration, rewrite any leftover `wip-docs/` path references to the durable Bindify destinations

---

## Guardrails

- Never alter execution logs or checklist content except link markup
- Never remove historical entries from `updates.md` or `hotfixes.md`
- If target file is ambiguous, stop and ask

---

## Acceptance criteria

- All changed plan/WIP files contain valid wiki-links where needed
- Every updated file has a `## Related` section
- Cross-file navigation is consistent and non-duplicative for both flat and nested layouts
