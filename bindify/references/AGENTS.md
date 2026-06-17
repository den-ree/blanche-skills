# Bindify — Agent Entry Point

Use this file as a quick entry point, not as the full specification.

- Canonical protocol, command list, and workflow rules live in `SKILL.md`.
- Command behavior details live in `.bindify/commands/*.md`.
- Templates live in `.bindify/templates/*.md`.

## Hard rules

- Never modify `plan.md` during apply; execution state belongs in `updates.md`.
- `updates.md` and `hotfixes.md` are append-only.
- Use repo-relative paths only.
- Keep context docs markdown-only (paths and symbols, not code dumps).
- When required input is missing or ambiguous, stop and ask.

## Read order for agents

1. `SKILL.md`
2. Current feature `coordinator.md` (if present)
3. Relevant `brief.md` / `proposal.md` / `plan.md` for the active workflow step
4. `references/docs/workflow.md` — when branch strategy or doc linking is unclear
