# Command: publish-plan

Publish a plan to a dedicated bindify tracking repository by creating a plan branch and pushing the plan folder.

---

## When to use

- The human says `/bindify` or asks to publish the plan
- `plan.md` is ready and tied to an approved proposal
- Execution should happen on a persistent per-plan branch

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `BINDIFY_REPO_PATH` | yes | Local path to the dedicated bindify repository |
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` |
| `FEATURE_NAME` | yes | Feature folder name in kebab-case |
| `PLAN_NAME` | yes | Plan folder name in kebab-case |
| `PATH_TO_PROPOSAL_MD` | yes | Repo-relative path to reviewed `proposal.md` |
| `PATH_TO_PLAN_MD` | yes | Repo-relative path to `plan.md` |
| `ALLOW_OVERWRITE` | no | `true` only with explicit human approval if branch already exists |

---

## Branch strategy

- Base branch: `main`
- Plan branch: `plan/<plan-name>`
- Merge policy: merge back to `main` after `verify.md` is signed off by human

---

## Procedure

1. Validate prerequisites
   - Confirm `PATH_TO_PLAN_MD` exists
   - Confirm `PATH_TO_PROPOSAL_MD` exists
   - Confirm proposal decision is `approved` or `approved with changes`

2. Create or select branch
   - In `BINDIFY_REPO_PATH`, checkout `main` and create `plan/<plan-name>`
   - If branch exists and `ALLOW_OVERWRITE` is not `true`, stop and ask

3. Sync plan folder
   - Copy `.bindify/development/<category>/<feature-name>/plans/<plan-name>/` into the bindify repo branch
   - Preserve existing files unless explicit overwrite is approved

4. Run link maintenance
   - Invoke `update-links` on the copied plan folder

5. Commit and publish
   - Commit with message `feat(bindify): publish plan <plan-name>`
   - Push branch to remote

6. Return handoff context
   - Report branch name
   - Report plan folder path in the bindify repo
   - Instruct executor agents to continue work on this branch

---

## Guardrails

- Never push plan content directly to `main`
- Do not create plan branch without a reviewed proposal
- Use repo-relative paths inside markdown content
- If repository state is unclear, stop and ask

---

## Acceptance criteria

- Branch `plan/<plan-name>` exists from `main`
- Plan folder is present on that branch
- Links are refreshed via `update-links`
- Branch is pushed and ready for executor workflow
