# Command: draft-brief

Create `brief.md` from planning discussion inputs and mark it ready for proposal generation.

---

## When to use

- A planning discussion is complete and the team wants a structured brief
- A new plan folder is being initialized
- The next action is to generate `proposal.md`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` |
| `FEATURE_NAME` | yes | Feature folder name in kebab-case |
| `PLAN_NAME` | yes | Plan folder name in kebab-case |
| `DISCUSSION_SOURCES` | yes | Conversation context used to derive problem, goals, constraints, and success criteria |

---

## Output path

Write to:

```
.bindify/development/<category>/<feature-name>/plans/<plan-name>/brief.md
```

---

## Procedure

1. Resolve output path
   - Validate `CATEGORY`, `FEATURE_NAME`, and `PLAN_NAME`
   - Ensure plan directory is under `.bindify/development/`
   - If path is ambiguous, stop and ask

2. Gather source context
   - Read all `DISCUSSION_SOURCES`
   - Capture only decisions actually discussed
   - Keep unresolved questions in `Open questions`

3. Populate brief template
   - Use `.bindify/templates/brief.md` structure
   - Fill `Problem statement`, `Goals`, `Out of scope`, `Constraints`, `Inputs available`, `Success criteria`, `Open questions`
   - Set `Status` to `ready for proposal`

4. Save markdown
   - Create missing directories if needed
   - Save plain markdown only

5. Run link maintenance
   - Invoke `update-links` for the current plan folder

---

## Guardrails

- Use repo-relative paths only
- Do not invent decisions not in sources
- Do not include source code in `brief.md`
- Do not generate `proposal.md` or `plan.md` in this command
- If required context is missing, stop and ask

---

## Acceptance criteria

- `brief.md` exists in the correct plan folder
- Brief is complete enough for proposal generation
- `Status` is `ready for proposal`
- `update-links` has run for the plan folder
