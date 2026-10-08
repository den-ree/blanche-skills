# Bindify Agent Skill

Filesystem-based coordination for AI agents working on software — brief, propose, plan, apply, and verify through structured markdown. **Active feature work lives in `wip-docs/` at the project root**; durable history migrates into a Bindify tracking repo (`.bindify/` or `bindify/`, often a submodule).

Compatible with any AI coding tool that supports the [Agent Skills open format](https://agentskills.io/home).

## Who this is for

- Teams running multi-agent workflows (orchestrator + executors) on shared repos.
- Developers who want durable, reviewable planning artifacts instead of chat-only context.
- Anyone using `wip-docs/`, Bindify tracking folders, coordinator/brief/proposal/plan/updates/verify files, or bindify commands.

## How to Use This Skill

### Option A: Using skills.sh

Install this skill with a single command:

```bash
npx skills add https://github.com/den-ree/bindify-skill --skill bindify
```

Then ask your agent to use the bindify skill, for example:

> Use the bindify skill and set up a new feature plan in this repo.

### Option B: Claude Code Plugin

#### Personal usage

1. Add the marketplace:

   ```bash
   /plugin marketplace add den-ree/bindify-skill
   ```

2. Install the skill:

   ```bash
   /plugin install bindify@bindify-skill
   ```

#### Project configuration

To provide this skill to everyone working in a repository, add `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "bindify@bindify-skill": true
  },
  "extraKnownMarketplaces": {
    "bindify-skill": {
      "source": {
        "source": "github",
        "repo": "den-ree/bindify-skill"
      }
    }
  }
}
```

### Option C: Using pi package manager

Install via [pi](https://github.com/mariozechner/pi-mono):

```bash
pi install https://github.com/den-ree/bindify-skill
```

The skill is available automatically in pi sessions.

### Option D: Manual install

1. Clone this repository.
2. Install or symlink the `bindify/` folder following your tool's skills installation docs:
   - [Codex: Where to save skills](https://developers.openai.com/codex/skills/#where-to-save-skills)
   - [Claude: Using Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
   - [Cursor: Enabling Skills](https://cursor.com/docs/context/skills#enabling-skills)
3. Ask your agent to use the **bindify** skill when coordinating multi-step work.

**How to verify:** Your agent should reference `bindify/SKILL.md`, load command files from `bindify/references/commands/` on demand, and follow the plan → propose → apply → verify pipeline.

## What This Skill Offers

Bindify is a filesystem protocol — no message queue, no HTTP. Agents communicate by reading and writing markdown. Active work stays in a flat, agent-readable `wip-docs/` folder; completed plans migrate into the Bindify tracking repo.

### Pipeline

```
human + agent dialogue
        ↓
   wip-docs/brief.md      ← problem, goals, constraints
        ↓
   wip-docs/proposal.md   ← approach + options; human reviews
        ↓
   wip-docs/plan.md       ← source of truth for execution
        ↓
   wip-docs/updates.md    ← append-only execution log
        ↓
   wip-docs/verify.md     ← human checklist
        ↓
   publish-bindify-pr     ← migrate into Bindify development/... and remove wip-docs/
```

`wip-docs/coordinator.md` runs in parallel as a conversation journal for intent, decisions, and pivots.

### Commands

| Command | Purpose |
|---|---|
| `coordinate-updates` | Update the feature coordinator journal |
| `save-agent-plan` | Persist a planning discussion as `plan.md` |
| `iterate-planning-mode` | Execute one step from `plan.md` |
| `summarize-work-for-updates` | Append step results to `updates.md` |
| `generate-verify` | Build a human verification checklist |
| `investigate` | Look up prior fixes in `.bindify/` before code research; seed a later brief |
| `research-codebase` | Research before proposing |

### Two placements (+ WIP)

- **Global skill** — install for shared commands and templates across projects.
- **Project tracking** — `.bindify/` or `bindify/` inside each product repo (often a submodule) for durable history, architecture, and completed plans.
- **Active WIP** — `wip-docs/` at the host project root while a feature is in progress.

## Skill Structure

```
bindify/
├── SKILL.md                           # Main skill: pipeline, rules, command index
└── references/
    ├── AGENTS.md                      # Drop-in AGENTS.md for bindify-managed repos
    ├── commands/
    │   ├── coordinate-updates.md
    │   ├── save-agent-plan.md
    │   ├── iterate-planning-mode.md
    │   ├── summarize-work-for-updates.md
    │   ├── generate-verify.md
    │   ├── research-codebase.md
    │   └── investigate.md
    └── templates/
        ├── brief.md
        ├── proposal.md
        ├── coordinator.md
        ├── verify.md
        └── investigation.md
```

## License

MIT — see [LICENSE](LICENSE).
