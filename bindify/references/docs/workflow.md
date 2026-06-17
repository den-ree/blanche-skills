# Bindify Workflow — Visual Reference

Load this document when setting up a new product, publishing plan branches, or repairing markdown links. Do not load it on every command invocation — use `SKILL.md` for the command table and canonical pipeline diagram.

---

## Repo and branch model

Bindify tracking runs in one dedicated repository per product. Product code may span multiple repos (frontend, backend, mobile). Plan steps reference which repo they touch via a `Project Repo:` field in `plan.md`.

```mermaid
flowchart LR
    subgraph bindifyRepo [Bindify_repo]
        mainBranch["main\nstable history"]
        planBranch["plan/plan-name\nactive work"]
        devFolder[".bindify/development/"]
    end

    subgraph productRepos [Product_repos]
        frontend["frontend"]
        backend["backend"]
        mobile["mobile"]
    end

    mainBranch -->|"publish-plan creates"| planBranch
    planBranch -->|"commits updates and hotfixes"| planBranch
    planBranch -->|"after verify sign-off"| mainBranch

    planBranch --> devFolder
    devFolder --> planFiles["features/feature/plans/plan-name/\nbrief proposal plan updates verify"]
    devFolder --> fixFiles["fixes/feature/hotfixes.md"]

    planFiles -.->|"Project Repo per step"| frontend
    planFiles -.->|"Project Repo per step"| backend
    planFiles -.->|"Project Repo per step"| mobile
```

**Branch rules:**

- `main` — stable merged history only.
- `plan/<plan-name>` — created by `publish-plan` from an approved `plan.md`.
- Executor updates and hotfix logs commit to the active plan branch.
- Merge to `main` only after human sign-off on `verify.md`.

---

## Markdown link graph

Bindify markdown files form an Obsidian-compatible graph. Use inline `[[wiki-links]]` and a `## Related` section at the bottom of each file. Run `update-links` after any command that writes markdown.

```mermaid
flowchart TD
    coordinator["coordinator.md"]
    brief["brief.md"]
    proposal["proposal.md"]
    plan["plan.md"]
    updates["updates.md"]
    verify["verify.md"]
    hotfixes["hotfixes.md"]
    updateLinksCmd["update-links"]

    coordinator <-->|"wiki-links"| brief
    brief <-->|"wiki-links"| proposal
    proposal <-->|"wiki-links"| plan
    plan <-->|"wiki-links"| updates
    updates <-->|"wiki-links"| verify
    hotfixes <-->|"wiki-links"| plan
    hotfixes <-->|"wiki-links"| coordinator

    updateLinksCmd -->|"maintains links and Related"| brief
    updateLinksCmd -->|"maintains links and Related"| proposal
    updateLinksCmd -->|"maintains links and Related"| plan
    updateLinksCmd -->|"maintains links and Related"| updates
    updateLinksCmd -->|"maintains links and Related"| verify
    updateLinksCmd -->|"maintains links and Related"| hotfixes
    updateLinksCmd -->|"maintains links and Related"| coordinator
```

---

## Orchestrator vs executor

The orchestrator (Claude Code, Cursor) drives planning and delegates step execution. Executors (pi instances) run one step per invocation against the shared workspace.

```
Claude Code (orchestrator)
  ├─ runs coordinate-updates → writes coordinator.md
  ├─ runs draft-brief + generate-proposal + save-agent-plan
  ├─ runs publish-plan → creates branch plan/<plan-name>
  ├─ spawns pi executor: pi -p "iterate-planning-mode Step-001"
  ├─ reads updates.md → decides next step
  └─ runs generate-verify when all steps done
```

```mermaid
sequenceDiagram
    participant Human
    participant Orchestrator
    participant Executor
    participant BindifyRepo

    Human->>Orchestrator: planning dialogue
    Orchestrator->>BindifyRepo: draft-brief, generate-proposal, save-agent-plan
    Human->>Orchestrator: approve proposal
    Orchestrator->>BindifyRepo: publish-plan creates plan branch
    loop each Step_ID
        Orchestrator->>Executor: iterate-planning-mode Step-N
        Executor->>BindifyRepo: code changes + summarize-work-for-updates
    end
    Orchestrator->>BindifyRepo: generate-verify
    Human->>Orchestrator: sign off verify.md
    Orchestrator->>BindifyRepo: merge plan branch to main
```

**Executor contract:** read `STEP_ID` from `plan.md`, execute only that step's tasks, append to `updates.md`, exit. Never modify `plan.md` during apply.
