# Command: log-pr

Read a pull request — the unit of change — and write an architecture-aware log: what the PR did, what it
affects elsewhere, which architecture objects it moves, and how well it aligns with the project's standards and
patterns. This happens alongside the root history layer, where `generate-history-summary` produces the concise
human/UI digest and `log-pr` records the detailed PR-alignment evidence. It is followed by `publish-bindify-pr`.

`log-pr` does not change product code. It reads a PR that already exists and produces bindify artifacts.

When `wip-docs/` is present, treat it as the **primary step-artifact source** for intent and execution evidence
before writing durable logs into the Bindify tracking repo.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `PR` | yes | PR number or URL |
| `BASE` | no | Base branch for diff fallback (default: repo default branch) |
| `STEPS_FILE` | no | Repo-relative path to the iterate-mode steps file attached to / referenced by the PR |
| `CATEGORY` | no | `features` \| `fixes` \| `refactor` \| `chore` — prefer `wip-docs/` headers, else infer from PR |
| `FEATURE_NAME` | no | Prefer `wip-docs/` headers, else infer from branch/labels/linked plan |
| `PLAN_NAME` | no | Prefer `wip-docs/` headers, else infer |

---

## Ingestion — use the richest source available, fall back in order

1. **`wip-docs/` (preferred when present).** Read `plan.md`, `updates.md`, `brief.md`, `verify.md`, `coordinator.md`
   as the authoritative record of planned steps and execution evidence for the active feature.
2. **gh CLI / GitHub API.** Pull PR metadata, file set, and diff:
   ```bash
   gh pr view <PR> --json title,body,author,commits,files,baseRefName,headRefName,labels,url
   gh pr diff <PR>
   ```
   Captures discussion, intent, and the authoritative file/diff set.
3. **iterate-mode steps file.** If `STEPS_FILE` is given (the final iteration document the executor attached to
   the PR), read it as an additional record of *what was intended* step by step.
4. **git diff vs base (offline fallback).** If gh is unavailable:
   ```bash
   git diff <BASE>...<head-branch> --stat
   git diff <BASE>...<head-branch>
   ```

Prefer 1 for plan evidence, 2 for metadata + alignment, 3 for attached step files, 4 only when 2 is impossible.
State in the log which sources were used.

---

## Procedure

1. **Resolve placement.** Determine `CATEGORY` / `FEATURE_NAME` / `PLAN_NAME` from `wip-docs/` headers first,
   then PR labels, branch name, or a linked plan.
2. **Migrate WIP if needed.** If `wip-docs/` still exists at the host root, perform the same migration steps as
   `publish-bindify-pr` section A (copy plan artifacts into Bindify `development/<category>/<feature>/plans/<plan>/`,
   merge coordinator, rewrite metadata, `update-links`). Prefer leaving cleanup of `wip-docs/` to
   `publish-bindify-pr` unless the human asked to finish packaging in this command.
3. **Read the architecture skeleton.** Load `architecture/_map.md` from `.bindify/` or `bindify/` and the objects
   the diff plausibly touches.
4. **Summarize the change** in the impact-aware `updates.md` format from `summarize-work-for-updates`:
   - Prefer appending the PR alignment entry to the **migrated** plan `updates.md` (or to `wip-docs/updates.md`
     if migration is deferred to `publish-bindify-pr`).
   - If the PR is a standalone fix with no plan, route to `development/fixes/<feature>/hotfixes.md` instead.
   - Include Summary, File Changes, Key Components, **Impact & Connections**, **Architecture**.
5. **Write the Alignment assessment** (see format below).
6. **Update the architecture graph.** Invoke `scan-architecture` in `fill` mode with this PR's changes as
   `SOURCE_REFS`.
7. **Refresh links.** Run `update-links` for the affected folder (`wip-docs/` and/or migrated plan folder).
8. **Check root history state.** If a PR exists and no root history summary has been created yet, suggest or run
   `generate-history-summary` in `pr-open` mode so the outcome appears in Bindify `history/`.
9. **Hand off.** Report the log path and the affected architecture objects; suggest `publish-bindify-pr` to open
   the PR against the Bindify submodule (and finish WIP cleanup if still pending).

---

## Alignment assessment format

Append this block inside the PR's `updates.md` entry, after **Architecture**:

```markdown
### Alignment
- **Follows:** [[architecture/standards/<pattern>]] — how the PR conforms
- **Deviates:** [[architecture/standards/<pattern>]] — where and why it diverges (or "none")
- **New convention:** <any pattern the PR introduces that should become a `standard` object> (or "none")
- **Rating:** `aligned` | `mostly aligned` | `diverges` — one-line justification
```

Base the rating on evidence from the diff and the standard/pattern objects, not vibes. If the codebase has no
`standard`/`pattern` objects yet, note that and recommend a `scan-architecture bootstrap` first.

---

## Hard rules

- **Read-only on product code.** Never push code or edit the product source from this command.
- **`updates.md` / `hotfixes.md` are append-only.** Add one PR entry; never rewrite history.
- **Ground alignment in objects**, not opinion — cite the `standard`/`pattern` object you measured against.
- **Repo-relative paths only.** No absolute paths in markdown.
- Prefer `wip-docs/` as the active evidence source until migration completes.
- If feature/plan placement is ambiguous, stop and ask before writing.

---

## Acceptance criteria

- A single impact-aware entry is appended for the PR, including non-empty Impact & Connections, Architecture,
  and Alignment sections.
- When `wip-docs/` was present, Category/Feature/Plan were resolved from its headers and migration was performed
  or explicitly deferred to `publish-bindify-pr`.
- `scan-architecture fill` has run; objects the PR touched exist and carry a change-log line citing the PR.
- The log states which ingestion sources were used.

---

## Related

- `[[references/commands/summarize-work-for-updates.md]]`
- `[[references/commands/generate-history-summary.md]]`
- `[[references/commands/scan-architecture.md]]`
- `[[references/commands/publish-bindify-pr.md]]`
- `[[references/commands/log-hotfix.md]]`
