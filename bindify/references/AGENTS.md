# Bindify — Agent Entry Point

Use this file as a quick entry point, not as the full specification.

- Canonical protocol, command list, and workflow rules live in `SKILL.md`.
- Command behavior details live in `.bindify/commands/*.md`.
- Templates live in `.bindify/templates/*.md`.

## Hard rules

- Never modify `plan.md` during apply; execution state belongs in `updates.md`.
- `updates.md` and `hotfixes.md` are append-only.
- Every update entry carries **Impact & Connections** + **Architecture** sections — logs connect changes to the architecture graph, they are not flat changelogs.
- Architecture object **Responsibility** is human-owned; `scan-architecture fill` only appends change-log lines and edges.
- Use `project/environment.md` commands to run/verify the app; never guess.
- Use repo-relative paths only.
- Keep context docs markdown-only (paths and symbols, not code dumps).
- When required input is missing or ambiguous, stop and ask.

## Read order for agents

1. `SKILL.md`
2. `.bindify/project/profile.md` and `.bindify/project/environment.md` (if present)
3. Current feature `coordinator.md` (if present)
4. `architecture/_map.md` — the system skeleton, when reasoning about impact or alignment
5. Relevant `brief.md` / `proposal.md` / `plan.md` for the active workflow step
6. `references/docs/workflow.md` — when branch strategy or doc linking is unclear
