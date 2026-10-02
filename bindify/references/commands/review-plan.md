# Command: review-plan

Review a plan PR that `iterate-planning-mode` just marked ready. Schedule another implementation round only for misses against the approved plan.

This command is for the **reviewer** agent (usually a ready-for-review trigger on `plan/*`). It does not implement code. The planner stays out of implementation. The executor picks up fix steps only after this command opens a draft.

One automatic round. `ready_for_review` on `plan-fixes/*` does not run this command again.

---

## When to use

- `iterate-planning-mode` has finished the original plan and switched that draft to ready (`gh pr ready`)
- The open PR head is `plan/<leaf>` (not `plan-fixes/<leaf>`)
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
| `plan/<leaf>` | `publish-plan` | Open PR into the parent (`main`, `release/*`, `feature/*`, …) |
| `plan-fixes/<leaf>` | **this command only** | Draft PR **into** `plan/<leaf>` |

`<leaf>` is the plan branch with the `plan/` prefix removed. `plan/onboarding-flow` → `plan-fixes/onboarding-flow`. Reuse that leaf. Do not invent a new slug. Do not open the fixes PR into `main` or `release/*`.

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
   - Continue only when `state` is `OPEN`, `isDraft` is `false`, and `headRefName` starts with `plan/`.
   - If `headRefName` starts with `plan-fixes/`, stop. Comment that this ready PR is for a human. Do not append steps and do not open another draft.
   - If the PR is still a draft, stop and leave it for the executor.

2. Spend the round at most once
   - `<leaf>` = `headRefName` with the `plan/` prefix removed
   - Fixes head = `plan-fixes/<leaf>`
   - ```bash
     gh pr list --head "plan-fixes/<leaf>" --state all --json number,state,url
     ```
   - If any PR exists (open, merged, or closed), comment on the plan PR that the automatic review round is already used, then stop. Do not append more steps.

3. Review against the approved plan
   - Check out `plan/<leaf>` at the PR head. Do not commit on this branch.
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
   - Fetch and branch from the current `plan/<leaf>` tip (the open PR head):
     ```bash
     git fetch origin
     git checkout "plan/<leaf>"
     git pull --ff-only origin "plan/<leaf>"
     ```
   - If `plan-fixes/<leaf>` already exists locally or on `origin`, check it out. Otherwise:
     ```bash
     git checkout -b "plan-fixes/<leaf>"
     ```
   - Do not reset or force-push the fixes branch.
   - If that branch already contains `**Origin:** review-plan` steps that are not on `plan/<leaf>`, do not append those defects again. Open the draft if it is still missing, then stop.
   - On `plan-fixes/<leaf>` only, append new steps at the end of `## Execution Steps` (before `## Related` when that section exists).
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

7. Open one draft into the plan branch
   - Base is `plan/<leaf>`. Head is `plan-fixes/<leaf>`.
   - If that draft already exists, report its URL and stop.
   - ```bash
     gh pr create --draft --base "plan/<leaf>" --head "plan-fixes/<leaf>" \
       --title "Plan fixes: <leaf>" \
       --body "$(cat <<'EOF'
     ## Plan fixes
     - Plan: <leaf>
     - Base: `plan/<leaf>`
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

8. Stop
   - Do not run `iterate-planning-mode`
   - Do not mark the fixes draft ready
   - Do not commit anything else on `plan/<leaf>`

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

- Only `review-plan` may create `plan-fixes/<leaf>`
- Never create `feature/...`, and never open the fixes PR into the parent of `plan/<leaf>`
- Never edit completed steps, `updates.md`, or `verify.md` in this command
- Never implement the fix in this command
- Never start a second automatic round
- Never schedule improvements as steps
- Do not write `hotfixes.md` or anything under `.bindify/` / `bindify/`
- After the plan PR is open, leave `plan/<leaf>` frozen so the fixes append merges cleanly
- Use repo-relative paths only. No source code in `plan.md`

---

## Acceptance criteria

- Plan PR stayed open and gained no new commits from this command
- Improvements are comments, not steps
- Either:
  - no fixes branch and a clean-review comment on the plan PR, or
  - `plan-fixes/<leaf>` exists, contains only appended steps, and has one draft PR whose base is `plan/<leaf>`
- Existing `Step-###` sections are unchanged
- No second `plan-fixes/` PR was opened when one already existed for that leaf

---

## Related

- `[[references/commands/iterate-planning-mode.md]]`
- `[[references/commands/publish-plan.md]]`
- `[[references/commands/generate-verify.md]]`
- `[[references/commands/log-hotfix.md]]`
