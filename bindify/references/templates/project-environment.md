# Environment — [Project Name]

**Last updated:** YYYY-MM-DD

Source of truth for how to run and verify this repo. Agents must use these commands instead of guessing.

---

## Dev server

| Field | Value |
|---|---|
| Start | `_e.g. npm run dev_` |
| URL | `_e.g. http://localhost:3000_` |
| Prerequisites | `_e.g. copy .env.example → .env.local; docker compose up -d_` |
| Needed for verify | `yes` \| `no` |

---

## Verification

| Kind | Command |
|---|---|
| test | `_e.g. npm test_` |
| lint | `_e.g. npm run lint_` |
| build | `_e.g. npm run build_` |

_Add rows for other checks as needed (typecheck, e2e, format)._

---

## Services

_Optional. Databases, queues, docker compose services, seed commands._

| Service | How to start / use |
|---|---|
| _e.g. postgres_ | `_e.g. docker compose up -d db_` |

---

## Machine-local

Personal overrides (ports, absolute paths, private flags) belong in `local.md` in this folder.

- `local.md` / `local.*` are gitignored by convention and must never hold secrets that belong in a proper secret store.
- Committed files above only reference env _paths_ (e.g. `.env.local`), never secret values.

---

## Related

- `[[profile.md]]`
- `[[commands/start-dev.md]]` _(if present)_
