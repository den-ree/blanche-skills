# Command: publish-plan

Kick off execution on the **product** repo: put approved `wip-docs/` on a per-plan product branch, push it, and open a **draft** pull request so draft-created automations can start a **separate executor agent**.

The agent that runs `publish-plan` is the **planner**. It must **not** implement the plan. It waits until the draft PR is marked ready for review (executor finished). Durable Bindify migration still happens later via `publish-bindify-pr` / `log-pr`.

---

## When to use

- The human says `/bindify` or asks to publish the plan
- `wip-docs/plan.md` is ready and tied to an approved proposal
- Ready to start `iterate-planning-mode` on a persistent product branch (often via a draft-PR trigger)

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | no | Infer from `wip-docs/brief.md` / `plan.md` header when omitted |
| `FEATURE_NAME` | no | Infer from WIP headers when omitted |
| `PLAN_NAME` | no | Infer from WIP headers when omitted |
| `PATH_TO_PROPOSAL_MD` | no | Defaults to `wip-docs/proposal.md` |
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` |
| `BRANCH_NAME` | no | Implementation head. Leave empty and follow the branch stack. Set only when the human names an exact head (`plan/<plan-name>` or `plan-iteration-N/<plan-name>`) |
| `BASE` | no | PR base. Leave empty and follow the branch stack. Set only when the human names the exact base (`feature/<feature-name>`, `plan/<plan-name>`, or `plan-iteration-N/<plan-name>`). Do not default this to `main` or `release/*` |
| `ALLOW_OVERWRITE` | no | `true` only with explicit human approval if an existing `plan/` branch would be reset |
| `DRAFT_PR` | no | Defaults to `true`. When `true`, ensure a draft PR exists from the plan branch into `BASE` |
| `PR_TITLE` | no | Defaults to `Plan: <plan-name>` (or feature + plan from WIP headers) |

---

## Branch stack (read this)

`publish-plan` does **not** open the implementation PR into `main` or `release/*`. Read `git branch --show-current` and apply one row. Slugs come from WIP headers (`Feature` → feature slug, `Plan` → plan slug), kebab-case.

| Current branch | What to create | Draft PR |
|---|---|---|
| `main`, `master`, `release`, or `release/*` | `feature/<feature-slug>` from that branch, then `plan/<plan-slug>` from the feature branch | `plan/<plan-slug>` → `feature/<feature-slug>` |
| `feature/*` | `plan/<plan-slug>` from that feature branch. Do not create another `feature/` | `plan/<plan-slug>` → current `feature/*` |
| `plan/<leaf>` that **already has a PR**, same plan | `plan-iteration-1/<leaf>`, or the next free `plan-iteration-N/<leaf>` | iteration → `plan/<leaf>` |
| `plan-iteration-N/<leaf>` that **already has a PR**, same plan | `plan-iteration-(N+1)/<leaf>` | new head → current iteration branch |
| `plan/<leaf>` or `plan-iteration-N/<leaf>` with **no PR yet**, same plan | Nothing new. Stay on it | into its parent (feature branch, or the previous iteration) |
| anything else (`develop`, `hotfix/*`, `plan-fixes/*`, a different plan's branch) | Stop and ask | — |

```
main  or  release/*
└── feature/onboarding                         ← pushed, no PR in this command
    └── plan/welcome-screen                    ← draft PR into feature/onboarding
        └── plan-iteration-1/welcome-screen    ← only after plan/welcome-screen already has a PR
            └── plan-iteration-2/welcome-screen
```

`Feature:` is the `feature/<feature-slug>` branch. `Plan:` is the leaf under `plan/` and `plan-iteration-N/`. `Category:` is not a branch. Creating `feature/` from a `plan/` branch is a bug. Opening `plan/` straight into `main` or `release/*` is a bug.

---

## Procedure

1. Validate prerequisites
   - Confirm `PATH_TO_PLAN_MD` exists (default `wip-docs/plan.md`)
   - Confirm `PATH_TO_PROPOSAL_MD` exists (default `wip-docs/proposal.md`)
   - Confirm proposal `Human review → Decision` is `approved` or `approved with changes`
   - Resolve `CATEGORY` / `FEATURE_NAME` / `PLAN_NAME` from inputs or WIP headers
   - Run `update-links` for `wip-docs/` if links look stale

2. Resolve the implementation head and its PR base
   - Detect current branch: `git branch --show-current`
   - Feature branch = `feature/<feature-slug>`. Plan leaf = `<plan-slug>`.
   - If the human set **both** `BRANCH_NAME` and `BASE`, use those. Still refuse a base of `main`, `master`, `release`, or `release/*` unless the human explicitly said that base. Then skip the stack and continue at the commit step.
   - Do **not** commit `wip-docs/` until the implementation head is checked out. Creating `feature/` or the next iteration happens first, so the parent does not receive the WIP commit.
   - **Current branch is `main`, `master`, `release`, or `release/*`:**
     - If `feature/<feature-slug>` exists locally or on `origin`, check it out. Do not reset it and do not recreate it from the long-lived branch.
     - Otherwise: `git checkout -b feature/<feature-slug>` from the current branch, then `git push -u origin feature/<feature-slug>`.
     - Do not commit on the feature branch. Do not open a feature → `main`/`release` PR.
     - If `plan/<plan-slug>` exists locally or on `origin`, check it out. Otherwise: `git checkout -b plan/<plan-slug>` from the feature tip.
     - `BASE` = `feature/<feature-slug>`. Implementation head = `plan/<plan-slug>`.
   - **Current branch is `feature/*`:**
     - Do not create another feature branch. `BASE` = the current feature branch.
     - If `plan/<plan-slug>` exists, check it out. Otherwise create it from this feature tip.
     - Push the feature branch if it is not on `origin` yet.
   - **Current branch is `plan/<leaf>` or `plan-iteration-N/<leaf>`, and `<leaf>` is this plan:**
     - Look for an existing PR: `gh pr list --head <current> --json number,url,baseRefName`.
     - **No PR yet:** stay. This is a retry, not an iteration. If the head is `plan/<leaf>`, `BASE` = `feature/<feature-slug>` (stop and ask if that feature branch does not exist — do not default to `main`). If the head is `plan-iteration-N/<leaf>`, `BASE` is the previous branch in the stack (`plan/<leaf>` when N is 1, otherwise `plan-iteration-(N-1)/<leaf>`).
     - **PR already exists:** do not commit more planning work on this head. Create the next iteration from the current tip, then check it out before any commit. First name is `plan-iteration-1/<leaf>`. If that name exists locally or on `origin`, use the next free N. `BASE` = the branch you were on. Implementation head = the new iteration branch.
   - **Current branch is some other `plan/*` or `plan-iteration-*` (different leaf):**
     - Do not create `plan-iteration-*` for this leaf, and do not branch `plan/<plan-slug>` off the current plan branch.
     - Check out existing `feature/<feature-slug>` and create or reuse `plan/<plan-slug>` from it. `BASE` = that feature branch.
     - If `feature/<feature-slug>` does not exist, stop and ask. Never create `feature/` from a `plan/` branch.
   - **Any other current branch:** stop and ask. Do not invent a base.
   - Push `feature/<feature-slug>` before opening the plan PR whenever that branch is the base, so the remote ref exists.

3. Stage active WIP on the implementation branch
   - Ensure these exist under `wip-docs/` when present: `brief.md`, `proposal.md`, `plan.md` (and any `plan-v*.md`), `coordinator.md`
   - Do **not** create `updates.md` / `verify.md` here unless they already exist
   - Do **not** write into tracking `development/` (history card comes after the draft PR URL exists)

4. Commit and push (product repo)
   - Stage `wip-docs/` (and only related product files the human already asked to include)
   - Commit with blanche author (do not change git config):
     ```bash
     git commit --author="blanche <blanche@bindify.app>" -m "$(cat <<'EOF'
     feat(plan): publish <plan-name> wip-docs

     EOF
     )"
     ```
   - Skip commit if nothing changed
   - Push the implementation head (`plan/<plan-slug>` or `plan-iteration-N/<plan-slug>`) to remote (`-u` when first publishing)
   - If `BASE` is `feature/<feature-slug>`, push that feature branch too if it is not already on the remote
   - Do not push `main` or `release/*`

5. Ensure draft pull request (`DRAFT_PR` default `true`)
   - PR base = `BASE` from the branch stack. Never substitute `main` or `release/*` when the stack says `feature/*`, `plan/*`, or `plan-iteration-*`.
   - Check for an existing PR from the implementation head:
     ```bash
     gh pr list --head <implementation-head> --json number,isDraft,url,baseRefName
     ```
   - If a PR already exists:
     - Reuse it. If it is not a draft and work has not started review yet, leave it as-is unless the human asks to convert.
     - Report the existing URL (draught or open).
   - If no PR exists, create a **draft**:
     ```bash
     gh pr create --draft --base <BASE> --head <implementation-head> \
       --title "<PR_TITLE>" \
       --body "$(cat <<'EOF'
     ## Plan
     - Feature: <feature-name>
     - Plan: <plan-name>
     - Plan file: `wip-docs/plan.md`

     ## Status
     Draft — ready for executor agents via iterate-planning-mode.

     ## Notes
     - Active docs live in `wip-docs/` on this branch.
     - Mark ready for review only after all plan steps complete (iterate-planning-mode finish path).
     EOF
     )"
     ```
   - If `gh` is unavailable, push the branch and report the compare URL for manual draft PR creation; stop and say draft automation will not fire until a draft PR exists.
   - Report the draft PR URL prominently — this is the handoff signal for draft-created agent triggers.

6. Upsert the in-progress history card (tracking `history/` only)
   - After a draft PR URL exists, resolve the Bindify tracking root (`.bindify/` then `bindify/`).
   - If the tracking checkout is missing, still keep the product draft PR and report that the history card was skipped — do not fail the publish.
   - When tracking is present, run `generate-history-summary` in `MODE=in-progress` with:
     - `PATH_TO_BRIEF_MD` = `wip-docs/brief.md`
     - `PATH_TO_PLAN_MD` = `wip-docs/plan.md`
     - `PR_REF` = the draft PR URL
     - `FEATURE_NAME` / `ENTRY_SLUG` from WIP headers
     - `AGENT` = `blanche` (or the working agent label when known)
   - That write may only touch tracking `history/entries/` and `history/index.md`. Do **not** touch `development/`, architecture, or other tracking trees.
   - Body = intended outcome from the brief. `plan` / `updates` properties point at the WIP plan (and updates when it exists). Topic tag from the feature name.
   - Commit and push the history changes on tracking `main` (or the tracking default branch). Do **not** bump the product submodule pointer for this history-only commit.
   - Rebuild the overview via the history-summary index step so the card appears under **In progress**.

7. Return handoff context — then **STOP**
   - Report implementation head, `BASE`, and whether `feature/`, `plan/`, or `plan-iteration-N/` was created or reused
   - Report **draft PR URL** (or existing PR URL)
   - Report whether the in-progress history card was written / skipped
   - Report `wip-docs/plan.md` as the path the **executor** agent will use
   - Tell the human: draft is published; a different agent should implement via `iterate-planning-mode`
   - Remind: Bindify `development/` migration is deferred to `publish-bindify-pr` after the product PR is ready/merged; live work may already appear in tracking `history/`

8. Planner wait gate (mandatory for the agent that ran `publish-plan`)
   - **Do not** run `iterate-planning-mode`, edit product code, or mark the PR ready yourself.
   - Implementation belongs to a **separate executor agent** triggered by the draft PR (or explicitly started by the human).
   - Stay idle on this workstream until the draft becomes a **ready-for-review / open** PR (`isDraft: false`), which the executor does at the end of the last step.
   - Poll or wait for that transition, e.g.:
     ```bash
     gh pr view <number> --json isDraft,state,url,headRefName
     ```
     Continue only when `isDraft` is `false` and `state` is `OPEN` (ready for review).
   - That ready transition starts **`review-plan`** (a separate reviewer), not the planner. Do not implement, do not append fix steps, and do not create `plan-fixes/`.
   - Stay idle again until the review round settles:
     - `review-plan` reports no in-scope misses, or
     - the `plan-fixes/<leaf>` draft is ready and a human has merged it into `plan/<leaf>`
   - After that, the planner may help with human review, `log-pr` / `publish-bindify-pr`, or other post-apply work — still not re-implement steps already done.

---

## Guardrails

- Operate in the **product** git repo for the plan branch / draft PR
- Tracking exception: after the draft PR URL exists, `history/` under `.bindify/` or `bindify/` may be written and pushed so the vault shows live work — still never touch tracking `development/`
- From `main`, `master`, `release`, or `release/*`, create `feature/<feature-slug>` first, then `plan/<plan-slug>` from it. The draft PR base is the feature branch
- From `feature/*`, create or reuse `plan/<plan-slug>` only. Do not create a second feature branch
- From a `plan/` or `plan-iteration-N/` branch that already has a PR, the next publish of the **same** plan is `plan-iteration-N/<leaf>` targeting that branch. Do not open another `plan/<leaf>` and do not target `main` or `release/*`
- A `plan/` or `plan-iteration-N/` head with no PR yet is reused. Do not spawn an iteration just because you are already on it
- Never create `feature/` from a `plan/` or `plan-iteration-*` branch
- Never push plan content onto `main`, `release/*`, or `feature/*`
- Default to a **draft** PR; do not mark ready for review in this command
- **Planner ≠ executor:** after opening the draft, the publishing agent must wait for ready-for-review — do not implement steps in the same session unless the human explicitly overrides
- Do not create the plan branch / draft without a reviewed proposal
- Do not delete `wip-docs/`
- Do not snapshot or copy WIP into tracking `development/`
- Do not bump the product submodule pointer for history-only commits
- Use repo-relative paths inside markdown content
- If repository state is unclear, stop and ask

---

## Acceptance criteria

- Checked out branch is the implementation head from the branch stack (`plan/<plan-slug>` or `plan-iteration-N/<plan-slug>`)
- When the starting branch was `main`, `master`, `release`, or `release/*`, `feature/<feature-slug>` exists, is pushed, and is the draft PR base
- When the starting branch was a `plan/` or `plan-iteration-N/` branch that already had a PR, the new head is the next `plan-iteration-N/` and the draft PR targets that previous branch
- No `wip-docs/` commit landed on `main`, `release/*`, or `feature/*`
- `wip-docs/` plan artifacts are committed and pushed on the implementation head
- A draft PR exists from that head into `BASE` (unless `DRAFT_PR=false`), and `BASE` is not `main` or `release/*` unless the human explicitly required it
- When tracking is present, an `in-progress` history card exists under tracking `history/` with the draft PR URL, and the index lists it under **In progress**
- When tracking is missing, the product draft PR still exists and the handoff reports that the history card was skipped
- No writes into tracking `development/`
- Product submodule pointer was not bumped for the history-only commit
- Handoff reports branch, draft PR URL, history-card status, and that the planner is waiting for the draft to become ready for review
- The publishing agent did **not** start `iterate-planning-mode` unless the human explicitly asked to override the split

---

## Related

- `[[references/commands/save-agent-plan.md]]`
- `[[references/commands/iterate-planning-mode.md]]`
- `[[references/commands/review-plan.md]]`
- `[[references/commands/generate-history-summary.md]]`
- `[[references/commands/generate-verify.md]]`
- `[[references/commands/publish-bindify-pr.md]]`
