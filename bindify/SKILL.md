---
name: bindify
description: Bindify is a filesystem-based protocol for coordinating AI agents on software work. Use this skill whenever the user mentions bindify, asks about coordinator/brief/proposal/plan/updates/verify files, references a `.bindify/` folder, asks to "save a plan", "coordinate updates", "iterate planning mode", "summarize work for updates", "generate verify", or works in a repo that contains a `.bindify/` directory. Also use when the user asks an orchestrator agent (e.g. Claude Code) to delegate work to executor agents (e.g. pi), or when they describe a multi-agent workflow with shared markdown files. The skill defines the folder layout, the plan → propose → review → apply → verify pipeline, the file templates, and the six commands that drive the system.
---

# Bindify

Bindify is a filesystem-based communication protocol for AI agents working on software, where agents communicate by reading and writing structured markdown files inside a `.bindify/` folder at the repo root.

This skill is what makes that protocol legible. Read this whole file when bindify is in play; load the command and template files from `references/` on demand.

## When to invoke each command

Six commands drive bindify. Each one is a self-contained markdown file in `references/commands/`. Read the full command file before executing it.

| User signal | Command | Reference file |
|---|---|---|
| "let's coordinate updates" / "update the coordinator" | `coordinate-updates` | `references/commands/coordinate-updates.md` |
| "save this as a plan" / planning discussion just finished | `save-agent-plan` | `references/commands/save-agent-plan.md` |
| "run step N" / "execute Step-003" / orchestrator delegating a step | `iterate-planning-mode` | `references/commands/iterate-planning-mode.md` |
| Right after a step finishes, before moving on | `summarize-work-for-updates` | `references/commands/summarize-work-for-updates.md` |
| All steps done, ready for human review | `generate-verify` | `references/commands/generate-verify.md` |
| "research the codebase" before proposing | `research-codebase` | `references/commands/research-codebase.md` |

## The pipeline

```
human + agent dialogue
        ↓
   brief.md          ← human + AI discussion captures problem, goals, constraints
        ↓
   proposal.md       ← AI proposes approach + options; human reviews and annotates
        ↓
   plan.md           ← AI generates from approved proposal; source of truth for execution
        ↓
   updates.md        ← executor appends after each step (append-only)
        ↓
   verify.md         ← generated from updates; human checklist
```

Alongside this pipeline, `coordinator.md` runs in parallel as a conversation journal — the human triggers `coordinate-updates` at any point to record what was discussed and decided.

## Folder layout

```
.bindify/
├── AGENTS.md                          ← root instructions for any agent entering the repo
├── commands/                          ← the six command files (this skill mirrors them)
├── templates/                         ← brief, proposal, coordinator, verify templates
├── docs/                              ← cross-feature reference docs (event schemas, etc.)
└── development/
    ├── features/   (commit type: feat:)
    ├── fixes/      (commit type: fix:)
    ├── refactor/   (commit type: refactor:)
    └── chore/      (commit type: chore:)
        └── <feature-name>/
            ├── coordinator.md          ← human dialogue log, intent, pivots
            └── plans/
                └── <plan-name>/
                    ├── brief.md        ← phase 1: plan
                    ├── proposal.md     ← phase 2: propose + review
                    ├── plan.md         ← phase 3: apply (AI-generated)
                    ├── updates.md      ← append-only execution log
                    └── verify.md       ← phase 4: verify (human checklist)
```

## Two responsibilities

**Coordinator** — `<feature>/coordinator.md`. The human-facing journal. Captures the *why* — intent, decisions, pivots. Not machine-executable. Never modified during apply. Initialized and updated via `coordinate-updates`.

**Executor** — the pipeline inside `plans/<plan-name>/`. Agent-driven. Each phase has one source document and a clear owner:

| Phase | Document | Who drives |
|---|---|---|
| plan | `brief.md` | human + AI |
| propose | `proposal.md` | AI |
| review | `proposal.md` (annotated) | human |
| apply | `plan.md` + `updates.md` | AI via `iterate-planning-mode` |
| verify | `verify.md` | human checklist |

## Hard rules

These are violated often by agents who don't read this file. Don't be one of them.

- **Never modify `plan.md` during apply.** Execution state goes into `updates.md` only.
- **`updates.md` is append-only.** Initialize with a feature overview on first creation; never rewrite past entries.
- **Never introduce scope beyond the current step.** Note observations, don't act on them.
- **Repo-relative paths only.** Never absolute paths.
- **No code in context files.** File paths and symbol names only.
- **When in doubt, stop and ask.** Especially when required inputs are missing.

## Architecture: orchestrator + executors

Bindify is the glue between an orchestrator agent (Claude Code, Cursor) and executor agents (pi instances, often in Docker containers). The shared workspace — mounted into every container — is the entire communication channel.

```
Claude Code (orchestrator)
  ├─ runs coordinate-updates → writes coordinator.md
  ├─ runs save-agent-plan → writes plan.md
  ├─ spawns pi executor: pi -p "iterate-planning-mode Step-001"
  ├─ reads updates.md → decides next step
  └─ runs generate-verify when all steps done
```

Executors only need to know one thing per invocation: which `STEP_ID` in which `plan.md`. They read the step, do the work, append to `updates.md`, exit.

## Skill location: global vs project

Two natural placements, often used together:

- **Global** — `~/.bindify/` cloned on your machine, with `commands/`, `templates/`, and this skill. Shared across all projects.
- **Project-local** — `.bindify/` inside each repo, with `development/` and project history. Committed alongside the code.

Pi discovers skills by walking up the directory tree, so the global one is found from any project. The project-local `.bindify/` overrides or extends it.

## What to read next

- `references/AGENTS.md` — the canonical AGENTS.md to drop at the root of any bindify-managed repo
- `references/commands/<name>.md` — load on demand when invoking a command
- `references/templates/<name>.md` — load when creating a new brief, proposal, coordinator, or verify file

When invoking a command, **read the full command file first**. The summaries in this skill are signposts, not substitutes.
