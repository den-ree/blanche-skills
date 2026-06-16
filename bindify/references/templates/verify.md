# Verify — [Plan Name]

**Plan:** `plans/<plan-name>/plan.md`  
**Generated:** YYYY-MM-DD  
**Status:** `pending` | `in review` | `passed` | `issues found`

---

## How to use this file

This checklist was generated from `updates.md` entries after all steps completed.
Go through each file, open it, and check the box when satisfied.
Add a note if something needs fixing — then decide whether it's a new `fix/` or an additional step.

---

## Files to review

<!-- Generated from updates.md step entries. Each file that was created or modified appears here. -->

### [Step 1 name]

- [ ] `path/to/file.swift`  
  _Why: New `TokenRefreshHandler` added — verify error path handles expired tokens correctly_

- [ ] `path/to/other.swift`  
  _Why: `AuthManager.init` modified — check it doesn't break existing call sites_

---

### [Step 2 name]

- [ ] `path/to/file.ts`  
  _Why: New Firebase callable — verify input validation and error response shape_

---

## Overall checklist

- [ ] All steps have a corresponding `updates.md` entry
- [ ] No unresolved notes flagged in any update
- [ ] Success criteria from `brief.md` are met
- [ ] No new scope was introduced during apply

---

## Outcome

**Result:** `passed` | `issues found`

**Issues:**
_List anything that needs follow-up. Each issue should become a new entry in `fixes/` or a new plan step._

- [ ] Issue: ...  
  → Action: ...

---

## Related

- `[[plan.md]]`
- `[[updates.md]]`
- `[[../coordinator.md]]`
