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
| `BRANCH_NAME` | no | Implementation branch. Defaults to `plan/<plan-name>`. Must stay under `plan/` unless the human explicitly overrides |
| `BASE` | no | Parent branch to fork from / PR base. Defaults to **current branch** when it is a parent branch (`main`, `release/*`, `feature/*`, etc.). Never default to inventing a new `feature/` name |
| `ALLOW_OVERWRITE` | no | `true` only with explicit human approval if an existing `plan/` branch would be reset |
| `DRAFT_PR` | no | Defaults to `true`. When `true`, ensure a draft PR exists from the plan branch into `BASE` |
| `PR_TITLE` | no | Defaults to `Plan: <plan-name>` (or feature + plan from WIP headers) |

---

## Naming trap (read this)

| Concept | Example | Is a git branch? |
|---|---|---|
| WIP metadata `Feature:` / `FEATURE_NAME` | `onboarding-flow` | **No** — folder name after migration only |
| WIP metadata `Category:` | `features` | **No** |
| Implementation branch | `plan/onboarding-flow` | **Yes** — only place to commit |
| Parent / PR base | `main`, `release/1.0.3`, or an **existing** `feature/foo` | **Yes** — fork-from / PR base only; **never create** one here |

If an agent creates `feature/<something>` from a `plan/` branch, that is a bug. Stay on `plan/`.

---

## Procedure

1. Validate prerequisites
   - Confirm `PATH_TO_PLAN_MD` exists (default `wip-docs/plan.md`)
   - Confirm `PATH_TO_PROPOSAL_MD` exists (default `wip-docs/proposal.md`)
   - Confirm proposal `Human review → Decision` is `approved` or `approved with changes`
   - Resolve `CATEGORY` / `FEATURE_NAME` / `PLAN_NAME` from inputs or WIP headers
   - Run `update-links` for `wip-docs/` if links look stale

2. Resolve implementation branch (`plan/...`)
   - Target = `BRANCH_NAME` if provided, else `plan/<plan-name>`
   - If `BRANCH_NAME` is provided and does **not** start with `plan/`, stop and ask (do not silently create `feature/...`)
   - Detect current branch: `git branch --show-current`
   - **Reuse path (preferred):**
     - If current branch == target → keep it
     - Else if target exists locally (`git show-ref --verify refs/heads/<target>`) → checkout target
     - Else if target exists on remote (`origin/<target>`) → checkout tracking branch for target
     - Do **not** create a new branch in any of these cases
   - **Create path (only when target does not exist anywhere):**
     - Resolve `BASE`:
       - Use explicit `BASE` if given
       - Else if current branch is a parent branch (`main`, `master`, `develop`, `release/*`, `feature/*`, `hotfix/*`, or anything **not** starting with `plan/`) → use current branch as `BASE`
       - Else if current branch is some other `plan/...` → stop and ask which parent to fork from
     - From `BASE`, create and checkout `plan/<plan-name>`
   - Never create a branch whose name starts with `feature/` as part of this command
   - Remember `BASE` for the draft PR even on the reuse path (infer from existing PR if one exists, else from explicit input / prior parent)

3. Stage active WIP on the implementation branch
   - Ensure these exist under `wip-docs/` when present: `brief.md`, `proposal.md`, `plan.md` (and any `plan-v*.md`), `coordinator.md`
   - Do **not** create `updates.md` / `verify.md` here unless they already exist
   - Do **not** write into `.bindify/` or `bindify/`

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
   - Push the **same** `plan/<plan-name>` branch to remote (`-u` when first publishing)
   - Do not push a differently named branch

5. Ensure draft pull request (`DRAFT_PR` default `true`)
   - Resolve PR base = `BASE` (parent branch). If unknown on reuse path, ask rather than guessing `main` when the user was on `release/*` or `feature/*`.
   - Check for an existing PR from head `plan/<plan-name>`:
     ```bash
     gh pr list --head <plan-branch> --json number,isDraft,url,baseRefName
     ```
   - If a PR already exists:
     - Reuse it. If it is not a draft and work has not started review yet, leave it as-is unless the human asks to convert.
     - Report the existing URL (draught or open).
   - If no PR exists, create a **draft**:
     ```bash
     gh pr create --draft --base <BASE> --head <plan-branch> \
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

6. Return handoff context — then **STOP**
   - Report implementation branch (`plan/<plan-name>`), parent/`BASE`, whether branch was created or reused
   - Report **draft PR URL** (or existing PR URL)
   - Report `wip-docs/plan.md` as the path the **executor** agent will use
   - Tell the human: draft is published; a different agent should implement via `iterate-planning-mode`
   - Remind: Bindify migration is deferred to `publish-bindify-pr` after the product PR is ready/merged

7. Planner wait gate (mandatory for the agent that ran `publish-plan`)
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

- Operate only in the **product** git repo — never the Bindify submodule for this command
- Implementation branch must be `plan/...` — never invent `feature/...` from the plan name
- If `plan/<plan-name>` already exists, reuse it; do not create a sibling or child branch
- Never create a new branch while already on the matching `plan/` branch
- Never push plan content directly to parent branches (`main`, `release/*`, `feature/*`)
- Default to a **draft** PR; do not mark ready for review in this command
- **Planner ≠ executor:** after opening the draft, the publishing agent must wait for ready-for-review — do not implement steps in the same session unless the human explicitly overrides
- Do not create the plan branch / draft without a reviewed proposal
- Do not delete `wip-docs/`
- Do not snapshot or copy WIP into tracking `development/`
- Use repo-relative paths inside markdown content
- If repository state is unclear, stop and ask

---

## Acceptance criteria

- Checked out branch is `plan/<plan-name>` (or explicit `plan/...` override)
- No new `feature/...` branch was created by this command
- If `plan/<plan-name>` already existed, it was reused (not recreated)
- `wip-docs/` plan artifacts are committed and pushed on that branch
- A draft PR exists from `plan/<plan-name>` into `BASE` (unless `DRAFT_PR=false`)
- No writes into `.bindify/` / `bindify/`
- Handoff reports branch, draft PR URL, and that the planner is waiting for the draft to become ready for review
- The publishing agent did **not** start `iterate-planning-mode` unless the human explicitly asked to override the split

---

## Related

- `[[references/commands/save-agent-plan.md]]`
- `[[references/commands/iterate-planning-mode.md]]`
- `[[references/commands/review-plan.md]]`
- `[[references/commands/generate-verify.md]]`
- `[[references/commands/publish-bindify-pr.md]]`
