# Command: publish-bindify-pr

Open a pull request against the `.bindify` tracking repo with the logs and architecture updates produced by
`log-pr`. This is step 5 of the bindify vision flow.

The `.bindify` repo is a **submodule inside the product repo**. This command commits the new bindify artifacts on
a branch in that submodule, opens a PR, and bumps the submodule pointer in the product repo so the tracking
history travels with the code.

Distinct from `publish-plan`: `publish-plan` pushes a *plan branch* up front before work; `publish-bindify-pr`
publishes the *log of what a merged/under-review PR did* after the fact.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `BINDIFY_SUBMODULE_PATH` | yes | Path to the `.bindify` submodule inside the product repo |
| `SOURCE_PR` | yes | The product PR these logs describe (number or URL) — used in the PR title/body |
| `CHANGED_PATHS` | no | Repo-relative bindify paths to include (updates.md, architecture/*) — default: all uncommitted bindify changes |
| `BASE` | no | Base branch in the bindify repo (default: `main`) |
| `BRANCH` | no | Branch name to create (default: `log/pr-<SOURCE_PR>`) |

---

## Procedure

1. **Validate.** Confirm `BINDIFY_SUBMODULE_PATH` is a git repo and there are bindify changes to publish
   (updates/hotfixes entries, `architecture/` objects). If nothing changed, stop — there is nothing to publish.
2. **Branch.** In the submodule, checkout `BASE`, pull, and create `BRANCH` (`log/pr-<SOURCE_PR>`).
3. **Commit.** Stage `CHANGED_PATHS` (or all bindify changes) and commit:
   `docs(bindify): log PR #<SOURCE_PR> — <feature/plan> + architecture updates`.
4. **Open PR.** Push and open the PR via gh:
   ```bash
   gh pr create --base <BASE> --head <BRANCH> \
     --title "Log: PR #<SOURCE_PR> — <feature/plan>" \
     --body "<summary + affected architecture objects + alignment rating; link to source PR>"
   ```
5. **Bump submodule pointer.** In the product repo, stage the updated submodule reference so the product PR (or a
   follow-up) records which bindify log commit corresponds to it. Do not force-push.
6. **Report.** Return the bindify PR URL and the updated submodule SHA.

---

## PR body should contain

- Link to the source product PR.
- The affected architecture objects (`created` / `modified` / `touches`).
- The alignment rating from `log-pr` and a one-line justification.
- Paths to the new/changed `updates.md` or `hotfixes.md` entries.

---

## Hard rules

- **Never commit product code here** — only bindify artifacts in the submodule.
- **Never push directly to the bindify `main`** — always via a `log/...` branch + PR.
- Use gh for PR creation; if gh is unavailable, push the branch and report the compare URL for manual PR.
- If the submodule has uncommitted unrelated changes, stop and ask before staging.
- Repo-relative paths only in commit bodies and markdown.

---

## Acceptance criteria

- A `log/pr-<SOURCE_PR>` branch exists in the submodule with exactly the bindify artifacts.
- A PR is open against the bindify `BASE` with body covering source PR, architecture objects, and alignment.
- The product repo's submodule pointer is updated to the log commit.

---

## Related

- `[[references/commands/log-pr.md]]`
- `[[references/commands/publish-plan.md]]`
