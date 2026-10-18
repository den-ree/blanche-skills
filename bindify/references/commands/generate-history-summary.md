# Command: generate-history-summary

Create or refresh a root-level history card that Obsidian and an agent can share: YAML properties for tags and links, a short readable body, one evolving file per outcome.

This command creates or refreshes (under the Bindify **tracking** root — `.bindify/` or `bindify/`):
- `history/entries/<date>-<slug>.md` — the history card (properties + short body)
- `history/index.md` — status-grouped discovery list rebuilt from entry properties

While a feature is still active, source evidence may still live in `wip-docs/`; after migration, read the plan under tracking `development/...`. Do not write history into `wip-docs/`.

`generate-history-summary` does not replace `updates.md`. It reads `updates.md` (or the brief, in `in-progress` mode) and turns that evidence into a concise card.

Use the skill template `references/templates/history-entry.md` for the card shape and `references/templates/history-index.md` for the index shape.

---

## When to use

- `publish-plan` has a draft PR URL and needs an `in-progress` card (handoff only; usually invoked from that command)
- A product PR is ready for review and the step work is recorded in `updates.md`
- A merged branch needs its root history card refreshed to reflect final status
- The UI / Obsidian vault needs a clean card instead of the raw step log

Typical timing:
- `in-progress` mode: right after the draft `plan/*` (or `plan-fixes/*`) PR URL exists
- `pr-open` mode: after the plan PR is ready for review, once `verify.md` exists
- `merged` mode: after the branch is merged to `main`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `MODE` | yes | `in-progress` \| `pr-open` \| `merged` |
| `PATH_TO_BRIEF_MD` | yes | Repo-relative path to `brief.md` |
| `PATH_TO_PLAN_MD` | yes for `pr-open` / `merged`; preferred for `in-progress` | Repo-relative path to `plan.md` |
| `PATH_TO_UPDATES_MD` | yes for `pr-open` / `merged`; optional for `in-progress` | Repo-relative path to `updates.md` |
| `PATH_TO_VERIFY_MD` | no | Repo-relative path to `verify.md` if available |
| `PR_REF` | no | Product PR number or URL (required in practice for `in-progress` / `pr-open`) |
| `MERGE_REF` | no | Merge commit SHA, merge PR URL, or equivalent final merge reference |
| `FEATURE_NAME` | no | Topic tag source; infer from WIP / plan headers when omitted |
| `ENTRY_SLUG` | no | Preferred history entry slug; infer from feature/plan if omitted |
| `AGENT` | no | Working agent label for in-progress chips (e.g. `blanche`); omit when unknown |

---

## Placement rules

Write into the tracking root history area (`.bindify/history/` or `bindify/history/`), not inside a feature folder or `wip-docs/`:

- Index: `history/index.md`
- Full entry: `history/entries/<date>-<slug>.md`

Naming guidance for entry files:
- Use the first generation date as the prefix: `<YYYY-MM-DD>-<slug>.md`
- Keep the slug stable across `in-progress` → `pr-open` → `merged`
- If multiple plans roll up into one summary, choose a shared outcome slug rather than a single feature name
- Never create a second entry for a `plan-fixes/*` draft — refresh the same slug and update `pr`

---

## Procedure

1. **Resolve the tracking root and existing card.**
   - Detect `.bindify/` then `bindify/`. Stop and ask if neither exists (except when invoked from `publish-plan`, which may skip the card — see that command).
   - Infer `ENTRY_SLUG` from `FEATURE_NAME` / plan name when omitted.
   - If `history/entries/*-<slug>.md` already exists, reuse that file (keep its date prefix). Do not fork a new date for status transitions.

2. **Load evidence for the mode.**
   - `in-progress`: read `PATH_TO_BRIEF_MD` (and `PATH_TO_PLAN_MD` when present). Do not require `updates.md`.
   - `pr-open` / `merged`: read `PATH_TO_UPDATES_MD` as the primary source; also read plan, brief, and `PATH_TO_VERIFY_MD` when present.

3. **Determine title, tags, and link roles.**
   - Title: short outcome title (not `History Summary — …`).
   - Tags: always include `history`; add lowercase topic tags from the feature name / brief (e.g. `auth`).
   - `plan` / `updates` properties: wikilinks to the current plan and updates files.
     - While still in `wip-docs/`: `[[plan]]` / `[[updates]]` (or paths that resolve to those WIP files).
     - After migration: point at the durable `development/...` plan and updates notes.
   - Architecture link roles (`touches` / `modified` / `created`): empty lists in `in-progress`; fill from Architecture sections in `updates.md` for `pr-open` / `merged`.

4. **Write the card body.**
   - `in-progress`: two or three sentences stating the intended outcome from the brief.
   - `pr-open` / `merged`: synthesize the combined result across steps — not a flattened changelog.
   - After the sentences, list architecture connections as aliased wikilinks only, matching the property lists:
     - `Touches [[session-store|Session store]].`
     - `Modified [[…|…]].` / `Created [[…|…]].` when applicable.
   - No status block, no path rows, no Evidence section, no `## Related` dump. Step evidence stays in `updates.md`.

5. **Write or refresh properties.**
   - `type: history`
   - `status`: `in-progress` | `pr-open` | `merged` matching `MODE`
   - `date`: keep the original entry date on refresh; set today only when creating
   - `pr`: URL string from `PR_REF`, or `""` when absent
   - `merge`: URL/SHA from `MERGE_REF` in `merged` mode; `""` otherwise
   - Keep property link lists and body aliases on the same targets

6. **Rebuild `history/index.md` from all entry properties.**
   - Ensure the file exists (under `.bindify/` or `bindify/`).
   - Scan every `history/entries/*.md` frontmatter.
   - Rebuild three sections only: **In progress**, **In review**, **Done**.
   - Map status → section: `in-progress` → In progress; `pr-open` → In review; `merged` → Done.
   - Each item is one line: `[[entries/<file>|Title]] — <topic tags>` plus `· #<pr-number>` and `· <agent>` when those values exist on the card.
   - Omit empty sections, or leave them with no bullets. Never put path rows or status words in the line body.

7. **Refresh links.**
   - Run `update-links` for tracking `history/` (history-card rules: sync properties with body aliases; do not add `## Related`).

8. **Rebuild the overview.**
   - Run `regenerate-overview` with `OPEN` false.
   - The dashboard is written to `<tracking-root>/overview.html` from the history cards and architecture graph just written.

---

## Card format: `history/entries/<date>-<slug>.md`

```markdown
---
type: history
status: in-progress
date: YYYY-MM-DD
tags:
  - history
  - <topic>
pr: "<url or empty>"
merge: ""
plan: "[[plan]]"
updates: "[[updates]]"
touches:
  - "[[object-id]]"
modified: []
created: []
---

# Short Outcome Title

Two or three sentences.

Touches [[object-id|Object Name]].
```

Properties are the contract for Obsidian / agents. The body is what humans read.

---

## Index format: `history/index.md`

```markdown
# History Index

## In progress

- [[entries/<date>-<slug>|Short Outcome Title]] — `<topic>` · `#<pr>` · `<agent>`

## In review

- [[entries/<date>-<slug>|Short Outcome Title]] — `<topic>` · `#<pr>`

## Done

- [[entries/<date>-<slug>|Short Outcome Title]] — `<topic>`
```

Do not copy the card body into the index. Do not list plan/updates paths.

---

## Hard rules

- **Never replace `updates.md` with this card.** `updates.md` stays the append-only execution ledger.
- **Write root history only under tracking `history/`** (`.bindify/history/` or `bindify/history/`). Do not place these cards in feature folders or `wip-docs/`.
- **One evolving entry per outcome.** Refresh the same file for `in-progress` → `pr-open` → `merged`; do not fork duplicates for `plan-fixes/*`.
- **`in-progress` body = intent; later modes = synthesized result.**
- **No path dumps in the body or index.** Paths belong in properties (`plan`, `updates`, `pr`, `merge`) or stay in `updates.md`.
- **No `## Related` on history cards.** Properties + aliased body links are the graph edges.
- **Repo-relative / vault-relative targets only.** No absolute paths in markdown.

---

## Acceptance criteria

- A card exists under tracking `history/entries/` with YAML properties and a short body.
- Tracking `history/index.md` groups the card under In progress / In review / Done from its `status`.
- The same slug is reused across status transitions.
- `pr-open` / `merged` cards synthesize outcomes and fill architecture link roles; `in-progress` cards use brief intent and may leave those lists empty.
- Property link lists and body aliases target the same objects.
- The card does not contain a status block, path rows, Evidence section, or `## Related` dump.
- `<tracking-root>/overview.html` was regenerated after the card and index write.

---

## Related

- `[[references/templates/history-entry.md]]`
- `[[references/templates/history-index.md]]`
- `[[references/commands/publish-plan.md]]`
- `[[references/commands/summarize-work-for-updates.md]]`
- `[[references/commands/generate-verify.md]]`
- `[[references/commands/log-pr.md]]`
- `[[references/commands/update-links.md]]`
- `[[references/commands/regenerate-overview.md]]`
