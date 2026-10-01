# Command: log-hotfix

Record unplanned bug fixes in `hotfixes.md` and connect them to impacted bindify plans via wiki-links and backlinks.

---

## When to use

- A bug fix was done outside planned step execution
- The human or another agent applied a fix directly in Agent mode
- The team wants traceability between hotfixes and existing plans/features

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `FEATURE_NAME` | yes | Feature/fix folder name in kebab-case |
| `HOTFIX_SUMMARY` | yes | Concise description of what was fixed |
| `FILES_CHANGED` | yes | Repo-relative paths changed by the fix |
| `AFFECTED_PLAN_PATHS` | no | Paths to related plan/coordinator docs that should be linked |
| `BRANCH_NAME` | no | Explicit target branch; defaults to active plan branch, else `main` |

---

## Output path

Write to (inside the Bindify tracking repo — `.bindify/` or `bindify/`):

```
development/fixes/<feature-name>/hotfixes.md
```

If the active feature still lives only in `wip-docs/` and has not migrated yet, prefer linking `AFFECTED_PLAN_PATHS` to `wip-docs/` artifacts; still write hotfixes into the Bindify tracking repo (not into `wip-docs/`).

---

## Procedure

1. Ensure fix folder exists
   - Resolve Bindify root (`.bindify/` or `bindify/`)
   - Create `development/fixes/<feature-name>/` if missing
   - Initialize `hotfixes.md` from the hotfixes template if needed

2. Append entry
   - Add a new top entry with date, summary, changed files, and outcome
   - Keep existing entries unchanged (append-only history)

3. Link impacted docs
   - Add `[[wiki-links]]` to each file in `AFFECTED_PLAN_PATHS` (may include `wip-docs/*`)
   - Invoke `update-links` to refresh backlinks and `## Related` sections

4. Commit tracking update
   - Commit in `BRANCH_NAME` when provided
   - Otherwise commit in active plan branch; fallback to `main` only when no plan branch is involved

---

## Guardrails

- Do not rewrite or delete previous hotfix entries
- Keep logs factual; do not infer unverified root causes
- Use repo-relative paths only
- Do not place hotfixes inside `wip-docs/`
- If no affected context docs can be identified, stop and ask

---

## Acceptance criteria

- `hotfixes.md` exists under Bindify `development/fixes/<feature-name>/` and includes the new entry
- Affected plans/features are linked
- Backlinks are refreshed via `update-links`
- Change is committed on the appropriate tracking branch
