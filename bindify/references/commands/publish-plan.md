# Command: publish-plan

Publish a plan to a dedicated Bindify tracking repository by creating a plan branch and syncing from `wip-docs/`.

---

## When to use

- The human says `/bindify` or asks to publish the plan
- `wip-docs/plan.md` is ready and tied to an approved proposal
- Execution should happen on a persistent per-plan branch in the Bindify tracking repo

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `BINDIFY_REPO_PATH` | no | Local path to the Bindify tracking repo; auto-detect `.bindify/` then `bindify/` if omitted |
| `CATEGORY` | no | Infer from `wip-docs/brief.md` / `plan.md` header when omitted |
| `FEATURE_NAME` | no | Infer from WIP headers when omitted |
| `PLAN_NAME` | no | Infer from WIP headers when omitted |
| `PATH_TO_PROPOSAL_MD` | no | Defaults to `wip-docs/proposal.md` |
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` |
| `ALLOW_OVERWRITE` | no | `true` only with explicit human approval if branch already exists |

---

## Branch strategy

- Base branch: `main`
- Plan branch: `plan/<plan-name>`
- Merge policy: merge back to `main` after `verify.md` is signed off by human and WIP has been migrated

---

## Procedure

1. Validate prerequisites
   - Confirm `PATH_TO_PLAN_MD` exists (default `wip-docs/plan.md`)
   - Confirm `PATH_TO_PROPOSAL_MD` exists (default `wip-docs/proposal.md`)
   - Confirm proposal decision is `approved` or `approved with changes`
   - Resolve `CATEGORY` / `FEATURE_NAME` / `PLAN_NAME` from inputs or WIP headers
   - Resolve `BINDIFY_REPO_PATH` (`.bindify/` or `bindify/`)

2. Create or select branch
   - In `BINDIFY_REPO_PATH`, checkout `main` and create `plan/<plan-name>`
   - If branch exists and `ALLOW_OVERWRITE` is not `true`, stop and ask

3. Sync plan folder from WIP
   - Copy current `wip-docs/` plan artifacts (`brief.md`, `proposal.md`, `plan*.md`, and `coordinator.md` if present) into:
     `development/<category>/<feature-name>/plans/<plan-name>/`
     (coordinator goes to `development/<category>/<feature-name>/coordinator.md`)
   - This is a **snapshot for the plan branch**, not the final migration — active work continues in `wip-docs/` until `publish-bindify-pr` / `log-pr`
   - Preserve existing Bindify files unless explicit overwrite is approved

4. Run link maintenance
   - Invoke `update-links` on the copied plan folder

5. Commit and publish
   - Commit with message `feat(bindify): publish plan <plan-name>`
   - Push branch to remote

6. Return handoff context
   - Report branch name
   - Report plan folder path in the Bindify repo
   - Instruct executor agents to continue writing execution evidence to **`wip-docs/`** on the product branch; Bindify plan branch is tracking snapshot + durable log destination after migrate

---

## Guardrails

- Never push plan content directly to `main`
- Do not create plan branch without a reviewed proposal
- Do not delete `wip-docs/` in this command (migration happens later)
- Use repo-relative paths inside markdown content
- If repository state is unclear, stop and ask

---

## Acceptance criteria

- Branch `plan/<plan-name>` exists from `main`
- Plan folder is present on that branch under `development/<category>/<feature>/plans/<plan>/`
- Links are refreshed via `update-links`
- Branch is pushed and ready for executor workflow
- `wip-docs/` remains the active working folder in the host project
