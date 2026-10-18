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
| Tracking | `.bindify/` or `bindify/` in the product repo (folder or submodule) | Read `project/`, `architecture/`; migrate durable `development/` at packaging; `history/` may start at draft PR |

**Never** open the tracking folder looking for skill command specs or brief/proposal templates. Those are only in the skill.

Example — `draft-brief`:
1. Read command + template from the **skill**
2. Optionally read tracking `project/profile.md` / `architecture/_map.md` for project context
3. Write `wip-docs/brief.md`

## Active work vs durable history

- **Active feature docs** live in `wip-docs/` at the **host project root** (flat). `publish-plan` stacks branches: `main` or `release/*` → `feature/<feature-slug>` → `plan/<plan-slug>` (draft PR into the feature branch). Already on `feature/*` → `plan/<plan-slug>` into that feature. Already on a published `plan/` or `plan-iteration-N/` branch → next `plan-iteration-N/<leaf>` into that branch.
- **Durable history / architecture** live in the Bindify tracking repo at `.bindify/` or `bindify/`.
- Do **not** write active plan artifacts into tracking `development/` during apply. Migrate via `publish-bindify-pr` / `log-pr` when packaging.
- `publish-plan` creates that product branch stack, commits `wip-docs/` only on the implementation head, opens the draft PR into the immediate parent, and upserts an `in-progress` history card under tracking `history/` (not `development/`). It creates `feature/<feature-slug>` only from `main` or `release/*`, never from a `plan/` branch.
- After `publish-plan`, the **planner waits** for the draft PR to become ready for review; a **separate executor** runs `iterate-planning-mode`.
- Executor stays on the triggering draft head (`plan/<leaf>`, `plan-iteration-N/<leaf>`, or `plan-fixes/…`): no new branches; all step commits push there; finish path runs `gh pr ready` on that draft.
- When `iterate-planning-mode` finishes the last unfinished step, it marks that draft PR ready for review and stops committing on that branch.
- `ready_for_review` on `plan/<leaf>` or `plan-iteration-N/<leaf>` starts a **reviewer** (`review-plan`). In-scope misses become appended steps on `plan-fixes/…` with one draft PR into that head (not into `feature/*`, `main`, or `release/*`). Improvements stay PR comments. `ready_for_review` on `plan-fixes/*` does not start another reviewer.
- Plan-step commits are one-per-step and authored as `blanche <blanche@bindify.app>` via `--author` (never change git config).

## Hard rules

- Never modify existing plan steps during apply; execution state belongs in `updates.md`. `review-plan` may append new steps on `plan-fixes/` only.
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
- **Git branch:** `main` or `release/*` → create `feature/<feature-slug>`, then `plan/<plan-slug>` whose draft PR targets the feature branch. On `feature/*`, create only `plan/<plan-slug>` into that feature. On a published `plan/<leaf>` or `plan-iteration-N/<leaf>`, create the next `plan-iteration-N/<leaf>` targeting that branch. `review-plan` alone creates `plan-fixes/…`, targeting the reviewed head. Executors never create a branch. Never create `feature/` from `plan/`, and never open `plan/` into `main` or `release/*`.

## Cloud & Linux Agent Execution (e.g. Cursor Cloud)

When executing in Linux cloud environments on macOS/iOS codebases:
- **No macOS toolchains:** Do not run `xcodebuild`, `xcrun`, or Simulator commands. macOS build/test verification happens downstream via local worktrees.
- **Compiler failure feedback:** If `test-failure.log` exists in the repo root, resolve those compiler/test errors first, delete the log file, and commit.
- **Output:** Focus on clean, typed source modifications and append execution evidence to `wip-docs/updates.md`.

## Read order for agents

1. This skill's `SKILL.md` and the relevant `references/commands/<name>.md`
2. For a feature or fix question before a brief: `investigate` — list tracking feature-folder names and read related fixes before product code
3. `wip-docs/` — if present, this is the active feature context
4. Tracking `project/profile.md` and `project/environment.md` (under `.bindify/` or `bindify/`) if present
5. Tracking `architecture/_map.md` — when reasoning about impact or alignment
6. Skill `references/docs/workflow.md` — when branch strategy or doc linking is unclear
