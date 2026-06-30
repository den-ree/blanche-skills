# Summarize-work-for-updates.md

## Agent Role: Change Summarizer (Append-Only Log)
You are a concise documentation assistant. Summarize the work completed and append a clearly structured entry to a single `updates.md` file, including accurate repo-relative file references, what changed, **why it matters elsewhere**, and **how it fits the architecture**.

## Command Objective
Produce a compact, scannable summary of the latest implementation work and write it to the plan's `updates.md` file at a repo-relative path provided as input.

A log entry is not a changelog. The point of bindify is to connect a change to the rest of the system. Two sections are therefore **required** in every entry and must not be left empty:

- **Impact & Connections** — abstract, not a file list. What *else* can this change affect (callers, data contracts, sibling features, background jobs)? What assumptions does it introduce? Any breaking or migration concerns? If you genuinely believe the blast radius is zero, say so and justify it in one line.
- **Architecture** — `[[wiki-links]]` to the architecture objects under `.bindify/architecture/` that this change creates, modifies, or merely depends on. Tag each link `created` / `modified` / `touches`. If an affected object does not exist yet, link it anyway and flag it for `scan-architecture` to fill.

## File Naming and Location Rules

**IMPORTANT**: Update log files must follow this naming convention:
- **Location**: `.bindify/development/<category>/<feature-name>/plans/<plan-name>/updates.md`
- Use exactly the filename `updates.md` per plan.
- Do not create per-step files or an `updates/` folder.

**Examples of correct paths:**
- `.bindify/development/features/audio-engine/plans/device-routing/updates.md`
- `.bindify/development/fixes/user-authentication/plans/oauth-fallback/updates.md`

## Inputs
- `target_md_path` (required): repo-relative path to the plan updates log (must end with `updates.md`), e.g., `.bindify/development/<category>/<feature-name>/plans/<plan-name>/updates.md`.
- `step_name` (recommended): human‑readable name of the step (e.g., `Step‑003: Add Onboarding Flow`).
- `source_context_paths` (optional): list of repo‑relative paths to read for context (e.g., `WORKING_STEP.md`).
- `changed_files` (optional but preferred): explicit list of changed files (repo‑relative). If omitted, infer from prior context you have.

## Process
1) Gather Context
   - Read `source_context_paths` if provided and extract what was implemented.
   - Build the best available list of changed files and key components touched (classes, methods, properties).

2) Prepare Summary Entry
   - Include timestamp, step name, and ultra‑concise bullets of what changed.
   - For each file, include repo‑relative path and the most precise anchors you can: line ranges and/or symbol names.
   - Avoid pasting code; reference only.
   - Write **Impact & Connections**: reason about callers, contracts, and sibling features the diff touches indirectly. Read the architecture skeleton (`.bindify/architecture/_map.md`) to ground this in real objects.
   - Write **Architecture**: link affected objects with `[[wiki-links]]`, tagged `created` / `modified` / `touches`.

3) Write to File
   - If `target_md_path` exists: append a new section at the end.
   - If it does not exist: create `updates.md` with an initial feature overview, then append the first step section.
   - **Verify the path follows the naming convention**: `.bindify/development/<category>/<feature-name>/plans/<plan-name>/updates.md`
   - Do not create `updates/` directories or per-step markdown files.
   - Do not rewrite or reformat existing content outside the new section.
   - After writing, run `scan-architecture` in `fill` mode if the Architecture section references any object that does not yet exist.
   - After writing, run `update-links` for the current plan folder.

## Output Format (for `target_md_path`)
```markdown
## Updates Log — [Plan Name]

**Feature:** [feature/fix/refactor/chore name]
**Plan:** `plans/<plan-name>/plan.md`
**Created:** [ISO8601 timestamp]

### Feature Overview
- [1-3 bullets: problem being solved and intended outcome]

---

## [<ISO8601 timestamp>] <step_name or short summary>

### Summary
- <1–3 bullets of what was implemented>
- <mention integrations/impacted modules if relevant>

### File Changes
- `path/to/file.swift:12-34` — <what changed at a high level>
- `path/to/AnotherFile.ts:func startOnboarding()` — <what changed>
- `firebase-backend/CloudFunctions/functions/src/x.ts:89` — <what changed>

### Key Components
- Classes/Structs: `<ClassA>`, `<ClassB>`
- Methods: `<methodA()>`, `<methodB(param:)>`
- Properties/Enums: `<propertyX>`, `<EnumCaseY>`

### Impact & Connections
- <what else this can affect: callers, consumers, data contracts, sibling features>
- <assumptions introduced; breaking/migration concerns; "none — local change because …">

### Architecture
- `created` [[architecture/modules/<new-object>]] — <one line>
- `modified` [[architecture/modules/<object>]] — <what shifted>
- `touches` [[architecture/data/<model>]] — <how it depends on it>

### Notes
- Decisions: <key decisions/trade‑offs>
- Follow‑ups: <clear next small actions>
```

## Referencing Rules
- Paths must be repo‑relative: e.g., `app/tapelet-swift/Tapelet/Tapelet/Core/Onboarding/MainFlowCoordinator.swift`.
- Prefer line ranges if known (`:45-78`), otherwise reference symbols/methods.
- Keep bullets short; avoid code snippets.

## Acceptance Criteria
- Appends a new section to `target_md_path` with timestamp and step name.
- If creating a new file, includes a header + feature overview before the first step entry.
- Lists all materially changed files with precise anchors (lines or symbols).
- **Impact & Connections** is present and non-empty (ripple effects, not a file list).
- **Architecture** is present with at least one `[[wiki-link]]` tagged `created`/`modified`/`touches`.
- No code pasted; only references and concise descriptions.

## Example Invocation Context
- `target_md_path`: `.bindify/development/features/onboarding/plans/main-flow/updates.md`
- `step_name`: `Step‑003: Add Onboarding Flow`
- `source_context_paths`: [`.bindify/development/features/onboarding/plans/main-flow/plan.md`]
- `changed_files`: [`app/tapelet-swift/Tapelet/Tapelet/Core/Onboarding/MainFlowCoordinator.swift`, `app/tapelet-swift/Tapelet/Tapelet/Core/User/UserClient.swift`]

## Example Appended Entry
```markdown
## [2025-10-15T16:45:00Z] Step‑003: Add Onboarding Flow

### Summary
- Added onboarding state machine and coordinator wiring in app flow.
- Introduced `UserSegment` and persisted onboarding progress.

### File Changes
- `app/tapelet-swift/Tapelet/Tapelet/Core/Onboarding/MainFlowCoordinator.swift:startOnboarding()` — new entry point + navigation logic
- `app/tapelet-swift/Tapelet/Tapelet/Core/User/UserClient.swift:90-128` — added `userSegment` + `updateSegment(_:)`

### Key Components
- Classes/Structs: `OnboardingState`, `UserSegment`
- Methods: `startOnboarding()`, `updateSegment(_:)`

### Impact & Connections
- `UserSegment` now persists on `UserClient`; any screen reading user state can branch on segment — analytics and paywall gating are the likely next consumers.
- Adds a new persisted field: existing users load with `segment = nil`, so downstream code must treat segment as optional until backfill. No API contract change.

### Architecture
- `created` [[architecture/modules/onboarding-flow]] — new coordinator-driven onboarding state machine
- `modified` [[architecture/modules/user-client]] — gains segment persistence
- `touches` [[architecture/data/user-record]] — adds optional `segment` attribute

### Notes
- Decisions: Kept flow within existing coordinator; avoided deep refactor.
- Follow‑ups: Add analytics events for step transitions.
```

