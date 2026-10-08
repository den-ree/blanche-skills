# Command: investigate

Side process for investigating a feature, fix, or similar question. Off the plan pipeline. Reads tracking history before product code. The note can be handed to `draft-brief` as `DISCUSSION_SOURCES`.

---

## When to use

- Before a brief, when the question is "have we already fixed this?" or "what did this feature do?"
- Research for a feature, fix, refactor, or chore that should not start `wip-docs/` yet
- The user asks to investigate, look up prior fixes, or turn research into something a brief can start from

Do not use this command to execute a plan step, log a hotfix, or write `brief.md`.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `TOPIC` | yes | Feature, fix, or question in the user's words |
| `CATEGORY_HINT` | no | `features` \| `fixes` \| `refactor` \| `chore` — narrows the name scan |
| `TARGET_AREA` | no | Code area for the later pass. Required only when the scan names no files and the question still needs code |
| `SAVE` | no | `true` writes `wip-docs/investigation.md`. Default: reply only |

---

## Output

Reply with the skill template `references/templates/investigation.md`.

Write a file only when `SAVE=true`:

```
wip-docs/investigation.md
```

That file is scratch. It is not brief, proposal, plan, updates, verify, or coordinator. Migration does not copy it.

---

## Procedure

Read this command fully before opening the product tree.

1. Resolve the tracking root
   - Explicit path, else `.bindify/`, else `bindify/`
   - If neither exists, say so, skip the name scan, and continue at step 5

2. Name scan — folder names only, no file contents
   - List immediate child directory names of `development/features/`, `development/fixes/`, `development/refactor/`, and `development/chore/`
   - If `CATEGORY_HINT` is set, list only that category
   - Under each feature directory, list plan names only. If a child directory is named `plans`, list its children. Otherwise list child directory names. Skip files
   - Tokenize `TOPIC`: lowercase, split on whitespace and `-` `/` `_`
   - Drop tokens shorter than 3 characters, and drop `the`, `and`, `for`, `with`, `this`, `that`, `fix`, `bug`, `issue`, `feature`, `hotfix`
   - A name matches when a remaining token equals the full name or equals one hyphen-separated segment of the name. `play` does not match `playback`. `playback` matches `playback-editor`
   - Rank feature folders by how many segments match. Keep at most 5. If more match, list the extra names in the note and do not open them
   - A related fix, inside a matched feature, is any of:
     - `development/fixes/<feature-name>/hotfixes.md`
     - a plan directory whose name contains `fix`, `hotfix`, `bug`, `regression`, or `crash`
     - a plan directory that itself matched a topic token
   - If no feature folder matches, run the same segment match on plan names. A plan match pulls in its parent feature. Still cap at 5 features

3. Read matched fixes only
   - `hotfixes.md`: each entry's date, title, **Summary**, and **Outcome**. Skip files changed unless the outcome is unclear
   - Each related plan: `brief.md` **Problem statement** and **Goals** only. If there is no brief, the first headings of `coordinator.md`
   - At most 3 plans per feature. Prefer fix-like plan names, then token matches
   - Do not open `proposal.md`, `plan.md`, `updates.md`, or `verify.md` in this step

4. Stop before code when the slices answer the question
   - If the user only asked what was already fixed, write the note and stop
   - Record **Codebase researched:** `no`

5. Code pass — only after steps 2–4
   - Open no product source file before the name scan and the matched-fix reads finish
   - Scope is the repo-relative paths named in those slices
   - If the slices name no paths, use `TARGET_AREA`. If that is missing and the question needs code, ask. Do not walk the repo
   - Follow `research-codebase` guardrails: read-only, no builds, paths and symbols only
   - Put results in **Code findings**

6. Fill the template
   - **Related fixes**, **Already done**, and **Still open** come from the slices. If nothing matched, say `no feature-name match` and list the feature names scanned
   - **Brief seed** restates the gap a later brief would capture. It is not `wip-docs/brief.md`
   - Do not invent causes the slices did not state

7. Hand-off
   - Do not run `draft-brief` in this command
   - Tell the user the brief seed can be `DISCUSSION_SOURCES` for `draft-brief`. The clarify gate still runs

---

## Guardrails

- Name scan first. Product source second
- Match hyphen segments, not substrings
- Do not grep the tracking tree for file contents during the name scan
- Do not modify product code, tracking files, or plan artifacts
- Do not write `wip-docs/brief.md`, `proposal.md`, or `plan.md`
- Do not start `draft-brief`, `log-hotfix`, or `iterate-planning-mode` from this command
- Repo-relative paths only
- No code dumps in the note
- If `SAVE=true` and `wip-docs/` already holds a different feature, stop and ask

---

## Acceptance criteria

- The note exists in the reply (and at `wip-docs/investigation.md` only when `SAVE=true`)
- Feature-folder names were listed before any product source file was opened
- Related fixes are limited to matched `hotfixes.md` entries and matched plan briefs
- **Brief seed** is present and labeled as input for `draft-brief`, not as the brief
- `draft-brief` was not run
