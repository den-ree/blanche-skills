# Command: save-agent-plan

Generate and save `plan.md` from an approved `proposal.md` into the active `wip-docs/` folder.

---

## When to use

- A proposal was reviewed by a human and approved
- The team is ready to transform proposal steps into executable plan steps
- A source-of-truth `plan.md` is needed for `iterate-planning-mode`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` — must match proposal/brief metadata |
| `FEATURE_NAME` | yes | Feature name in kebab-case |
| `PLAN_NAME` | yes | Plan name in kebab-case |
| `PATH_TO_PROPOSAL_MD` | no | Defaults to `wip-docs/proposal.md` |
| `PATH_TO_BRIEF_MD` | no | Defaults to `wip-docs/brief.md` |
| `ALLOW_OVERWRITE` | no | `true` only when human explicitly approves replacing an existing `plan.md` |

---

## Output path

Write to:

```
wip-docs/plan.md
```

If `plan.md` already exists and `ALLOW_OVERWRITE` is not `true`, create:

```
wip-docs/plan-v2.md
```

Increment (`plan-v3.md`, `plan-v4.md`, ...) if needed.

---

## Procedure

Read `references/docs/working-style.md` first. Chat is caveman. `plan.md` stays normal prose.

1. Resolve the active WIP path
   - Validate `CATEGORY`, `FEATURE_NAME`, and `PLAN_NAME`
   - Ensure output lands in `wip-docs/` at the host project root
   - Confirm metadata matches existing `brief.md` / `proposal.md` when present
   - If path is ambiguous, stop and ask the human

2. Validate proposal approval
   - Read `PATH_TO_PROPOSAL_MD` fully
   - Confirm `Human review -> Decision` is `approved` or `approved with changes`
   - If decision is missing, `rejected`, or ambiguous, stop and ask

3. Gather plan context
   - Read proposal sections: `Approach`, `Tradeoff`, `Proposed steps`, `Risks and unknowns`
   - Read `brief.md` when available for goals, constraints, and success criteria

4. Generate the execution plan
   - Convert approved proposal into actionable, ordered steps
   - Each step is the minimum work that satisfies the approved proposal. Do not add steps for later, scaffolding, or speculative flexibility.
   - Implementation tasks name the ponytail rung: reuse, stdlib, native platform, or installed dependency when that rung holds.
   - If the approved proposal is heavier than an earlier rung and the human was not shown that rung, stop and ask once. If they approved after seeing it, follow the approval.
   - Respect the **Prototype-First convention**: for interactive UI features, ensure `Step-001` is scoped to a full-flow UI prototype using static/mock state
   - Each step must include:
     - `Step ID`
     - `Goal`
     - `Inputs/Dependencies`
     - `Implementation Tasks`
     - `Expected Outputs` (repo-relative file paths and/or artifacts)
     - `Done Criteria`
   - Include explicit `Out of Scope` and `Risks/Assumptions` sections

5. Save as markdown
   - Create `wip-docs/` if needed
   - Save plan to `wip-docs/plan.md` (or versioned fallback file per Output path rules)
   - Include header metadata: `Category`, `Feature`, `Plan`
   - Keep content plain markdown only

6. Run link maintenance
   - Invoke `update-links` for `wip-docs/`

---

## Required plan template

```markdown
# Plan: <human-readable plan title>

**Category:** `features` | `fixes` | `refactor` | `chore`
**Feature:** `<feature-name>`
**Plan:** `<plan-name>`
**WIP path:** `wip-docs/`
**Migration destination:** `development/<category>/<feature-name>/plans/<plan-name>/`
**Generated From:** approved `proposal.md` (+ optional `brief.md`)
**Date:** <YYYY-MM-DD>

## Discussion Summary
- <why this work is needed>
- <key constraints and context>
- <alternatives considered and why rejected>
- <selected approach and rationale>

## Scope
- In scope: <items>
- Out of scope: <items>

## Risks and Assumptions
- Risks: <items>
- Assumptions: <items>

## Execution Steps

### Step-001: <title>
**Goal:** <outcome>
**Inputs/Dependencies:** <files, modules, approvals>
**Implementation Tasks:**
- <task 1>
- <task 2>
**Expected Outputs:**
- `<repo-relative-path>`
**Done Criteria:**
- <observable completion condition>

### Step-002: <title>
...

## Related
- `[[brief.md]]`
- `[[proposal.md]]`
- `[[updates.md]]`
```

---

## Guardrails

- Use repo-relative paths only
- Do not invent decisions not present in approved proposal or brief
- Do not include source code in `plan.md`
- Do not execute implementation work in this command
- Do not modify `updates.md` or `verify.md`
- Do not write the plan into the Bindify tracking submodule yet
- If proposal approval state is missing or invalid, stop and ask

---

## Acceptance criteria

- Plan file is saved under `wip-docs/plan.md` (or versioned fallback)
- Header includes Category / Feature / Plan metadata for migration
- Plan reflects approved proposal steps and review adjustments
- Uses ordered, actionable steps with clear outputs and done criteria
- Contains `Scope`, `Out of scope`, and `Risks/Assumptions`
- `update-links` has run for `wip-docs/`
