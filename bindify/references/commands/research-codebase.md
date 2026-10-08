# Command: research-codebase

Research existing codebase architecture and conventions to support proposal and plan quality.

---

## When to use

- After `investigate`, for the code pass on paths that command already scoped
- Before generating `proposal.md` for non-trivial work, once prior fixes have been scanned
- When the feature touches unfamiliar modules or cross-repo boundaries
- When existing patterns are unclear and must be mapped first

For a named feature or fix, start with `investigate`. Do not open the product tree first.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `TARGET_AREA` | yes | Area to study (for example: `frontend`, `backend/auth`, `mobile/navigation`) |
| `RESEARCH_DEPTH` | yes | `surface` \| `deep` |
| `SPECIFIC_GOALS` | yes | What this research must enable (integration, migration, refactor, bugfix) |
| `CONTEXT` | no | Extra constraints, assumptions, or known limitations |

---

## Procedure

1. Confirm the tracking name scan already ran
   - If this research is for a feature or fix and `investigate` has not listed `.bindify/` or `bindify/` feature-folder names yet, run `investigate` first and return
   - Use paths from that note as `TARGET_AREA` when the caller did not pass one

2. Map architecture
   - Read README/config/build files relevant to `TARGET_AREA`
   - Identify key modules and boundaries

3. Extract implementation patterns
   - Review naming, file layout, and dependency patterns
   - Find similar features as implementation references

4. Document integration guidance
   - List required interfaces and extension points
   - Note testing and validation patterns used in this area

5. Produce concise report
   - Executive summary
   - Architecture overview
   - Key patterns
   - Integration guidelines
   - Key files with paths
   - Concrete recommendations

---

## Output format

Use markdown with short sections and bullets:

- Executive Summary
- Architecture Overview
- Implementation Patterns
- Integration Guidelines
- Key Files and Examples
- Recommendations

---

## Guardrails

- Do not modify files, run builds, or implement changes
- Avoid exhaustive line-by-line documentation
- Focus on actionable findings, not complete inventories
- Ignore deprecated paths unless they affect current integration
- If scope is too broad, ask for narrower `TARGET_AREA`

---

## Acceptance criteria

- Report addresses the stated `SPECIFIC_GOALS`
- Architecture and integration recommendations are actionable
- Key file references are included with repo-relative paths
- Output is concise and scannable