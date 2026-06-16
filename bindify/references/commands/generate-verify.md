# Command: generate-verify

Read `updates.md` for a completed plan and generate a `verify.md` human review checklist.

---

## When to use

- All steps in `plan.md` are complete
- All steps have a corresponding entry in `updates.md`
- Ready to hand off to human for review

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `PATH_TO_PLAN_MD` | yes | Repo-relative path to `plan.md` |
| `PATH_TO_UPDATES_MD` | yes | Repo-relative path to `updates.md` |
| `PATH_TO_BRIEF_MD` | yes | Repo-relative path to `brief.md` — for success criteria |

---

## Procedure

1. Read `PATH_TO_PLAN_MD` — get the full list of steps
2. Read `PATH_TO_UPDATES_MD`
3. For each file listed in **File Changes** across all step sections:
   - Include the file path
   - Write one sentence explaining *why* it needs human review, derived from the update's Summary and Notes
   - Group entries by the step they came from
4. Read `PATH_TO_BRIEF_MD` — extract success criteria for the overall checklist
5. Write `verify.md` to the plan folder using the template structure
6. Run `update-links` for the current plan folder

---

## Output

Write to: `<plan-folder>/verify.md`

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

## Example output entry

```markdown
- [ ] `ios/App/Auth/TokenRefreshHandler.swift`  
  _Why: New handler added in step 2 — verify the expired token error path doesn't silently fail_
```
