# Command: configure-project

Adapt Bindify to the host project by writing or updating `.bindify/project/` — profile, environment, and optional project-local commands.

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
| `PROJECT_NAME` | no | Display name; inferred from repo root or package manifest if omitted |
| `CATEGORY` | no | `web` \| `mobile` \| `cli` \| `library` \| `other`; inferred when possible |
| `DEV_START` | no | Command to start the local environment (e.g. `npm run dev`) |
| `DEV_URL` | no | Local URL or port (e.g. `http://localhost:3000`) |
| `VERIFY_COMMANDS` | no | Test / lint / build commands if already known |
| `GENERATE_START_DEV` | no | If true, also write `project/commands/start-dev.md` |

Anything missing or ambiguous must be asked before writing.

---

## Output paths

```
.bindify/project/profile.md
.bindify/project/environment.md
.bindify/project/commands/<name>.md   ← optional
.bindify/project/local.md             ← machine-local only; never commit secrets here either
```

---

## Procedure

1. Detect project signals
   - Scan the repo root for manifests and tooling: `package.json`, `pnpm-lock.yaml`, `Cargo.toml`, `go.mod`, `pyproject.toml` / `requirements.txt`, `*.xcodeproj` / `Package.swift`, `Gemfile`, `docker-compose.yml`, etc.
   - Infer package manager, primary stack, and candidate scripts (`dev`, `start`, `test`, `lint`, `build`).
   - Read existing `.bindify/project/profile.md` and `environment.md` if present — this run merges, it does not wipe.

2. Interview for gaps
   - Confirm or ask: start command, URL/port, env prerequisites (e.g. copy `.env.example` → `.env.local`).
   - Confirm or ask: test / lint / build commands.
   - Ask whether verify needs a running server.
   - Ask whether to generate a project command such as `start-dev`.
   - Stop and ask when required answers are missing; do not invent.

3. Write `profile.md`
   - Create `.bindify/project/` if missing.
   - Initialize from `.bindify/templates/project-profile.md` (or the skill's `references/templates/project-profile.md`) when the file does not exist.
   - On re-run: update only fields that changed; preserve human-authored notes and constraints.

4. Write `environment.md`
   - Initialize from `.bindify/templates/project-environment.md` when missing.
   - Fill **Dev server**, **Verification**, and **Services** from detection + interview.
   - On re-run: merge new answers into the matching sections; leave untouched sections alone.
   - Point **Machine-local** at `project/local.md` (gitignored by convention).

5. Optional project commands
   - If the user wants a runnable workflow (e.g. start localhost), write `.bindify/project/commands/<name>.md` in the same command-file format as canonical commands (Inputs, Procedure, Rules).
   - Project commands override canonical commands of the same name when both exist.

6. Gitignore convention
   - Ensure the host repo ignores machine-local files, e.g. `.bindify/project/local.md` (or `.bindify/project/local.*`).
   - Do not add a `project/` tree to the Bindify skill/source repo; that layer lives only in host projects.

---

## Rules

- Never write secrets, tokens, or private keys into `profile.md` or `environment.md` — reference env file paths instead
- Machine-specific values (personal ports, local paths) go in `project/local.md`, not the committed files
- Merge on re-run; never regenerate from scratch and discard prior content
- Use repo-relative paths only
- `project/` is committed by default in the host project; only `local.md` / `local.*` are gitignored
- Canonical Bindify skill files (`SKILL.md`, `commands/`, `templates/`, `docs/`) must not be edited for per-project adaptation

---

## Acceptance criteria

- `.bindify/project/profile.md` and `environment.md` exist and reflect detected + confirmed facts
- Re-running merges without losing prior sections
- No secrets in committed project files
- Optional `project/commands/*.md` files follow the command-file format when generated
