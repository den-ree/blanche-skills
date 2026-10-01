# Command: publish-bindify-pr

Open a pull request against the Bindify tracking repo with the logs and architecture updates produced by
`log-pr`, **including migration of active `wip-docs/` into the durable Bindify layout**.

The Bindify repo is a **submodule or nested repo inside the product repo** (path `.bindify/` or `bindify/`).
This command migrates WIP artifacts, commits them on a branch in that repo, opens a PR, bumps the submodule
pointer in the product repo, and removes `wip-docs/` from the host root.

Distinct from `publish-plan`:
- `publish-plan` only kickstarts the **product** branch with committed `wip-docs/` (no Bindify writes).
- `publish-bindify-pr` is the **only** WIP → Bindify migration/publish step, run after the product PR exists.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `BINDIFY_SUBMODULE_PATH` | no | Path to Bindify tracking repo; auto-detect `.bindify/` then `bindify/` if omitted |
| `SOURCE_PR` | yes | The product PR these logs describe (number or URL) — used in the PR title/body |
| `CHANGED_PATHS` | no | Repo-relative bindify paths to include — default: migrated plan folder + architecture + history |
| `BASE` | no | Base branch in the bindify repo (default: `main`) |
| `BRANCH` | no | Branch name to create (default: `log/pr-<SOURCE_PR>`) |
| `KEEP_WIP` | no | If `true`, leave `wip-docs/` in place after copy (default: remove after successful migrate) |

---

## Detect Bindify path

Resolve `BINDIFY_SUBMODULE_PATH` in order:

1. Explicit input if provided
2. `<host-root>/.bindify` if it is a git repo / submodule
3. `<host-root>/bindify` if it is a git repo / submodule
4. Stop and ask if neither exists or both exist with conflicting content

---

## Procedure

### A. Migrate `wip-docs/` (when present)

1. **Confirm WIP.** If `wip-docs/` exists at the host project root:
   - Read Category / Feature / Plan from `wip-docs/brief.md`, else `wip-docs/plan.md`, else `wip-docs/proposal.md` / `coordinator.md`.
   - If metadata is missing or ambiguous, stop and ask.
2. **Create destination folders** inside the Bindify repo:
   - `development/<category>/<feature-name>/`
   - `development/<category>/<feature-name>/plans/<plan-name>/`
3. **Copy plan artifacts** into the plan folder:
   - `brief.md`, `proposal.md`, `plan.md` (and any `plan-v*.md`), `updates.md`, `verify.md`
4. **Merge coordinator:**
   - If Bindify already has `development/<category>/<feature-name>/coordinator.md`, prepend new session entries from `wip-docs/coordinator.md` (newest first); never delete older durable entries.
   - If missing, copy `wip-docs/coordinator.md` to that path and rewrite Related links for the nested layout.
5. **Rewrite path metadata** in migrated files so `Plan path` / migration destination reflect the Bindify layout (not `wip-docs/`).
6. **Run `update-links`** on the destination plan folder (and feature folder for coordinator).
7. **Clean up host WIP** unless `KEEP_WIP=true`:
   - Delete `wip-docs/` from the host project root (all contents).
   - Stage the deletion in the **product** repo if `wip-docs/` was tracked.

If `wip-docs/` is absent, skip migration and publish whatever Bindify changes already exist (history, architecture, etc.).

### B. Publish Bindify PR

1. **Validate.** Confirm Bindify path is a git repo and there are changes to publish
   (migrated plan folder, history entries, architecture objects, hotfixes). If nothing changed, stop.
2. **Branch.** In the Bindify repo, checkout `BASE`, pull, and create `BRANCH` (`log/pr-<SOURCE_PR>`).
3. **Commit.** Stage `CHANGED_PATHS` (or all bindify changes) and commit:
   `docs(bindify): log PR #<SOURCE_PR> — <feature/plan> + architecture updates`.
4. **Open PR.** Push and open the PR via gh:
   ```bash
   gh pr create --base <BASE> --head <BRANCH> \
     --title "Log: PR #<SOURCE_PR> — <feature/plan>" \
     --body "<summary + affected architecture objects + alignment rating; link to source PR; note WIP migration>"
   ```
5. **Bump submodule pointer.** In the product repo, stage the updated submodule reference so the product PR (or a
   follow-up) records which bindify log commit corresponds to it. Do not force-push.
6. **Report.** Return the bindify PR URL, migrated destination path, whether `wip-docs/` was removed, and the updated submodule SHA.

---

## PR body should contain

- Link to the source product PR.
- Migration note: source `wip-docs/` → destination `development/<category>/<feature>/plans/<plan>/`.
- The affected architecture objects (`created` / `modified` / `touches`).
- The alignment rating from `log-pr` and a one-line justification.
- Paths to the new/changed history entries plus `updates.md` or `hotfixes.md` evidence.

---

## Hard rules

- **Never commit product code into the Bindify repo** — only bindify artifacts.
- **Never push directly to the bindify `main`** — always via a `log/...` branch + PR.
- Use gh for PR creation; if gh is unavailable, push the branch and report the compare URL for manual PR.
- If the submodule has uncommitted unrelated changes, stop and ask before staging.
- Do not remove `wip-docs/` until copy + link maintenance succeeded.
- Repo-relative paths only in commit bodies and markdown.

---

## Acceptance criteria

- If WIP existed: plan artifacts live under Bindify `development/<category>/<feature>/plans/<plan>/` and `wip-docs/` is gone (unless `KEEP_WIP`).
- Coordinator is present/merged at the feature level in Bindify.
- A `log/pr-<SOURCE_PR>` branch exists with the bindify artifacts.
- A PR is open against the bindify `BASE` with body covering source PR, migration, architecture, and alignment.
- The product repo's submodule pointer is updated to the log commit when applicable.

---

## Related

- `[[references/commands/log-pr.md]]`
- `[[references/commands/publish-plan.md]]`
