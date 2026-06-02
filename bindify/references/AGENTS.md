# Bindify — Agent Guidelines

This file defines how AI agents operate inside the Bindify project.
Read this before doing anything else.

---

## Project structure

```
.bindify/
├── AGENTS.md                          ← you are here
├── commands/
│   ├── coordinate-updates.md
│   ├── save-agent-plan.md
│   ├── summarize-work-for-updates.md
│   ├── generate-verify.md
│   ├── research-codebase.md
│   └── iterate-planning-mode.md
└── development/
    ├── features/
    │   └── <feature-name>/
    │       ├── coordinator.md          ← human dialogue log, intent, pivots
    │       └── plans/
    │           └── <plan-name>/
    │               ├── brief.md        ← phase 1: plan
    │               ├── proposal.md     ← phase 2: propose + review
    │               ├── plan.md         ← phase 3: apply (AI-generated)
    │               ├── updates.md      ← append-only execution log (all steps)
    │               └── verify.md       ← phase 4: verify (human checklist)
    ├── fixes/
    ├── refactor/
    └── chore/
```

Same structure applies under `fixes/`, `refactor/`, and `chore/`.

---

## Two responsibilities

### 1. Coordinator
Human-driven. Lives at `<feature>/coordinator.md`.
Captures the *why* — dialogue summaries, decisions, pivots, current status.
Not machine-executable. Never modify it during apply phase.

The coordinator is not a phase in the pipeline — it is a conversation journal.
It is initialized and updated by the human at any point during a chat session
by invoking the `coordinate-updates` command. A typical trigger:

```
human chats freely with AI
        ↓
human says "okay let's plan"  →  brief.md + proposal.md created
        ↓
human says "okay let's coordinate updates"  →  coordinate-updates runs
        ↓
coordinator.md created or updated, plan linked
```

### 2. Executor
Agent-facing. The pipeline inside `plans/<plan-name>/`:

```
plan → propose → review → apply → verify
```

| Phase | Document | Who drives |
|---|---|---|
| `plan` | `brief.md` | human + AI discussion |
| `propose` | `proposal.md` | AI agent |
| `review` | `proposal.md` annotated | human |
| `apply` | `plan.md` + `updates.md` | AI agent via `iterate-planning-mode` |
| `verify` | `verify.md` | human checklist |

---

## Pipeline rules

- `brief.md` is the input to proposal generation — read it fully before proposing
- `proposal.md` must be reviewed and annotated by human before apply starts
- `plan.md` is AI-generated from the reviewed `proposal.md` — it is the source of truth for execution
- Never modify `plan.md` during apply — execution state goes into `updates.md` only
- `updates.md` is append-only and initialized with a short feature overview on first creation
- `verify.md` is generated after all steps are complete — derived from `updates.md` entries

---

## Core rules

- **Never introduce scope beyond the current step.** Note observations, don't act on them.
- **Never modify a `plan.md` while executing it.**
- **Always use repo-relative paths** in all output and reference files.
- **No code pasted into context files.** File paths and symbol names only.
- **When in doubt, stop and ask.**

---

## Commands

| Command | When to use |
|---|---|
| `coordinate-updates` | After any planning conversation — create or update coordinator.md |
| `save-agent-plan` | After planning-mode discussion — generate and save a plan markdown file in the correct feature path |
| `summarize-work-for-updates` | After completing any step — document what changed |
| `iterate-planning-mode` | When executing a specific step from `plan.md` |
| `generate-verify` | After all steps complete — generate human review checklist |
| `research-codebase` | If you need to investigate the codebase and detect patterns to implement the feature |

Read the full command file before using any command. They are in `.bindify/commands/`.

---

## Development categories

| Folder | Commit type | Use for |
|---|---|---|
| `features/` | `feat:` | New capabilities |
| `fixes/` | `fix:` | Bug fixes |
| `refactor/` | `refactor:` | Internal restructuring |
| `chore/` | `chore:` | Tooling, CI, config |

---

## What agents should always read first

1. This file
2. `coordinator.md` for the current feature — intent and history
3. The relevant `plan.md` before starting any step