# Command: save-agent-plan

Generate and save a planning-mode plan from agent discussion outputs into the correct Bindify feature path.

---

## When to use

- A planning discussion (human + agent, or multi-agent) is complete
- The human wants the discussed approach captured as an executable plan file
- A plan needs to be stored under the feature's `plans/` directory as a `.md` file

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` |
| `FEATURE_NAME` | yes | Feature folder name in kebab-case |
| `PLAN_NAME` | yes | Plan folder name in kebab-case |
| `DISCUSSION_SOURCES` | yes | Planning context sources (conversation + agent planning outputs) |
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

2. Gather planning context
   - Read all `DISCUSSION_SOURCES`
   - Include both human intent and agent planning proposals
   - Extract only decisions that were actually discussed

3. Build the discussion summary section
   - Capture: problem framing, alternatives discussed, final approach, constraints, explicit trade-offs
   - Keep concise (2-6 bullets)
   - Do not include transcript-like raw chat

4. Generate the execution plan
   - Convert approved discussion into actionable, ordered steps
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

---

## Required plan template

```markdown
# Plan: <human-readable plan title>

**Feature:** `.bindify/development/<category>/<feature-name>/`
**Plan Folder:** `plans/<plan-name>/`
**Generated From:** planning-mode discussion (human + agents)
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
```

---

## Guardrails

- Use repo-relative paths only
- Do not invent decisions not present in planning discussion
- Do not include source code in `plan.md`
- Do not execute implementation work in this command
- Do not modify `updates.md` or `verify.md`
- If required planning context is missing, stop and ask

---

## Acceptance criteria

- Plan file is saved under the correct feature path in `.bindify/development/<category>/<feature-name>/plans/<plan-name>/`
- Includes a concise discussion summary explaining why the plan exists
- Uses ordered, actionable steps with clear outputs and done criteria
- Saved as a `.md` file (`plan.md` or versioned fallback when not overwriting)
- Contains `Scope`, `Out of scope`, and `Risks/Assumptions`
