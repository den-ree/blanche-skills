# Command: save-agent-plan

Generate and save `plan.md` from an approved `proposal.md` into the correct Bindify feature path.

---

## When to use

- A proposal was reviewed by a human and approved
- The team is ready to transform proposal steps into executable plan steps
- A source-of-truth `plan.md` is needed for `iterate-planning-mode`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` |
| `FEATURE_NAME` | yes | Feature folder name in kebab-case |
| `PLAN_NAME` | yes | Plan folder name in kebab-case |
| `PATH_TO_PROPOSAL_MD` | yes | Repo-relative path to reviewed `proposal.md` |
| `PATH_TO_BRIEF_MD` | no | Repo-relative path to `brief.md` (required when not inferable from proposal) |
| `ALLOW_OVERWRITE` | no | `true` only when human explicitly approves replacing an existing `plan.md` |

---

## Output path

Write to:

```
.bindify/development/<category>/<feature-name>/plans/<plan-name>/plan.md
```

If `plan.md` already exists and `ALLOW_OVERWRITE` is not `true`, create:

```
.bindify/development/<category>/<feature-name>/plans/<plan-name>/plan-v2.md
```

Increment (`plan-v3.md`, `plan-v4.md`, ...) if needed.

---

## Procedure

1. Resolve the feature path
   - Validate `CATEGORY`, `FEATURE_NAME`, and `PLAN_NAME`
   - Ensure output lands in the exact feature directory under `.bindify/development/`
   - If path is ambiguous, stop and ask the human

2. Validate proposal approval
   - Read `PATH_TO_PROPOSAL_MD` fully
   - Confirm `Human review -> Decision` is `approved` or `approved with changes`
   - If decision is missing, `rejected`, or ambiguous, stop and ask

3. Gather plan context
   - Read proposal sections: `Approach`, `Options considered`, `Proposed steps`, `Risks and unknowns`
   - Read `brief.md` when available for goals, constraints, and success criteria

4. Generate the execution plan
   - Convert approved proposal into actionable, ordered steps
   - Each step must include:
     - `Step ID`
     - `Goal`
     - `Inputs/Dependencies`
     - `Implementation Tasks`
     - `Expected Outputs` (repo-relative file paths and/or artifacts)
     - `Done Criteria`
   - Include explicit `Out of Scope` and `Risks/Assumptions` sections

5. Save as markdown
   - Create missing plan folder if needed
   - Save plan to `plan.md` (or versioned fallback file per Output path rules)
   - Keep content plain markdown only

6. Run link maintenance
   - Invoke `update-links` for the current plan folder

---

## Required plan template

```markdown
# Plan: <human-readable plan title>

**Feature:** `.bindify/development/<category>/<feature-name>/`
**Plan Folder:** `plans/<plan-name>/`
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
- If proposal approval state is missing or invalid, stop and ask

---

## Acceptance criteria

- Plan file is saved under the correct feature path in `.bindify/development/<category>/<feature-name>/plans/<plan-name>/`
- Plan reflects approved proposal steps and review adjustments
- Uses ordered, actionable steps with clear outputs and done criteria
- Saved as a `.md` file (`plan.md` or versioned fallback when not overwriting)
- Contains `Scope`, `Out of scope`, and `Risks/Assumptions`
- `update-links` has run for the plan folder
