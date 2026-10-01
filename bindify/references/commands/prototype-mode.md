# Command: prototype-mode

Build a complete interactive UI slice with mock data so the full user journey can be reviewed before real services, persistence, or networking.

This is a bindify command. It is not a separate skill. Invoke it from the bindify skill when the user asks for a prototype, or when `iterate-planning-mode` is executing a step marked Prototype.

---

## When to use

- A new user-facing feature, usually `Step-001`
- The user asks to prototype first, build a UI mock, or run prototype mode
- UX flow, navigation, and component structure need review before API or database work

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `FEATURE` | yes | What the prototype covers |
| `ENTRY` | yes | First screen or route the user starts from |
| `JOURNEY` | yes | The path that must be clickable end to end |
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` when implementing a plan step |

---

## Procedure

Read `references/docs/working-style.md` first. The prototype is the lazy path: mock UI, no real services. Chat is caveman.

1. Implement the full journey from entry to completion
2. Use in-memory mock models or a stub store only
3. Keep every control interactive: buttons, forms, sheets, transitions
4. Separate presentation from the mock source (protocol, store, or observable state) so a later step can swap in the real implementation without redesigning views
5. Do not add database schemas, network clients, auth gates, or remote calls
6. If this implements a plan step, stop at that step's outputs and log with `summarize-work-for-updates`

---

## Done criteria

- The journey can be navigated from start to finish in preview, canvas, or simulator
- Diff is layout and interaction only
- The mock boundary is explicit enough for the next integration step to replace

---

## Guardrails

- Stub loading with instant success or a short simulated delay
- Do not start the integration step in the same invocation
- Reuse an existing screen or component before adding a new one
- Do not add a design system, state library, or mock framework for this slice
- On a Linux cloud agent, do not run `xcodebuild` or the simulator; leave that to `verify-worktree` on macOS
