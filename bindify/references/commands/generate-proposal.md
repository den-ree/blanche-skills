# Command: generate-proposal

Generate `proposal.md` from a ready `brief.md`, then hand off to human review.

---

## When to use

- `brief.md` exists and is marked `ready for proposal`
- The team needs an options-based implementation proposal
- Human review should happen before creating `plan.md`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` |
| `FEATURE_NAME` | yes | Feature folder name in kebab-case |
| `PLAN_NAME` | yes | Plan folder name in kebab-case |
| `PATH_TO_BRIEF_MD` | yes | Repo-relative path to `brief.md` |

---

## Output path

Write to:

```
.bindify/development/<category>/<feature-name>/plans/<plan-name>/proposal.md
```

---

## Procedure

1. Validate inputs and path
   - Confirm `PATH_TO_BRIEF_MD` exists
   - Confirm file belongs to the specified category/feature/plan path

2. Validate brief readiness
   - Read `brief.md` fully
   - Confirm `Status` is `ready for proposal`
   - If not ready, stop and ask for brief updates

3. Generate proposal content
   - Use `.bindify/templates/proposal.md`
   - Fill `Approach`, `Options considered`, `Proposed steps`, `Risks and unknowns`
   - Set `Status` to `proposed`
   - Leave `Human review` as a human-owned section

4. Save markdown
   - Save plain markdown only

5. Run link maintenance
   - Invoke `update-links` for the current plan folder

---

## Guardrails

- Do not create or modify `plan.md`
- Do not mark proposal as `approved` (human-only decision)
- Use repo-relative paths in outputs
- If brief context is insufficient, stop and ask

---

## Acceptance criteria

- `proposal.md` exists in the correct plan folder
- Proposal includes options, tradeoffs, and proposed steps
- `Status` is `proposed`
- `update-links` has run for the plan folder
