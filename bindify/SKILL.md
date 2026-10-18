---
name: bindify
description: Bindify is a filesystem-based protocol for coordinating AI agents on software work. Use this skill when the user references `wip-docs/`, `.bindify/`, bindify commands, plan/proposal/update/verify artifacts, coordinator workflows, multi-agent execution with shared markdown state, iterate-planning-mode, prototype-mode, or verify-worktree. Also use when drafting a brief, when the user may be asking for work they do not need, when investigating a feature or fix, when looking up prior fixes before researching code, or when bindify chat, planning, and implementation should follow caveman and ponytail.
---

# Bindify

Bindify is a filesystem-based communication protocol for AI agents working on software. **Active feature work lives in a flat `wip-docs/` folder at the project root** so agents can reliably read and write planning artifacts. The Bindify tracking repo (`.bindify/` or `bindify/` — often a submodule) holds architecture, completed plans, and an Obsidian-friendly `history/` brain — cards may appear when a draft plan PR opens; plans migrate into `development/` at packaging.

Read this whole file when bindify is in play; load command/template files from this skill's `references/` on demand.

## Three path layers (do not confuse)

| Layer | Where | What lives there | Agent rule |
|---|---|---|---|
| **Skill** | Installed skill (e.g. `~/.agents/skills/bindify/`) | `SKILL.md`, `references/commands/`, `references/templates/` | **How to run bindify.** Always read commands and templates from here. Never look inside the project tracking folder for command specs or templates. |
| **Active WIP** | `<project-root>/wip-docs/` | `brief.md`, `proposal.md`, `plan.md`, `updates.md`, `verify.md`, `coordinator.md` | **Write active feature docs here.** Flat; one feature at a time. |
| **Tracking repo** | `<project-root>/.bindify/` **or** `<project-root>/bindify/` (folder or submodule) | `development/`, `architecture/`, `history/`, `project/` | **Durable project memory.** Read `project/` and `architecture/` for context. Write migrated plans into `development/` at packaging time. Exception: `history/` may be written as soon as a draft plan PR exists so the vault shows live work. |

Example: `draft-brief` → read template from **skill** `references/templates/brief.md` → optionally read **tracking** `project/profile.md` / `architecture/_map.md` for context → write **`wip-docs/brief.md`**. Do **not** open `.bindify/commands/` or `.bindify/templates/` expecting skill implementation.

Resolve tracking root as: explicit path → `.bindify/` if present → `bindify/` if present → ask if neither.

## When to invoke each command

These commands drive bindify. Each one is a self-contained markdown file in `references/commands/`. Read the full command file before executing it. Prototype mode and macOS worktree verification are commands of this skill, not separate skills.

| User signal | Command | Reference file |
|---|---|---|
| "adapt bindify to this project" / "add a dev server command" / first-time setup in a repo | `configure-project` | `references/commands/configure-project.md` |
| "let's coordinate updates" / "update the coordinator" | `coordinate-updates` | `references/commands/coordinate-updates.md` |
| "capture this planning context as a brief" | `draft-brief` | `references/commands/draft-brief.md` |
| "generate proposal from this brief" | `generate-proposal` | `references/commands/generate-proposal.md` |
| "save this as a plan" / proposal has been approved | `save-agent-plan` | `references/commands/save-agent-plan.md` |
| "/bindify" / "publish this plan" / kick off product plan branch | `publish-plan` | `references/commands/publish-plan.md` |
| "run step N" / "execute Step-003" / "/iterate-planning-mode" / orchestrator delegating a step | `iterate-planning-mode` | `references/commands/iterate-planning-mode.md` |
| "review the open plan PR" / ready-for-review on `plan/*` | `review-plan` | `references/commands/review-plan.md` |
| "prototype this" / "/prototype-mode" / Step-001 UI mock before real wiring | `prototype-mode` | `references/commands/prototype-mode.md` |
| "verify this branch" / "/verify-worktree" / open or test an agent branch on macOS | `verify-worktree` | `references/commands/verify-worktree.md` |
| Right after a step finishes, before moving on | `summarize-work-for-updates` | `references/commands/summarize-work-for-updates.md` |
| "scan the architecture" / "build the architecture map" / missing arch object | `scan-architecture` | `references/commands/scan-architecture.md` |
| "log this PR" / ingest a PR into the tracking history | `log-pr` | `references/commands/log-pr.md` |
| "generate the final summary" / "refresh history after PR" / "prepare the UI summary" / draft-PR in-progress card | `generate-history-summary` | `references/commands/generate-history-summary.md` |
| "refresh the overview" / "open the overview" / rebuild the history dashboard | `regenerate-overview` | `references/commands/regenerate-overview.md` |
| "open a bindify PR" / publish logs to the `.bindify` submodule | `publish-bindify-pr` | `references/commands/publish-bindify-pr.md` |
| All steps done, ready for human review | `generate-verify` | `references/commands/generate-verify.md` |
| "investigate this" / "what did we already fix" / research a feature or fix before a brief | `investigate` | `references/commands/investigate.md` |
| "research the codebase" before proposing | `research-codebase` | `references/commands/research-codebase.md` |
| "repair links/backlinks after edits" | `update-links` | `references/commands/update-links.md` |
| "log an unplanned bugfix" | `log-hotfix` | `references/commands/log-hotfix.md` |

## The pipeline

```mermaid
flowchart TD
    dialogue["human + agent dialogue"]
    draftBrief["draft-brief"]
    briefMd["wip-docs/brief.md"]
    genProposal["generate-proposal"]
    proposalMd["wip-docs/proposal.md"]
    humanApproval["human approval"]
    savePlan["save-agent-plan"]
    planMd["wip-docs/plan.md"]
    publishPlan["publish-plan"]
    planBranch["feature/ + plan/ draft PR into feature"]
    historyInProgress["history card in-progress"]
    iterate["iterate-planning-mode"]
    summarize["summarize-work-for-updates"]
    updatesMd["wip-docs/updates.md"]
    genVerify["generate-verify"]
    verifyMd["wip-docs/verify.md"]
    prReady["mark draft PR ready for review"]
    reviewPlan["review-plan"]
    fixesDraft["plan-fixes draft into plan branch"]
    migrate["publish-bindify-pr migrates wip-docs"]
    genHistory["generate-history-summary"]
    historyIndex["history/index.md"]
    historyEntry["history/entries/<date>-<slug>.md"]
    humanSignoff["human sign-off"]
    mergeMain["merge to main"]

    coordinate["coordinate-updates"]
    investigate["investigate"]
    logHotfix["log-hotfix"]
    updateLinks["update-links"]

    dialogue --> draftBrief
    draftBrief --> briefMd
    briefMd --> genProposal
    genProposal --> proposalMd
    proposalMd --> humanApproval
    humanApproval --> savePlan
    savePlan --> planMd
    planMd --> publishPlan
    publishPlan --> planBranch
    planBranch --> historyInProgress
    historyInProgress --> historyEntry
    historyInProgress --> historyIndex
    planBranch --> iterate
    iterate --> summarize
    summarize --> updatesMd
    updatesMd -->|"more steps"| iterate
    updatesMd -->|"all steps done"| genVerify
    genVerify --> verifyMd
    verifyMd --> prReady
    prReady -->|"head plan/"| reviewPlan
    prReady -->|"head plan-fixes/"| humanSignoff
    reviewPlan -->|"clean"| humanSignoff
    reviewPlan -->|"in-scope misses"| fixesDraft
    fixesDraft --> historyInProgress
    fixesDraft --> iterate
    humanSignoff --> migrate
    migrate --> genHistory
    genHistory --> historyEntry
    genHistory --> historyIndex
    historyEntry --> mergeMain
    mergeMain --> genHistory

    dialogue -.-> coordinate
    dialogue -.-> investigate
    investigate -.->|"brief seed"| draftBrief
    iterate -.-> logHotfix
    briefMd -.-> updateLinks
    proposalMd -.-> updateLinks
    planMd -.-> updateLinks
    updatesMd -.-> updateLinks
    verifyMd -.-> updateLinks
    historyIndex -.-> updateLinks
    historyEntry -.-> updateLinks
```

Alongside this pipeline, `wip-docs/coordinator.md` runs in parallel as a conversation journal. Unplanned fixes may still land under the Bindify repo's `development/fixes/`. Tracking `history/` is the Obsidian brain layer: short property-backed cards plus a status-grouped index. Cards appear as `in-progress` when the draft plan PR opens, then refresh through `pr-open` and `merged`.

`investigate` stays off this pipeline. It lists tracking feature-folder names, reads related fixes, and only then looks at product code. Its **Brief seed** is `DISCUSSION_SOURCES` for `draft-brief`. It does not write the brief.

## Active work: `wip-docs/`

Why a flat root folder? The Bindify tracking repo is often a **nested git repo / submodule** (`.bindify/` or `bindify/`). Many agents cannot reliably read or write inside submodule boundaries or hidden dot-directories during feature work. `wip-docs/` stays in the **host project root** so every agent can see the active plan.

```
<project-root>/
├── wip-docs/                          ← ACTIVE feature only (flat; host repo)
│   ├── coordinator.md                 ← human dialogue log for this feature
│   ├── brief.md
│   ├── proposal.md
│   ├── plan.md
│   ├── updates.md                     ← append-only execution log
│   └── verify.md
├── .bindify/   or   bindify/          ← durable tracking repo (often a submodule)
│   ├── ...
│   └── development/...                ← destination after migration
└── ... product source ...
```

Rules for `wip-docs/`:

- **One active feature at a time.** Flat layout — no nested category/feature/plan folders while WIP.
- Every artifact must carry **Category**, **Feature**, and **Plan** metadata in its header so migration knows the destination path.
- Agents plan and execute **only** against `wip-docs/*` until packaging.
- On `publish-bindify-pr` / `log-pr`, docs migrate into the Bindify repo under `development/<category>/<feature-name>/plans/<plan-name>/`, the coordinator merges into the feature folder, then `wip-docs/` is removed from the host root.

## Folder layout (Bindify tracking repo)

Durable project memory only. Path may be `.bindify/` or `bindify/`. This is **not** the skill install — do not expect `commands/` or skill `templates/` here.

```
.bindify/   (or bindify/)
├── project/                           ← host-project adaptation
│   ├── profile.md                     ← stack, category, conventions, constraints
│   ├── environment.md                 ← how to start/run/verify this repo
│   ├── local.md                       ← machine-local overrides (gitignored)
│   └── commands/                      ← optional *project* command overrides (not skill commands)
│       └── start-dev.md
├── history/
│   ├── index.md
│   └── entries/
│       └── <date>-<slug>.md
├── architecture/
│   ├── _map.md
│   ├── system/<name>.md
│   ├── modules/<name>.md
│   ├── data/<name>.md
│   └── standards/<name>.md
└── development/
    ├── features/
    │   └── <feature-name>/
    │       ├── coordinator.md          ← merged from wip-docs on promote
    │       └── plans/
    │           └── <plan-name>/
    │               ├── brief.md
    │               ├── proposal.md
    │               ├── plan.md
    │               ├── updates.md
    │               └── verify.md
    ├── fixes/
    │   └── <feature-name>/
    │       └── hotfixes.md
    ├── refactor/
    └── chore/
```

Canonical command specs and templates always come from the **skill** (`references/commands/`, `references/templates/`), not from this tracking tree.

## Two responsibilities

**Coordinator** — `wip-docs/coordinator.md` while active; after migration, `<feature>/coordinator.md` in the Bindify repo. Human-facing journal via `coordinate-updates`.

**Executor** — the pipeline inside `wip-docs/` (then the migrated plan folder). Agent-driven. Each phase has one source document and a clear owner:

| Phase | Document | Who drives |
|---|---|---|
| plan | `wip-docs/brief.md` | human + AI |
| propose | `wip-docs/proposal.md` | AI |
| review | `wip-docs/proposal.md` (annotated) | human |
| apply | `wip-docs/plan.md` + `wip-docs/updates.md` | AI via `iterate-planning-mode` |
| verify | `wip-docs/verify.md` | human checklist |
| review | open `plan/` or `plan-iteration-N/` PR | AI via `review-plan` (append-only fix steps on `plan-fixes/`) |
| migrate | copy into Bindify `development/...` + remove `wip-docs/` | AI via `publish-bindify-pr` / `log-pr` |
| summarize-for-history | `.bindify/history/index.md` + `.bindify/history/entries/<date>-<slug>.md` (property-backed cards; may start at draft PR) | AI via `generate-history-summary` / `publish-plan` handoff |

## Architecture object graph

Bindify models the system itself as a web of typed **objects** under `.bindify/architecture/` — one markdown
file per object, linked by `[[wiki-links]]`, browsable like Capacities. Markdown is the source of truth.

Object types: `system`, `module`, `service`, `data-model`, `integration`, `pattern`, `standard`. Edges are
derived from the **Depends on** (`depends-on`), **Used by** (`used-by`), and **Standards & patterns** (`follows`)
sections of each object file.

`scan-architecture` builds a small, reliable skeleton first (`bootstrap`), then fills it in incrementally
(`fill`) as changes land. **Responsibility is stable; fill only appends change-log lines and adds edges.**

## Logs connect changes to architecture

A log is not a changelog. Every `updates.md` entry must carry an **Impact & Connections** section (abstract
ripple effects — what else the change can affect) and an **Architecture** section (`[[wiki-links]]` to the
objects it `created` / `modified` / `touches`). This is what turns the log into a connected graph instead of a
flat history.

`updates.md` is still the execution ledger, not the best user-facing overview. Root history cards are a
separate layer: YAML properties for tags and links, a short readable body with aliased `[[wiki-links]]`, and
`history/index.md` rebuilt into In progress / In review / Done for agents and UI surfaces.

## PR-driven logging flow

Each PR is a unit of change. The vision flow:

1. Human + agent plan a feature at a high level → write into `wip-docs/` (`coordinator.md` + `brief.md` + `proposal.md`).
2. After approval, `save-agent-plan` writes `wip-docs/plan.md`. `publish-plan` reads the current branch and stacks branches: from `main` or `release/*` it creates `feature/<feature-slug>`, then `plan/<plan-slug>` from that feature branch, and opens a **draft** PR into the feature branch (not into `main` or `release/*`). From an existing `feature/*` it only creates `plan/<plan-slug>` into that feature. From a `plan/` or `plan-iteration-N/` branch that already has a PR, the same plan continues as `plan-iteration-N/<leaf>` targeting that branch. After the draft URL exists, it upserts an `in-progress` history card under tracking `history/` (not `development/`) and pushes that history commit without bumping the product submodule pointer.
3. The **planner** agent that ran `publish-plan` **stops and waits** for the draft to become ready for review. A **separate executor** agent (draft-created trigger) runs `iterate-planning-mode` against `wip-docs/plan.md`; each step appends to `wip-docs/updates.md`.
4. When every step has an updates entry, the executor finish path runs `generate-verify` and marks the draft PR **ready for review** (`gh pr ready`). The executor stops. It does not keep committing on the draft head (`plan/<leaf>` or `plan-iteration-N/<leaf>`).
5. A **reviewer** agent runs `review-plan` on that ready PR when the head is `plan/<leaf>` or `plan-iteration-N/<leaf>`. It compares the diff to the brief, the plan, and `updates.md`. Improvements are a PR comment only. In-scope misses (unmet done criteria, unmet brief success criteria, missing or wrong planned behavior) are appended as new steps — existing steps stay unchanged — on a `plan-fixes/` branch. That branch gets one **draft** PR whose base is the reviewed head, not `feature/*`, `main`, or `release/*`. This round happens once. The same history card stays `in-progress` with `pr` updated to the fixes draft.
6. Draft-created on `plan-fixes/*` starts the executor again, only for the new steps. The finish path marks **that** draft ready. `ready_for_review` on `plan-fixes/*` does not start another reviewer. A human merges the fixes PR into the plan branch, or reviews the plan PR directly when `review-plan` found nothing to schedule.
7. Once the product PR is ready/merged as appropriate, `log-pr` / `publish-bindify-pr` **migrates** `wip-docs/` into the Bindify tracking repo under `development/<category>/<feature>/plans/<plan>/`, merges `coordinator.md`, rewrites the history card's `plan` / `updates` links off `wip-docs/`, and deletes `wip-docs/`.
8. `generate-history-summary` refreshes the same root history card in `pr-open` mode and rebuilds `history/index.md` under **In review**.
9. `log-pr` records alignment against `standard`/`pattern` objects and runs `scan-architecture fill`.
10. After merge, `generate-history-summary` runs again in `merged` mode so the card moves to **Done**. Each history-summary run also rebuilds `<tracking-root>/overview.html`.
11. `publish-bindify-pr` opens a PR to the Bindify submodule with the migrated logs + architecture updates (history may already be on tracking `main` from earlier status writes).

## Hard rules

- **Active docs live in `wip-docs/` until migration.** Do not write active brief/proposal/plan/updates/verify/coordinator into tracking `development/` during apply.
- **Branch stack:** `main` or `release/*` → `feature/<feature-slug>` → `plan/<plan-slug>` (draft PR into the feature branch). Already on `feature/*` → `plan/<plan-slug>` into that feature. Already on `plan/<leaf>` or `plan-iteration-N/<leaf>` with a PR → next `plan-iteration-N/<leaf>` into that branch. Only `review-plan` may create `plan-fixes/`, and its draft PR targets the reviewed head. Executors never create a branch. Never create `feature/` from a `plan/` branch, and never open `plan/` into `main` or `release/*`.
- **Never modify existing plan steps during apply.** Execution state goes into `updates.md` only. After the plan PR is open, `review-plan` may append new steps on `plan-fixes/` only.
- **Every update entry needs Impact & Connections + Architecture sections.** No flat changelogs.
- **Architecture `Responsibility` is human-owned.** `scan-architecture fill` appends change-log lines and edges only — it never rewrites a responsibility.
- **`updates.md` is append-only.** Initialize with a feature overview on first creation; never rewrite past entries.
- **Root history is the Obsidian brain layer.** One card per outcome under `history/entries/`; properties hold tags and link roles; the body stays short with aliased wikilinks. `history/index.md` rebuilds into In progress / In review / Done. Cards may be written from draft PR time onward; refresh the same slug through `in-progress` → `pr-open` → `merged`.
- **`hotfixes.md` is append-only.** Log unplanned fixes; do not rewrite history.
- **Never introduce scope beyond the current step.** Note observations, don't act on them.
- **Word limits for planning:** `brief.md` must be ≤ 150 words. `proposal.md` must be ≤ 250 words.
- **Prototype-first:** For user-facing features, `Step-001` must be a mock UI / Workflow prototype to validate flow before real data/backend integration.
- **Repo-relative paths only.** Never absolute paths.
- **No code in context files.** File paths and symbol names only.
- **Investigate before the codebase.** For a feature or fix question, `investigate` scans tracking feature-folder names and reads related fixes before any product-code research. It does not write the brief.
- **Clarify before capture.** Before `brief.md`, and before writing any user decision the user has not stated, ask about intention, necessity, and missing inputs, then wait. See `references/docs/working-style.md`.
- **Chat is caveman.** User-facing replies follow [caveman](https://github.com/JuliusBrussee/caveman) full. Artifacts, commits, and PR text stay normal prose. Questions, security warnings, and irreversible confirmations stay unambiguous.
- **Plan and build with ponytail.** Proposals, plans, and implementation follow the [ponytail](https://github.com/DietrichGebert/ponytail) ladder. Planning asks before dropping a user request. An approved step is the scope; climb the ladder inside it.

## Architecture: orchestrator + executors

Bindify is the glue between an orchestrator agent (Claude Code, Cursor) and executor agents (pi instances, often in Docker containers). The shared workspace — mounted into every container — is the entire communication channel.

Executors only need to know one thing per invocation: which `STEP_ID` in which `plan.md`. They read the step, do the work, append to `updates.md`, exit.

The reviewer is a third role. After a `plan/<leaf>` or `plan-iteration-N/<leaf>` PR is ready, `review-plan` either comments that the plan is clean or appends in-scope fix steps and opens one `plan-fixes/` draft into that head. It does not implement. `ready_for_review` on `plan-fixes/*` goes to a human.

For the orchestrator vs executor model, see `references/docs/workflow.md`.

## Git tracking workflow

Two git surfaces, different jobs:

**Product repo**
- `publish-plan` commits `wip-docs/` on the implementation head and opens a **draft** PR into the immediate parent from the branch stack: `feature/<feature-slug>` when starting from `main` or `release/*` (the feature branch is created and pushed first, with no PR of its own), the current `feature/*` when already on one, or the current `plan/` / `plan-iteration-N/` branch when that head already has a PR (next head is `plan-iteration-N/<leaf>`). That draft is what starts **executor** agents.
- The **planner** that ran `publish-plan` does not implement. It waits until the draft is marked ready for review, then waits again while `review-plan` runs. If that opens a fixes draft, it waits until a human merges the fixes branch into the reviewed head.
- Do not use `main` or `release/*` as the plan PR base. A `plan/` or `plan-iteration-N/` head that has no PR yet is reused (retry), not turned into another iteration. A different plan while sitting on another plan branch is cut from `feature/<feature-slug>`, not from the current plan branch.
- Executors commit **one commit per plan step** on the draft-PR head that triggered them (`plan/<leaf>`, `plan-iteration-N/<leaf>`, or, for the review round, `plan-fixes/…`) via `iterate-planning-mode`, authored as `blanche <blanche@bindify.app>` (per-commit `--author`, never global git config). Never create a new branch during iterate.
- When the last unfinished step is done, `iterate-planning-mode` runs `generate-verify` (separate commit), pushes the same branch, then marks **that** draft PR **ready for review** (`gh pr ready`). After that, the head stays frozen so a fixes append can merge.
- `ready_for_review` on `plan/<leaf>` or `plan-iteration-N/<leaf>` starts `review-plan`. That command either comments that the plan is clean, or appends in-scope fix steps and opens one `plan-fixes/` draft into the reviewed head (not into `feature/*`, `main`, or `release/*`). `ready_for_review` on `plan-fixes/*` does not start another reviewer.
- Human sign-off on `wip-docs/verify.md` / the ready plan PR gates merge. When a fixes draft exists, merge it into the plan branch before that sign-off.

**Bindify tracking repo** (`.bindify/` or `bindify/`, often a submodule)
- `development/` stays untouched during apply.
- Exception: `history/` may be written and pushed to tracking `main` as soon as the draft plan PR exists (`publish-plan` / `review-plan` / `generate-history-summary`), without bumping the product submodule pointer.
- `publish-bindify-pr` / `log-pr` migrate completed WIP into `development/...`, refresh history/architecture, open a Bindify `log/pr-*` PR, and bump the submodule pointer.
- Tracking `main` holds live history cards plus durable migrated plans after those log PRs merge.

See `references/docs/workflow.md` for the repo and branch diagram.

## Markdown linking conventions

Bindify markdown files should be navigable as an Obsidian graph.

- Use inline `[[wiki-links]]` when referencing related docs.
- Maintain a `## Related` section at the bottom of each file — except history cards, which use YAML link properties plus aliased body links instead of a `## Related` dump.
- Run `update-links` after commands that write markdown files.

See `references/docs/workflow.md` for the markdown link graph diagram.

## Skill location: global vs project

Three distinct places — never treat the tracking submodule as the skill:

- **Skill install** — e.g. `~/.agents/skills/bindify/` with `SKILL.md` + `references/`. Source of all canonical commands and templates.
- **Project tracking** — `.bindify/` or `bindify/` inside the product repo (often a submodule) for `development/`, `architecture/`, `history/`, `project/`.
- **Active WIP** — `wip-docs/` at the host project root while a feature is in progress.

Pi discovers skills by walking up the directory tree, so the skill install is found from any project.

## Project adaptation layer

Host projects adapt Bindify via tracking `project/` (under `.bindify/` or `bindify/`), written by `configure-project`. That folder holds **project runtime context only** — not skill commands or templates.

- **Committed by default** (`profile.md`, `environment.md`, optional `project/commands/`) so teammates and CI agents share how to run the project.
- **Machine-local only:** `project/local.md` / `project/local.*` are gitignored; never put secrets in committed project docs — reference env file paths instead.
- **Resolution order for running the app:** tracking `project/environment.md` is source of truth for start/test/lint/build — agents must not guess. Optional `project/commands/<name>.md` may override a skill command of the same name for *this host project only*.
- Templates for new `profile.md` / `environment.md` come from the **skill** (`references/templates/project-*.md`), never from a mythical tracking `templates/` tree.

## What to read next

- `references/AGENTS.md` — concise entry-point rules for agents
- `references/docs/working-style.md` — clarify gate, caveman chat, ponytail planning and implementation
- `references/docs/workflow.md` — visual deep-dive (repo branches, link graph, orchestrator model)
- `references/commands/<name>.md` — load on demand when invoking a command
- `references/templates/<name>.md` — load when creating a new brief, proposal, coordinator, verify, history, hotfix, investigation, architecture, or project file

When invoking a command, **read the full command file first**. The summaries in this skill are signposts, not substitutes.
