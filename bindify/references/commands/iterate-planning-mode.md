# Command: iterate-planning-mode

Execute exactly one step from an existing `plan.md` and produce only that step's declared outputs.

When that step is the **last unfinished step**, finish the apply loop: write `verify.md`, push to the **same** draft-PR head branch, and mark **that** draft PR ready for review.

This command is for the **executor** agent (usually draft-PR triggered). The planner that ran `publish-plan` must not run this unless the human explicitly overrides. The reviewer that runs `review-plan` must not run this either.

Draft heads this command may lock:

| Head | After `gh pr ready` |
|---|---|
| `plan/<leaf>` | Stop. A separate reviewer runs `review-plan`. Do not commit again on this branch. |
| `plan-fixes/<leaf>` | Stop. A human reviews this PR. Do not run `review-plan` again. |

---

## Branch lock (non-negotiable)

1. Resolve the draft PR head branch first. Use the PR that triggered this agent when there is one. Otherwise:
   ```bash
   gh pr list --state open --json number,isDraft,headRefName,url \
     --jq '.[] | select(.isDraft==true and ((.headRefName|startswith("plan/")) or (.headRefName|startswith("plan-fixes/"))))'
   ```
   If more than one draft matches, stop and ask. Preferred head = that PR's `headRefName` (`plan/<leaf>` or `plan-fixes/<leaf>` only).
2. Checkout **exactly** that branch. Do not create anything new.
3. **Forbidden for the entire command** (including finish path):
   - `git checkout -b` / `git switch -c`
   - creating `feature/...`, `feat/...`, `fix/...`, `plan-fixes/...`, or any branch that is not the existing draft head
   - opening a second PR with a different head
   - appending or editing steps in `plan.md` (`review-plan` is the only command that appends fix steps)
4. `FEATURE_NAME` / Category `features` in `wip-docs/` are **metadata only** — never git branch names.
5. If you are not on the triggering draft's `plan/...` or `plan-fixes/...` head, stop and ask. Do not invent a branch.
6. Every commit and push in this command goes to **that same branch only**.
7. On `plan-fixes/<leaf>`, refuse a `STEP_ID` that already has an `updates.md` entry. Those steps finished on the plan branch. Run only the appended steps that still lack an entry.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `FEATURE` | yes | Human-readable feature reference |
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` |
| `STEP_ID` | yes | Exact step identifier in `Step-###` format (e.g., `Step-002`) |
| `LIST_OF_EXISTING_MD_FILES` | no | Additional repo-relative context docs |
| `SUMMARISE_FILE` | no | Optional summary file for quick context |
| `MARK_PR_READY` | no | Defaults to `true`. When the plan is complete, mark the **existing draft** PR ready for review |
| `DRAFT_PR` | no | PR number/URL if known (preferred when the agent was triggered by draft-created) |

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

0. **Lock branch** — follow [Branch lock](#branch-lock-non-negotiable). Confirm `git branch --show-current` equals the draft PR `headRefName` and is `plan/<leaf>` or `plan-fixes/<leaf>`.
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
9. **One commit per step** on the **locked draft-PR head branch** (required when there are changes):
   - Confirm still on the same branch before committing
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
   - Push **this same branch** after the commit (`git push origin HEAD`). Never push a differently named branch.
10. **Completion check** — after this step's update is committed, decide whether the plan is finished:
    - List every `Step-###` in `plan.md`
    - Confirm each has a corresponding section in `wip-docs/updates.md`
    - If any step is still missing an updates entry → stop here and report the next `STEP_ID` (draft stays draft)
    - If **all** steps have updates entries → run the [Finish path](#finish-path-plan-complete)

---

## Finish path (plan complete)

Run only when every plan step has an `updates.md` entry. Still on the **same** draft-PR head branch — no new branch.

1. Run `generate-verify` → `wip-docs/verify.md`
2. Commit `wip-docs/verify.md` as its **own** commit (do not fold into the last step commit) with blanche author:
   ```bash
   git commit --author="blanche <blanche@bindify.app>" -m "$(cat <<'EOF'
   docs(plan): add verify checklist for <plan-name>

   EOF
   )"
   ```
3. Push the **same** branch again
4. Resolve the draft PR whose **head is this branch** (`publish-plan` for `plan/<leaf>`, `review-plan` for `plan-fixes/<leaf>`):
   ```bash
   gh pr list --head "$(git branch --show-current)" --json number,isDraft,url,baseRefName,state,headRefName
   ```
5. If `MARK_PR_READY` is `true` (default):
   - **Required:** a draft PR with `headRefName` == current branch must exist → mark **that** draft ready for review:
     ```bash
     gh pr ready <number>
     ```
   - Verify afterward: `gh pr view <number> --json isDraft` → `isDraft` must be `false`
   - If an open non-draft PR already exists for this head → leave it; report the URL
   - If **no** PR exists for this head → stop and ask (do **not** create a new branch). A missing `plan/` draft may be created only with `--head` set to the current `plan/<leaf>` and the known parent/`BASE`. A missing `plan-fixes/` draft belongs to `review-plan` — do not open it here. Never invent `feature/...`
6. Report, then stop committing on this branch:
   - Plan complete, verify path, PR URL, and that this draft was switched to ready for review
   - Head `plan/<leaf>`: a separate reviewer must run `review-plan`. This command does not review and does not open `plan-fixes/`
   - Head `plan-fixes/<leaf>`: human review only. Do not run `review-plan`
7. Do **not** migrate into Bindify here — that remains `publish-bindify-pr` / `log-pr` after the product PR exists

---

## Commit convention (blanche)

All product commits created by this command (step commits + verify commit):

| Rule | Detail |
|---|---|
| Branch | Only the draft PR head (`plan/<leaf>` or `plan-fixes/<leaf>`) — never a new branch |
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
- **Never create any new git branch.** Commit and push only on the draft PR's existing head (`plan/<leaf>` or `plan-fixes/<leaf>`). `FEATURE_NAME` ≠ branch name. Do not create `plan-fixes/` here.
- Finish path must call `gh pr ready` on **that** draft — do not open a different-head PR.
- After `gh pr ready` on `plan/<leaf>`, do not commit on that branch again. Later fix commits belong on `plan-fixes/<leaf>`.

---

## Acceptance criteria

- Current branch stayed the triggering draft head (`plan/<leaf>` or `plan-fixes/<leaf>`) for the whole run
- No `feature/` or `plan-fixes/` branch was created by this command
- Each completed step has its own blanche commit on that branch and was pushed
- On `plan-fixes/`, already-logged steps were not executed again
- On plan completion: `verify.md` committed, same branch pushed, draft PR marked ready (`isDraft: false`)
- Ready `plan/*` handed off to `review-plan`; ready `plan-fixes/*` handed off to a human

---

## Result

After every step:
- [summarize-work-for-updates](./summarize-work-for-updates.md)

After the last step (finish path):
- [generate-verify](./generate-verify.md)
- Same draft PR switched to ready for review (`gh pr ready`)
- `plan/*` ready → [review-plan](./review-plan.md) (separate agent)
- `plan-fixes/*` ready → human only

---

## Related

- `[[references/commands/publish-plan.md]]`
- `[[references/commands/review-plan.md]]`
- `[[references/commands/summarize-work-for-updates.md]]`
- `[[references/commands/generate-verify.md]]`
