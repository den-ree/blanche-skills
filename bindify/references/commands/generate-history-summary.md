# Command: generate-history-summary

Read a completed plan's execution evidence and produce a root-level history summary that is short, clear, and easy for humans or UI surfaces to scan.

This command creates or refreshes:
- `.bindify/history/entries/<date>-<slug>.md` — the full synthesized summary
- `.bindify/history/index.md` — a compact index entry pointing at that summary

`generate-history-summary` does not replace `updates.md`. It reads `updates.md` and related context, then turns that evidence into a concise narrative layer.

---

## When to use

- A product PR has been opened and the step work is already recorded in `updates.md`
- A merged branch needs its root history summary refreshed to reflect final status
- The UI needs a primary, visualization-friendly summary instead of the raw step log

Typical timing:
- `pr-open` mode: after PR creation, once `verify.md` exists and the plan is reviewable
- `merged` mode: after the branch is merged to `main`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `MODE` | yes | `pr-open` or `merged` |
| `PATH_TO_PLAN_MD` | yes | Repo-relative path to `plan.md` |
| `PATH_TO_UPDATES_MD` | yes | Repo-relative path to `updates.md` |
| `PATH_TO_BRIEF_MD` | yes | Repo-relative path to `brief.md` |
| `PATH_TO_VERIFY_MD` | no | Repo-relative path to `verify.md` if available |
| `PR_REF` | no | Product PR number or URL |
| `MERGE_REF` | no | Merge commit SHA, merge PR URL, or equivalent final merge reference |
| `RELATED_PATHS` | no | Additional repo-relative docs/research/history inputs that shaped the outcome |
| `ENTRY_SLUG` | no | Preferred history entry slug; infer from feature/plan if omitted |

---

## Placement rules

Write into the root history area, not inside a feature folder:

- Index: `.bindify/history/index.md`
- Full entry: `.bindify/history/entries/<date>-<slug>.md`

Naming guidance for entry files:
- Use the first generation date as the prefix: `<YYYY-MM-DD>-<slug>.md`
- Keep the slug stable when refreshing the same history entry after merge
- If multiple plans roll up into one summary, choose a shared outcome slug rather than a single feature name

---

## Procedure

1. **Load the execution evidence.**
   - Read `PATH_TO_UPDATES_MD` as the primary source of implementation evidence.
   - Read `PATH_TO_PLAN_MD` and `PATH_TO_BRIEF_MD` to recover scope and intended outcome.
   - Read `PATH_TO_VERIFY_MD` if present to capture human review framing.
   - Read `RELATED_PATHS` only when they materially shaped the story (research docs, architecture notes, linked feature docs).

2. **Determine the summary scope.**
   - Identify the main feature or change area.
   - Detect whether the work affects multiple features, shared modules, or cross-cutting docs.
   - Decide whether the history entry should name one feature or a broader outcome.

3. **Synthesize, do not restate.**
   - Compress all step entries into a short explanation of the combined result.
   - Focus on user-facing effect, architecture impact, and important follow-ups.
   - Do not repeat every step bullet-by-bullet.
   - Preserve backlinks to the most relevant step entries so readers can drill into the evidence.

4. **Write or refresh the full history entry.**
   - Create the entry if it does not exist.
   - If it already exists for the same slug, refresh it in place with the latest status and references.
   - In `pr-open` mode, status should clearly indicate review/open PR state.
   - In `merged` mode, status should clearly indicate merged/finalized state.

5. **Update the root index.**
   - Ensure `.bindify/history/index.md` exists.
   - Add or refresh one compact row/section for this history entry.
   - Keep the index brief; it is a discovery surface, not a duplicate of the full entry.

6. **Refresh links.**
   - Run `update-links` for `.bindify/history/`.
   - Ensure the history entry links back to plans, features, step logs, architecture objects, and related docs.

---

## Full entry requirements

The full history entry is the main human/UI summary and must be understandable without opening `updates.md`.

It should answer, quickly:
- What happened?
- Why does it matter?
- What changed in the architecture?
- Which features/docs/research were involved?
- Where can I drill down for evidence?

Mandatory qualities:
- Short, scannable prose and bullets
- Combined effect across steps, not a restated changelog
- Explicit architecture impact
- Explicit links to evidence and related materials
- Clear PR/merge state

---

## Output format: `.bindify/history/entries/<date>-<slug>.md`

```markdown
# History Summary — [Short outcome title]

**Status:** `pr-open` | `merged`
**Date:** YYYY-MM-DD
**Plan:** `development/<category>/<feature>/plans/<plan-name>/plan.md`
**Updates Log:** `development/<category>/<feature>/plans/<plan-name>/updates.md`
**PR:** <link or `none`>
**Merge:** <link/SHA or `pending`>

## What Changed
- <2-4 bullets describing the combined outcome>

## User / Feature Impact
- <what a human should understand about behavior, product surface, or workflow change>

## Architecture Impact
- `modified` [[architecture/modules/<object>]] — <what shifted>
- `touches` [[architecture/data/<object>]] — <why it matters>
- `created` [[architecture/modules/<object>]] — <if applicable>

## Evidence
- Step updates: `development/.../updates.md#<step-anchor>` — <why this step matters to the overall story>
- Plan: `development/.../plan.md`
- Verify: `development/.../verify.md`

## Related Features and Docs
- Features: `development/features/<other-feature>/...` — <if cross-feature>
- Docs/Research: `docs/<path>.md` — <if relevant>

## Follow-ups
- <only unresolved next actions or `none`>

## Related
- `[[../../development/.../plan.md]]`
- `[[../../development/.../updates.md]]`
- `[[../../development/.../verify.md]]`
- `[[../index.md]]`
```

---

## Output format: `.bindify/history/index.md`

Keep index entries compact. One entry should summarize the summary:

```markdown
## YYYY-MM-DD — [Short outcome title]

- Status: `pr-open` | `merged`
- Summary: <1-2 short bullets>
- Entry: `[[entries/<date>-<slug>.md]]`
- Plans: `development/.../plan.md`
- Features/Docs: `<optional cross-links>`
```

Do not copy the full history entry into the index.

---

## Hard rules

- **Never replace `updates.md` with this summary.** `updates.md` stays the append-only execution ledger.
- **Write root history only under `.bindify/history/`.** Do not place these summaries in feature folders.
- **One evolving entry per outcome.** Refresh the same entry for `pr-open` → `merged`; do not fork duplicate entries unless the work is genuinely a different outcome.
- **Synthesize across steps.** If the summary reads like a flattened changelog, it is wrong.
- **Preserve evidence links.** The summary must point back to plans, step logs, and related docs.
- **Repo-relative paths only.** No absolute paths in markdown.

---

## Acceptance criteria

- A summary entry exists under `.bindify/history/entries/`.
- `.bindify/history/index.md` contains a compact link to that entry.
- The entry clearly distinguishes `pr-open` vs `merged` status.
- The entry links back to the relevant plan and step evidence.
- The entry can reference multiple features and supporting docs when the outcome is cross-cutting.

---

## Related

- `[[references/commands/summarize-work-for-updates.md]]`
- `[[references/commands/generate-verify.md]]`
- `[[references/commands/log-pr.md]]`
- `[[references/docs/workflow.md]]`
