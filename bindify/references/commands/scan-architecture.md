# Command: scan-architecture

Build and maintain the architecture object graph under `.bindify/architecture/`. Everything is an object;
edges between objects come from `[[wiki-links]]`. The graph is meant to be browsed like Capacities — a web of
typed, connected notes.

The cardinal rule: **build a small, reliable skeleton first, then fill it in incrementally.** Never try to
document the whole system in one pass. A correct 8-object graph beats a guessed 80-object one.

---

## Modes

| Mode | When | What it does |
|---|---|---|
| `bootstrap` | `architecture/` is empty or missing | Create the high-level skeleton only |
| `fill` | A log/PR references an object that is missing or changed | Add/update the affected objects + edges |

If `MODE` is not given: `bootstrap` when `architecture/` has no object files, otherwise `fill`.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `BINDIFY_ROOT` | no | Path to `.bindify` (default: discover in cwd) |
| `MODE` | no | `bootstrap` \| `fill` (inferred if omitted) |
| `SOURCE_REFS` | for `fill` | Repo-relative paths or PR ref whose changes drive the fill (e.g. an `updates.md` entry, a PR diff) |
| `TARGET_AREA` | no | Narrow a `fill` to one area when the change is large |

---

## Object types

`system`, `module`, `service`, `data-model`, `integration`, `pattern`, `standard`.

`pattern` and `standard` objects are first-class — they are what `log-pr` checks alignment against. Capture the
conventions the codebase actually follows (naming, layering, error handling, testing), not aspirational ones.

---

## bootstrap procedure

Run once per product.

1. Read top-level signals only: root `README`, build/config files, top-level source folders, and any
   existing `coordinator.md` intents. Do **not** read deep into implementation.
2. Create `architecture/_map.md` from `references/templates/architecture-map.md`. Fill **Overview** and
   **Layers** with what is unambiguous.
3. Create one `system` object and the **handful** of top-level `module` / `service` / `integration` objects
   that obviously exist. Each from `references/templates/architecture-object.md`. Stop at the level where you
   would have to guess — leave finer objects for `fill`.
4. Create the seed `standard` / `pattern` objects the codebase clearly follows.
5. Wire **Depends on** / **Used by** edges only where the relationship is obvious.
6. Set each object's **status** honestly (`stable` vs `evolving`).
7. Run `update-links`.

Bootstrap output should be small. If you have more than ~12 objects, you are decomposing too early.

---

## fill procedure

Run whenever a change references architecture that is missing or has shifted (usually invoked by
`log-pr` or `summarize-work-for-updates`).

1. Read `SOURCE_REFS` (the updates entry, PR diff, or steps file) and extract which objects the change
   `created` / `modified` / `touches`.
2. For each referenced object:
   - **Missing** → create it from the template. Write a stable **Responsibility**, set type/status/repo,
     and wire its obvious edges.
   - **Existing** → do **not** rewrite **Responsibility**. Append one line to its **Change log** referencing
     the plan/PR, and add any new edges to **Depends on** / **Used by** / **Standards & patterns**.
3. Keep `architecture/_map.md`'s **Top-level objects** index in sync — add new objects under the right type.
4. Maintain reciprocity: if A now depends-on B, ensure B lists A under **Used by**.
5. Run `update-links`.

---

## Hard rules

- **Append, don't rewrite.** In `fill`, only **Change log** and edge lists may grow; **Responsibility** is owned
  by humans and earlier scans.
- **One object per file.** Filename = object `id`.
- **No code.** Responsibilities and edges only — paths and symbol names at most.
- **Skeleton over completeness.** When unsure whether an object deserves its own file, leave it folded into its
  parent until a change forces it out.
- **Repo-relative paths only.**
- When the right decomposition is ambiguous, stop and ask rather than guessing the hierarchy.

---

## Acceptance criteria

- `bootstrap`: `_map.md` + a small, correct set of objects exist; edges resolve.
- `fill`: every object the source change referenced now exists; existing objects gained change-log lines and
  edges but kept their responsibilities; `_map.md` index updated.

---

## Related

- `[[references/templates/architecture-object.md]]`
- `[[references/templates/architecture-map.md]]`
- `[[references/commands/log-pr.md]]`
- `[[references/commands/summarize-work-for-updates.md]]`
