# Command: update-links

Maintain Obsidian-friendly links across bindify markdown files by normalizing inline `[[wiki-links]]` and `## Related` backlinks.

---

## When to use

- After any command writes or updates a bindify markdown file
- When file relationships changed and backlinks need refresh
- When manually repairing plan-folder navigation

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `PLAN_FOLDER_PATH` | yes | Repo-relative path to a specific plan folder |
| `CHANGED_FILES` | no | List of recently edited markdown files for targeted link repair |

---

## Procedure

1. Discover markdown files
   - Read all `.md` files under `PLAN_FOLDER_PATH`
   - Include `coordinator.md` and related `fixes/*/hotfixes.md` if explicitly referenced

2. Normalize inline links
   - Detect file mentions and add `[[...]]` links when obvious and safe
   - Keep existing manual link text intact

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

- Prefer relative wiki-link targets (for example, `[[plan.md]]`, `[[../coordinator.md]]`)
- Keep one link format consistently across the plan folder
- Avoid duplicate entries in `## Related`
- Keep link labels human-readable

---

## Guardrails

- Never alter execution logs or checklist content except link markup
- Never remove historical entries from `updates.md` or `hotfixes.md`
- If target file is ambiguous, stop and ask

---

## Acceptance criteria

- All changed plan files contain valid wiki-links where needed
- Every updated file has a `## Related` section
- Cross-file navigation is consistent and non-duplicative
