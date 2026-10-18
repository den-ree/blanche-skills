# Command: review-plan

Review a plan PR that `iterate-planning-mode` just marked ready. Schedule another implementation round only for misses against the approved plan.

This command is for the **reviewer** agent (usually a ready-for-review trigger on `plan/<leaf>` or `plan-iteration-N/<leaf>`). It does not implement code. The planner stays out of implementation. The executor picks up fix steps only after this command opens a draft.

One automatic round. `ready_for_review` on `plan-fixes/*` does not run this command again.

---

## When to use

- `iterate-planning-mode` has finished the original plan and switched that draft to ready (`gh pr ready`)
- The open PR head is `plan/<leaf>` or `plan-iteration-N/<leaf>` (not `plan-fixes/…`)
- A human or automation asks to review the finished plan before sign-off

Do **not** use this command when:

- The PR head is `plan-fixes/*` — that ready PR is for a human
- The plan PR is still a draft — the executor has not finished
- The miss is new scope (improvement, refactor, extra edge case). Comment it; do not schedule it

In-scope misses on an open plan PR are **not** `log-hotfix`. Hotfix logs are for unplanned fixes outside this review round, written into the tracking repo later.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `REVIEW_PR` | no | Plan PR number or URL. Defaults to the PR that triggered this agent |
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` on the plan branch |
| `PATH_TO_BRIEF_MD` | no | Defaults to `wip-docs/brief.md` |
| `PATH_TO_UPDATES_MD` | no | Defaults to `wip-docs/updates.md` |
| `PATH_TO_VERIFY_MD` | no | Defaults to `wip-docs/verify.md` |

---

## Branch names

| Branch | Who creates it | PR |
|---|---|---|
| `feature/<feature-slug>` | `publish-plan`, from `main` or `release/*` only | No PR in `publish-plan`. It is the base of `plan/<leaf>` |
| `plan/<leaf>` | `publish-plan` | Draft PR **into** `feature/<feature-slug>` |
| `plan-iteration-N/<leaf>` | `publish-plan`, only when the previous head already has a PR | Draft PR **into** the previous plan or iteration branch |
| `plan-fixes/<leaf>` | **this command**, when the reviewed head is `plan/<leaf>` | Draft PR **into** `plan/<leaf>` |
| `plan-fixes/iteration-N-<leaf>` | **this command**, when the reviewed head is `plan-iteration-N/<leaf>` | Draft PR **into** `plan-iteration-N/<leaf>` |

`<leaf>` is the last path segment (`plan/onboarding-flow` and `plan-iteration-1/onboarding-flow` both use leaf `onboarding-flow`). Do not invent a new slug. The fixes PR base is the reviewed head. Never open it into `feature/*`, `main`, or `release/*`.

---

## What counts as a fix step

A finding becomes a new plan step only when the diff misses the **approved** scope. At least one of these is true:

- A `Done Criteria` item on an existing step is unmet
- A `brief.md` success criterion is unmet
- Required behavior from the plan is missing, wrong, or regressed
- An `Expected Outputs` path or behavior from the plan is absent or incorrect

These do **not** become steps. Put them in the plan PR comment under `Noted, not scheduled`:

- Style, naming, or structure preferences
- Refactors, extra abstractions, or "while we're here" cleanup
- New behavior, extra edge cases, or work listed as out of scope
- Dependency bumps or architecture improvements the plan did not require

---

## Procedure

Read `references/docs/working-style.md` first. Chat is caveman. `plan.md`, the commit message, and the PR body stay normal prose.

1. Resolve the plan PR
   - Read `REVIEW_PR`, or the PR that triggered this agent:
     ```bash
     gh pr view <number> --json number,isDraft,state,url,headRefName,baseRefName
     ```
   - Continue only when `state` is `OPEN`, `isDraft` is `false`, and `headRefName` is `plan/<leaf>` or `plan-iteration-N/<leaf>` (`plan/` is a prefix followed by a single segment; `plan-iteration-` does not match `plan/`).
   - If `headRefName` starts with `plan-fixes/`, stop. Comment that this ready PR is for a human. Do not append steps and do not open another draft.
   - If the PR is still a draft, stop and leave it for the executor.

2. Spend the round at most once
   - Reviewed head = `headRefName`
   - If the head is `plan/<leaf>`, fixes head = `plan-fixes/<leaf>`
   - If the head is `plan-iteration-N/<leaf>`, fixes head = `plan-fixes/iteration-N-<leaf>`
   - Fixes PR base = the reviewed head, not `feature/*`, `main`, or `release/*`
   - ```bash
     gh pr list --head "<fixes-head>" --state all --json number,state,url
     ```
   - If any PR exists (open, merged, or closed), comment on the plan PR that the automatic review round is already used, then stop. Do not append more steps.

3. Review against the approved plan
   - Check out the reviewed head at the PR head. Do not commit on this branch.
   - Read `brief.md`, `plan.md`, `updates.md`, and `verify.md`
   - Read the PR diff (`gh pr diff <number>`)
   - Split findings into **fix steps** and **noted, not scheduled** using the bar above
   - Do not edit existing `Step-###` sections. Completed steps stay as written.

4. Clean review
   - If there are no fix-step findings, comment on the plan PR:
     - Result: no in-scope misses
     - `Noted, not scheduled`: improvement list, or "none"
   - Do not create a branch. Do not open a PR. Stop. The human reviews the open plan PR.

5. Append fix steps on the fixes branch
   - Fetch and branch from the reviewed head tip (the open PR head):
     ```bash
     git fetch origin
     git checkout "<reviewed-head>"
     git pull --ff-only origin "<reviewed-head>"
     ```
   - If the fixes head already exists locally or on `origin`, check it out. Otherwise:
     ```bash
     git checkout -b "<fixes-head>"
     ```
   - Do not reset or force-push the fixes branch.
   - If that branch already contains `**Origin:** review-plan` steps that are not on the reviewed head, do not append those defects again. Open the draft if it is still missing, then stop.
   - On the fixes head only, append new steps at the end of `## Execution Steps` (before `## Related` when that section exists).
   - Number from the next free `Step-###`. Never renumber or rewrite earlier steps.
   - One step per distinct defect. Each step is the minimum fix and must include `Goal`, `Inputs/Dependencies`, `Implementation Tasks`, `Expected Outputs`, and `Done Criteria`.
   - `Goal` names the missed criterion. `Inputs/Dependencies` cites the plan step or brief criterion it repairs.
   - Add `**Origin:** review-plan` on each new step.
   - Do not edit `updates.md` or `verify.md` here. The executor writes those while implementing the new steps.
   - Run `update-links` for `wip-docs/`.

6. Commit and push the fixes branch
   - Stage the `plan.md` append only (plus link updates inside `wip-docs/` if `update-links` changed them)
   - Author is blanche. Never change git config:
     ```bash
     git commit --author="blanche <blanche@bindify.app>" -m "$(cat <<'EOF'
     docs(plan): append review fixes for <leaf>

     EOF
     )"
     ```
   - `git push -u origin HEAD`

7. Open one draft into the reviewed head
   - Base is the reviewed head (`plan/<leaf>` or `plan-iteration-N/<leaf>`). Head is the fixes branch from step 2.
   - If that draft already exists, report its URL and stop.
   - ```bash
     gh pr create --draft --base "<reviewed-head>" --head "<fixes-head>" \
       --title "Plan fixes: <leaf>" \
       --body "$(cat <<'EOF'
     ## Plan fixes
     - Plan: <leaf>
     - Base: `<reviewed-head>`
     - Source PR: <plan PR url>
     - Automatic review round: 1 of 1

     ## Fix steps
     - <Step-### — title, one per new step>

     ## Status
     Draft — executor runs iterate-planning-mode on these new steps only.

     ## Notes
     - Do not edit earlier steps.
     - Mark ready when every new step has an updates entry.
     - ready_for_review on this PR does not start another review-plan.
     EOF
     )"
     ```
   - Also comment on the **plan** PR: link the fixes draft, list the scheduled steps, and list `Noted, not scheduled`.

8. Refresh the same in-progress history card
   - Reuse the existing history entry for this plan/outcome slug. Do **not** create a second card.
   - Run `generate-history-summary` in `MODE=in-progress` with `PR_REF` set to the **fixes** draft PR URL, keeping `status: in-progress`.
   - Rebuild `history/index.md` so the item stays under **In progress** with the updated PR chip.
   - Tracking writes are limited to `history/` (same exception as `publish-plan`). Do not touch `development/` and do not bump the product submodule pointer.
   - If tracking is missing, report that the history refresh was skipped.

9. Stop
   - Do not run `iterate-planning-mode`
   - Do not mark the fixes draft ready
   - Do not commit anything else on the reviewed head

---

## Appended step shape

```markdown
### Step-004: Fix <short defect>
**Origin:** review-plan
**Goal:** <which done criterion or brief success criterion is unmet>
**Inputs/Dependencies:** <existing Step-### or brief criterion, plus repo-relative paths>
**Implementation Tasks:**
- <minimum change that makes that criterion true>
**Expected Outputs:**
- `<repo-relative-path>`
**Done Criteria:**
- <observable condition copied from the missed criterion>
```

---

## Guardrails

- Only `review-plan` may create a `plan-fixes/` branch
- Never create `feature/...` or `plan-iteration-N/...` here, and never open the fixes PR into `feature/*`, `main`, or `release/*`
- Never edit completed steps, `updates.md`, or `verify.md` in this command
- Never implement the fix in this command
- Never start a second automatic round
- Never schedule improvements as steps
- Do not write `hotfixes.md` or anything under tracking `development/`
- Tracking exception: may refresh the same history card under tracking `history/` after the fixes draft URL exists
- After the plan PR is open, leave the reviewed head frozen so the fixes append merges cleanly
- Use repo-relative paths only. No source code in `plan.md`

---

## Acceptance criteria

- Plan PR stayed open and gained no new commits from this command
- Improvements are comments, not steps
- Either:
  - no fixes branch and a clean-review comment on the plan PR, or
  - the fixes branch exists (`plan-fixes/<leaf>` or `plan-fixes/iteration-N-<leaf>`), contains only appended steps, and has one draft PR whose base is the reviewed head
- Existing `Step-###` sections are unchanged
- No second `plan-fixes/` PR was opened when one already existed for that leaf
- When a fixes draft was opened and tracking is present, the existing history card stayed one file, `status: in-progress`, with `pr` updated to the fixes draft URL

---

## Related

- `[[references/commands/iterate-planning-mode.md]]`
- `[[references/commands/publish-plan.md]]`
- `[[references/commands/generate-history-summary.md]]`
- `[[references/commands/generate-verify.md]]`
- `[[references/commands/log-hotfix.md]]`
