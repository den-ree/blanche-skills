# Command: generate-verify

Read `updates.md` for a completed plan and generate a `verify.md` human review checklist.

This command prepares human review of the step-level execution evidence. It does not produce the root user-facing summary; that happens later via `generate-history-summary`.

---

## When to use

- All steps in `plan.md` are complete
- All steps have a corresponding entry in `updates.md`
- Ready to hand off: `review-plan` when the ready head is `plan/*`, or a human when the ready head is `plan-fixes/*`

`generate-verify` comes before root history summarization and WIP migration. The usual order is:
1. complete step work in `wip-docs/updates.md`
2. run `generate-verify` → `wip-docs/verify.md` (also invoked automatically from `iterate-planning-mode` finish path)
3. mark the product draft PR ready for review (`gh pr ready`) — done by `iterate-planning-mode` finish path
4. on a `plan/*` head, run `review-plan` (separate reviewer). A `plan-fixes/*` head stops here for a human — do not start another reviewer
5. migrate via `log-pr` / `publish-bindify-pr`
6. run `generate-history-summary`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `PATH_TO_PLAN_MD` | no | Defaults to `wip-docs/plan.md` |
| `PATH_TO_UPDATES_MD` | no | Defaults to `wip-docs/updates.md` |
| `PATH_TO_BRIEF_MD` | no | Defaults to `wip-docs/brief.md` — for success criteria |

---

## Procedure

1. Read `PATH_TO_PLAN_MD` — get the full list of steps
2. Read `PATH_TO_UPDATES_MD`
3. For each file listed in **File Changes** across all step sections:
   - Include the file path
   - Write one sentence explaining *why* it needs human review, derived from the update's Summary and Notes
   - Group entries by the step they came from
4. Read `PATH_TO_BRIEF_MD` — extract success criteria for the overall checklist
5. If `.bindify/project/environment.md` or `bindify/project/environment.md` exists, pull its Dev server and Verification commands into a short preamble on `verify.md` (how to start the app, open the URL, and which test/lint/build commands to run)
6. Write `verify.md` to `wip-docs/verify.md` using the template structure; include Category / Feature / Plan metadata from the brief/plan headers
7. Run `update-links` for `wip-docs/`
8. If invoked standalone (not already inside `iterate-planning-mode` finish path), remind the caller to mark the product draft PR ready for review — or run that finish path. On a ready `plan/*` head, the next agent is `review-plan`, not another pass of this command.

Do not attempt to replace `verify.md` with a broader narrative summary. `verify.md` stays focused on human review of changed files and success criteria.

---

## Output

Write to: `wip-docs/verify.md`

### Rules for the file review entries

- **One sentence per file** — what changed and what the human should look for
- Focus on: new logic, modified interfaces, error paths, side effects, anything flagged in update Notes
- Do not list files that were only renamed or had cosmetic changes unless flagged
- If a file appears in multiple steps, list it once under the step where the most significant change happened

### Rules for the checklist

- Derive the overall checklist items directly from `brief.md` success criteria
- Add a standard entry: "No new scope was introduced during apply"
- Do not invent criteria not present in the brief

---

## Relationship to root history

- `verify.md` is a review checklist derived from `updates.md` (still in `wip-docs/` until migration)
- After migration, history entries under the Bindify tracking repo synthesize the user/UI digest from the same evidence
- Both should link to the same plan evidence, but they serve different readers and should not duplicate each other

---

## Example output entry

```markdown
- [ ] `ios/App/Auth/TokenRefreshHandler.swift`  
  _Why: New handler added in step 2 — verify the expired token error path doesn't silently fail_
```
