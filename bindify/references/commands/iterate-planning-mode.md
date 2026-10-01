# Command: iterate-planning-mode

Execute exactly one step from an existing `plan.md` and produce only that step's declared outputs.

When that step is the **last unfinished step**, finish the apply loop: write `verify.md`, push, and mark the product PR **ready for review** (converting the draft opened by `publish-plan`).

## Branch hard rule

- Work **only** on the current `plan/<plan-name>` branch.
- **Never** create `feature/...`, `feat/...`, or any other new branch from `plan/...`.
- **Never** run `git checkout -b` / `git switch -c` during this command.
- `FEATURE_NAME` in `wip-docs/` headers is **metadata only** (migration path) — it is **not** a git branch name.
- If not already on `plan/...`, stop and ask. Do not invent a branch.
---

## Inputs

| Input | Required | Description |
|---|---|---|
| `FEATURE` | yes | Human-readable feature reference |
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` |
| `STEP_ID` | yes | Exact step identifier in `Step-###` format (e.g., `Step-002`) |
| `LIST_OF_EXISTING_MD_FILES` | no | Additional repo-relative context docs |
| `SUMMARISE_FILE` | no | Optional summary file for quick context |
| `MARK_PR_READY` | no | Defaults to `true`. When the plan is complete, mark the draft PR ready for review |

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
8. Append evidence via `summarize-work-for-updates` → `wip-docs/updates.md`
9. **One commit per step** on the current `plan/...` branch (required when there are changes):
   - Stage only this step's code outputs + the new `wip-docs/updates.md` entry (and any step-local docs)
   - Do **not** squash multiple steps into one commit
   - Do **not** leave step work uncommitted
   - Author must be blanche (per-commit override; never change global git config):
     ```bash
     git commit --author="blanche <blanche@bindify.app>" -m "$(cat <<'EOF'
     feat(plan): <STEP_ID> — <short step title>

     EOF
     )"
     ```
   - Push the branch after the commit
10. **Completion check** — after this step's update is committed, decide whether the plan is finished:
    - List every `Step-###` in `plan.md`
    - Confirm each has a corresponding section in `wip-docs/updates.md`
    - If any step is still missing an updates entry → stop here and report the next `STEP_ID`
    - If **all** steps have updates entries → run the [Finish path](#finish-path-plan-complete)

---

## Finish path (plan complete)

Run only when every plan step has an `updates.md` entry:

1. Run `generate-verify` → `wip-docs/verify.md`
2. Commit `wip-docs/verify.md` as its **own** commit (do not fold into the last step commit) with blanche author:
   ```bash
   git commit --author="blanche <blanche@bindify.app>" -m "$(cat <<'EOF'
   docs(plan): add verify checklist for <plan-name>

   EOF
   )"
   ```
3. Push the branch
4. Resolve the product PR for this head branch:
   ```bash
   gh pr list --head <current-branch> --json number,isDraft,url,baseRefName,state
   ```
5. If `MARK_PR_READY` is `true` (default):
   - If a **draft** PR exists → mark it ready for review:
     ```bash
     gh pr ready <number>
     ```
   - If an open non-draft PR already exists → leave it; report the URL
   - If **no** PR exists → create a **ready-for-review** PR into the parent/`BASE` (infer from branch history or ask; do not invent `feature/...`):
     ```bash
     gh pr create --base <BASE> --head <current-branch> \
       --title "Plan: <plan-name>" \
       --body "<summary + link to wip-docs/plan.md + wip-docs/verify.md>"
     ```
6. Report: plan complete, verify path, PR URL, and that human review can start
7. Do **not** migrate into Bindify here — that remains `publish-bindify-pr` / `log-pr` after the product PR exists

---

## Commit convention (blanche)

All product commits created by this command (step commits + verify commit):

| Rule | Detail |
|---|---|
| Granularity | Exactly **one git commit per `STEP_ID`** |
| Author | `--author="blanche <blanche@bindify.app>"` |
| Config | Never run `git config` to change user.name / user.email |
| Message | `feat(plan): Step-00N — <short title from plan.md>` |
| Scope | Only that step's files + its `updates.md` append |

`publish-plan`'s initial `wip-docs` publish commit also uses the same blanche author.
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

- Execute **ONLY** the specified step (except the finish path after the last step's evidence is written)
- Do **NOT** modify other steps in `plan.md`
- Do **NOT** introduce new scope beyond the step
- Append execution evidence to `wip-docs/updates.md` via `summarize-work-for-updates` — not into the Bindify submodule
- If required inputs are missing, explicitly state what is missing and stop
- If expected outputs are ambiguous, stop and ask for clarification
- Do not "improve" neighboring code while executing the step
- If Done Criteria involve running or verifying the app, consult `.bindify/project/environment.md` (or `bindify/project/environment.md`) for start/test/lint/build commands when that file exists; do not guess
- Mid-plan: leave the publish-plan **draft** PR as draft. Only mark ready when the finish path runs.
- One commit per step; author is always blanche via `--author` (never change git config)
- Do not combine multiple steps, or step work + verify, into a single commit
- **Never create a `feature/` (or any non-`plan/`) branch.** Stay on the existing `plan/` head. `FEATURE_NAME` ≠ branch name.

---

## Result

After every step:
- [summarize-work-for-updates](./summarize-work-for-updates.md)

After the last step (finish path):
- [generate-verify](./generate-verify.md)
- Product PR ready for review (`gh pr ready` or create non-draft PR)

---

## Related

- `[[references/commands/publish-plan.md]]`
- `[[references/commands/summarize-work-for-updates.md]]`
- `[[references/commands/generate-verify.md]]`
