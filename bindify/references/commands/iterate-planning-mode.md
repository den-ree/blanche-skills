# Command: iterate-planning-mode

Execute exactly one step from an existing `plan.md` and produce only that step's declared outputs.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `FEATURE` | yes | Human-readable feature reference |
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` |
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

Read `references/docs/working-style.md` first. Chat is caveman. Code comments and `updates.md` stay normal prose.

1. Read `PATH_TO_PLAN_MD` (default `wip-docs/plan.md`) and locate `STEP_ID` exactly
2. Validate required schema exists for that step
3. Check for test failure context:
   - If `test-failure.log` exists at repo root, read it first; compiler/test errors take priority
4. Execute only the tasks listed under that step
   - Read the code the step touches and trace the real flow, then climb the ponytail ladder inside the step: existing code, stdlib, native platform, installed dependency, one line, then the minimum that works.
   - Do not add files, abstractions, or dependencies the step does not need.
   - A bugfix lands at the root cause, once, where callers already route.
   - Mark a deliberate ceiling with a `ponytail:` comment naming the ceiling and the upgrade path.
   - Never cut trust-boundary validation, data-loss handling, security, accessibility, or anything the step explicitly requires.
5. Produce only outputs listed in that step's `Expected Outputs`
6. Validate completion against that step's `Done Criteria`
7. Do not execute or prepare adjacent steps

---

## Prototype Steps (Prototype-First Mode)

When `STEP_ID` is designated as a Prototype (commonly `Step-001` for UI features):
- **Stub only:** Use inline mock datasets, static state, or stub repositories.
- **Out of scope:** No backend networking, DB migrations, persistence, or complex edge handling.
- **Goal:** Unblock visual and interaction review by providing a complete, clickable end-to-end user journey.
- **Done Criteria:** The full workflow can be navigated from start to finish in UI or preview canvas.

For dedicated prototype-only runs, see also `prototype-mode`.

---

## Cloud / Remote Execution Guardrails

When executing on a Linux cloud agent (e.g. Cursor Cloud Agents) in a macOS/Apple-targeted project:
- **No macOS CLI tools:** Do NOT attempt `xcodebuild`, `xcrun simctl`, or Simulator launching in Linux containers.
- **Source verification:** Verify types, imports, and syntax statically without running platform-native toolchains.
- **Failure resolution:** If fixing a prior run indicated by `test-failure.log`, resolve all reported errors and remove `test-failure.log` before completing.

---

## Rules

- Execute **ONLY** the specified step
- Do **NOT** modify other steps in `plan.md`
- Do **NOT** introduce new scope beyond the step
- Append execution evidence to `wip-docs/updates.md` via `summarize-work-for-updates` — not into the Bindify submodule
- If required inputs are missing, explicitly state what is missing and stop
- If expected outputs are ambiguous, stop and ask for clarification
- Do not "improve" neighboring code while executing the step
- If Done Criteria involve running or verifying the app, consult `.bindify/project/environment.md` (or `bindify/project/environment.md`) for start/test/lint/build commands when that file exists; do not guess

---

## Result

After execution, summarize work using:
- [summarize-work-for-updates](./summarize-work-for-updates.md)
