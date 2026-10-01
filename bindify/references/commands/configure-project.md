# Command: configure-project

Adapt Bindify to the host project by writing or updating tracking `project/` — profile, environment, and optional project-local command overrides.

Tracking root is `.bindify/` or `bindify/` inside the product repo (folder or submodule). Templates come from the **skill**, not from the tracking tree.

---

## When to use

- First-time Bindify setup in a repo
- "adapt bindify to this project"
- "add a dev server command" / "how do we start localhost here"
- Stack, run, or verify commands changed and `environment.md` is stale

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `BINDIFY_TRACKING_PATH` | no | Tracking root; auto-detect `.bindify/` then `bindify/` if omitted |
| `PROJECT_NAME` | no | Display name; inferred from repo root or package manifest if omitted |
| `CATEGORY` | no | `web` \| `mobile` \| `cli` \| `library` \| `other`; inferred when possible |
| `DEV_START` | no | Command to start the local environment (e.g. `npm run dev`) |
| `DEV_URL` | no | Local URL or port (e.g. `http://localhost:3000`) |
| `VERIFY_COMMANDS` | no | Test / lint / build commands if already known |
| `GENERATE_START_DEV` | no | If true, also write `project/commands/start-dev.md` |

Anything missing or ambiguous must be asked before writing.

---

## Output paths

Under the tracking root (`.bindify/` or `bindify/`):

```
project/profile.md
project/environment.md
project/commands/<name>.md   ← optional project overrides
project/local.md             ← machine-local only; never commit secrets here either
```

---

## Procedure

1. Resolve tracking root
   - Use `BINDIFY_TRACKING_PATH`, else `.bindify/`, else `bindify/`. Stop and ask if neither exists and creation is unclear.
   - Templates always load from this skill's `references/templates/` — never from tracking `templates/`.

2. Detect project signals
   - Scan the repo root for manifests and tooling: `package.json`, `pnpm-lock.yaml`, `Cargo.toml`, `go.mod`, `pyproject.toml` / `requirements.txt`, `*.xcodeproj` / `Package.swift`, `Gemfile`, `docker-compose.yml`, etc.
   - Infer package manager, primary stack, and candidate scripts (`dev`, `start`, `test`, `lint`, `build`).
   - Read existing `project/profile.md` and `environment.md` if present — this run merges, it does not wipe.

3. Interview for gaps
   - Confirm or ask: start command, URL/port, env prerequisites (e.g. copy `.env.example` → `.env.local`).
   - Confirm or ask: test / lint / build commands.
   - Ask whether verify needs a running server.
   - Ask whether to generate a project command such as `start-dev`.
   - Stop and ask when required answers are missing; do not invent.

4. Write `profile.md`
   - Create tracking `project/` if missing.
   - Initialize from skill `references/templates/project-profile.md` when the file does not exist.
   - On re-run: update only fields that changed; preserve human-authored notes and constraints.

5. Write `environment.md`
   - Initialize from skill `references/templates/project-environment.md` when missing.
   - Fill **Dev server**, **Verification**, and **Services** from detection + interview.
   - On re-run: merge new answers into the matching sections; leave untouched sections alone.
   - Point **Machine-local** at `project/local.md` (gitignored by convention).

6. Optional project commands
   - If the user wants a runnable workflow (e.g. start localhost), write `project/commands/<name>.md` in the same command-file format as skill commands (Inputs, Procedure, Rules).
   - Project commands override skill commands of the same name when both exist — for this host project only.

7. Gitignore convention
   - Ensure the host repo ignores machine-local files, e.g. `.bindify/project/local.md` or `bindify/project/local.*`.
   - Do not add a `project/` tree to the Bindify skill/source repo; that layer lives only in host tracking.

---

## Rules

- Never write secrets, tokens, or private keys into `profile.md` or `environment.md` — reference env file paths instead
- Machine-specific values (personal ports, local paths) go in `project/local.md`, not the committed files
- Merge on re-run; never regenerate from scratch and discard prior content
- Use repo-relative paths only
- `project/` is committed by default in the tracking repo; only `local.md` / `local.*` are gitignored
- Do not edit skill files (`SKILL.md`, `references/commands/`, `references/templates/`) for per-project adaptation

---

## Acceptance criteria

- Tracking `project/profile.md` and `environment.md` exist and reflect detected + confirmed facts
- Re-running merges without losing prior sections
- No secrets in committed project files
- Optional `project/commands/*.md` files follow the command-file format when generated
- Templates were taken from the skill, not from the tracking folder
