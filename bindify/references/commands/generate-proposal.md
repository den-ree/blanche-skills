# Command: generate-proposal

Generate `proposal.md` from a ready `brief.md`, then hand off to human review.

---

## When to use

- `wip-docs/brief.md` exists and is marked `ready for proposal`
- The team needs an options-based implementation proposal
- Human review should happen before creating `plan.md`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` — must match brief metadata |
| `FEATURE_NAME` | yes | Feature name in kebab-case — must match brief metadata |
| `PLAN_NAME` | yes | Plan name in kebab-case — must match brief metadata |
| `PATH_TO_BRIEF_MD` | no | Defaults to `wip-docs/brief.md` |

---

## Output path

Write to:

```
wip-docs/proposal.md
```

---

## Procedure

Read `references/docs/working-style.md` first. Chat is caveman. `proposal.md` stays normal prose.

1. Validate inputs and path
   - Confirm `PATH_TO_BRIEF_MD` (default `wip-docs/brief.md`) exists
   - Confirm brief header `Category` / `Feature` / `Plan` match the inputs (or infer inputs from the brief)

2. Validate brief readiness
   - Read `brief.md` fully
   - Confirm `Status` is `ready for proposal`
   - If not ready, stop and ask for brief updates

3. Generate proposal content (Micro-Proposal)
   - Use the **skill** template `references/templates/proposal.md` (not the project tracking folder)
   - Copy `Category`, `Feature`, `Plan` from the brief into the proposal header
   - Climb the ponytail ladder before choosing an approach: need, existing code, stdlib, native platform, installed dependency, one line, then the minimum that works. Read the code the change would touch first.
   - `Approach` is the first rung that holds (max 2–3 sentences). `Tradeoff` names what was skipped and when to add it.
   - If the brief locked a heavier solution and the user has not been shown an earlier rung that meets the same goals, stop and ask once. If they already picked after seeing it, follow that pick. Do not re-argue an explicit request.
   - Fill `Proposed steps`, `Risks and unknowns`
   - **Prototype-First convention**: If the plan involves a new UI feature or interactive flow, `Step-001` must be a `UI Prototype` (mock state, full interactive navigation, zero backend/persistence dependencies)
   - Keep total word count under 250 words
   - Set `Status` to `proposed`
   - Leave `Human review` as a human-owned section

4. Save markdown
   - Save plain markdown only to `wip-docs/proposal.md`

5. Run link maintenance
   - Invoke `update-links` for `wip-docs/`

---

## Guardrails

- Hard word limit: strictly ≤ 250 words
- Prototype-first: user-facing features must introduce a mock UI prototype in Step-001 before backend wiring
- Do not create or modify `plan.md`
- Do not mark proposal as `approved` (human-only decision)
- Use repo-relative paths in outputs
- Do not write into the Bindify tracking submodule for active WIP
- If brief context is insufficient, or necessity was never picked, stop and ask
- Do not add a dependency, abstraction, or step the ladder rejects unless the brief explicitly requires it

---

## Acceptance criteria

- `wip-docs/proposal.md` exists with matching Category/Feature/Plan metadata
- Proposal includes options, tradeoffs, and proposed steps adhering to the ≤250 word limit
- If user-facing, Step-001 specifies a Prototype step
- `Status` is `proposed`
- `update-links` has run for `wip-docs/`
