# Command: iterate-planning-mode

Execute exactly one step from an existing `plan.md` and produce only that step's declared outputs.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `FEATURE` | yes | Human-readable feature reference |
| `PATH_TO_PLAN_MD` | yes | Repo-relative path to `plan.md` |
| `STEP_ID` | yes | Exact step identifier in `Step-###` format (e.g., `Step-002`) |
| `LIST_OF_EXISTING_MD_FILES` | no | Additional repo-relative context docs |
| `SUMMARISE_FILE` | no | Optional summary file for quick context |

---

## Required plan step schema

The target step in `plan.md` must include all of:

- `Goal`
- `Inputs/Dependencies`
- `Implementation Tasks`
- `Expected Outputs`
- `Done Criteria`

If any required section is missing for `STEP_ID`, stop and report the missing section names.

---

## Procedure

1. Read `PATH_TO_PLAN_MD` and locate `STEP_ID` exactly
2. Validate required schema exists for that step
3. Execute only the tasks listed under that step
4. Produce only outputs listed in that step's `Expected Outputs`
5. Validate completion against that step's `Done Criteria`
6. Do not execute or prepare adjacent steps

---

## Rules

- Execute **ONLY** the specified step
- Do **NOT** modify other steps in `plan.md`
- Do **NOT** introduce new scope beyond the step
- If required inputs are missing, explicitly state what is missing and stop
- If expected outputs are ambiguous, stop and ask for clarification

---

## Result

After execution, summarize work using:
- [summarize-work-for-updates](./summarize-work-for-updates.md)