# Bindify — Agent Entry Point

Use this file as a quick entry point, not as the full specification.

- Canonical protocol, command list, and workflow rules live in this skill's `SKILL.md`.
- Command behavior details live in this skill's `references/commands/*.md`.
- Templates live in this skill's `references/templates/*.md`.

## Three path layers

| Layer | Path | Use for |
|---|---|---|
| Skill | Installed bindify skill | Commands + templates (how to run bindify) |
| Active WIP | `wip-docs/` at host project root | Write brief/proposal/plan/updates/verify/coordinator |
| Tracking | `.bindify/` or `bindify/` in the product repo (folder or submodule) | Read `project/`, `architecture/`; migrate durable `development/` + `history/` at packaging |

**Never** open the tracking folder looking for skill command specs or brief/proposal templates. Those are only in the skill.

Example — `draft-brief`:
1. Read command + template from the **skill**
2. Optionally read tracking `project/profile.md` / `architecture/_map.md` for project context
3. Write `wip-docs/brief.md`

## Active work vs durable history

- **Active feature docs** live in `wip-docs/` at the **host project root** (flat), on product branch `plan/<plan-name>` after `publish-plan` (reuse existing `plan/` branch; parent may be `release/*` or `feature/*`; opens a **draft** PR).
- **Durable history / architecture** live in the Bindify tracking repo at `.bindify/` or `bindify/`.
- Do **not** write active plan artifacts into the Bindify submodule during apply. Migrate via `publish-bindify-pr` / `log-pr` when packaging.
- `publish-plan` only ensures the **product** `plan/` branch + draft PR — it never snapshots into tracking and never creates a `feature/` branch from the plan name.
- When `iterate-planning-mode` finishes the last step, it marks that draft PR ready for review.
- Plan-step commits are one-per-step and authored as `blanche <blanche@bindify.app>` via `--author` (never change git config).

## Hard rules

- Never modify `plan.md` during apply; execution state belongs in `updates.md`.
- `updates.md` and `hotfixes.md` are append-only.
- Every update entry carries **Impact & Connections** + **Architecture** sections — logs connect changes to the architecture graph, they are not flat changelogs.
- Architecture object **Responsibility** is human-owned; `scan-architecture fill` only appends change-log lines and edges.
- Use tracking `project/environment.md` commands to run/verify the app; never guess.
- Use repo-relative paths only.
- Keep context docs markdown-only (paths and symbols, not code dumps).
- When required input is missing or ambiguous, stop and ask.
- **Word limits:** Briefs must be ≤ 150 words. Proposals must be ≤ 250 words.
- **Prototype-first:** User-facing features must implement a mock UI prototype in Step-001 before wiring logic.
- **WIP location:** Active brief/proposal/plan/updates/verify/coordinator → `wip-docs/` only.
- **Git branch:** Only `plan/<plan-name>` for implementation. Never create `feature/...` from a plan branch. `FEATURE_NAME` is metadata, not a branch.

## Cloud & Linux Agent Execution (e.g. Cursor Cloud)

When executing in Linux cloud environments on macOS/iOS codebases:
- **No macOS toolchains:** Do not run `xcodebuild`, `xcrun`, or Simulator commands. macOS build/test verification happens downstream via local worktrees.
- **Compiler failure feedback:** If `test-failure.log` exists in the repo root, resolve those compiler/test errors first, delete the log file, and commit.
- **Output:** Focus on clean, typed source modifications and append execution evidence to `wip-docs/updates.md`.

## Read order for agents

1. This skill's `SKILL.md` and the relevant `references/commands/<name>.md`
2. `wip-docs/` — if present, this is the active feature context
3. Tracking `project/profile.md` and `project/environment.md` (under `.bindify/` or `bindify/`) if present
4. Tracking `architecture/_map.md` — when reasoning about impact or alignment
5. Skill `references/docs/workflow.md` — when branch strategy or doc linking is unclear
