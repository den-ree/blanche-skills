# Command: draft-brief

Create `brief.md` from planning discussion inputs and mark it ready for proposal generation.

---

## When to use

- A planning discussion is complete and the team wants a structured brief
- A new active feature is being initialized in `wip-docs/`
- The next action is to generate `proposal.md`

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` |
| `FEATURE_NAME` | yes | Feature folder name in kebab-case (destination metadata) |
| `PLAN_NAME` | yes | Plan folder name in kebab-case (destination metadata) |
| `DISCUSSION_SOURCES` | yes | Conversation context used to derive problem, goals, constraints, and success criteria |

---

## Output path

Write to:

```
wip-docs/brief.md
```

Active work is always flat under `wip-docs/` at the **host project root**. Do not write into `.bindify/` or `bindify/` during drafting. `CATEGORY` / `FEATURE_NAME` / `PLAN_NAME` are stored as header metadata for later migration.

---

## Procedure

Read `references/docs/working-style.md` first. User-facing chat is caveman. Questions in this command stay clear. `brief.md` stays normal prose.

1. Resolve output path
   - Validate `CATEGORY`, `FEATURE_NAME`, and `PLAN_NAME`
   - Ensure `wip-docs/` exists at the host project root (create if missing)
   - If `wip-docs/` already contains artifacts for a *different* feature/plan, stop and ask (one active feature at a time)

2. Clarify gate — required before any write
   - Run this even when the user sounds sure. Users often name a solution they do not need.
   - Skip a question only when the user already answered it in this conversation in their own words. An inference is not an answer.
   - Ask only the open items, then stop. Do not write `brief.md` in the same turn.
   - **Intention:** what should be true when this is done? Not which implementation they pictured.
   - **Necessity:** restate the solution they named. If a smaller change or something already in the repo covers the outcome, say that in one line and ask which they want. This is the ponytail "does this need to exist?" rung. Wait for the pick. Do not drop the request and do not keep the heavier one by default.
   - **Inputs:** non-goals, the check they will use to call it done, and any constraint or file still missing.
   - If intention, necessity, or the done check is still open after they answer, ask again. Leave `Status` as `draft` until those three are answered.

3. Gather source context
   - Read all `DISCUSSION_SOURCES`
   - An `investigate` note counts as a source. Use its **Brief seed** and **Related fixes**. Do not paste the note in as the brief
   - The clarify gate still runs. A brief seed is not a user answer
   - Capture only decisions the user actually made, including the necessity pick
   - Keep unresolved questions in `Open questions`

4. Populate brief template (Micro-Brief)
   - Use the **skill** template `references/templates/brief.md` (this skill install — not the project tracking folder)
   - Optionally read tracking `project/profile.md` and `architecture/_map.md` under `.bindify/` or `bindify/` for constraints/context only
   - Set header fields: `Category`, `Feature`, `Plan`, `Status`, word limit
   - Fill `Problem statement` (max 2 sentences), `Goals`, `Out of scope`, `Constraints`, `Inputs available`, `Success criteria`, `Open questions`
   - Enforce brevity: total body must stay under 150 words
   - Use strict bullet points; omit prose paragraphs
   - Set `Status` to `ready for proposal` only when the clarify gate has closed. Otherwise `draft`

5. Save markdown
   - Create `wip-docs/` if needed
   - Save plain markdown only to `wip-docs/brief.md`
   - Set `Status` to `ready for proposal` only after the clarify gate closed. Otherwise `draft`.

6. Run link maintenance
   - Invoke `update-links` for `wip-docs/`

---

## Guardrails

- Hard word limit: strictly ≤ 150 words
- Bullet-first: avoid discursive or narrative prose
- Use repo-relative paths only
- Do not invent decisions not in sources
- Do not include source code in `brief.md`
- Do not generate `proposal.md` or `plan.md` in this command
- Do not write into the Bindify tracking submodule for active WIP
- Do not look in tracking `.bindify/` / `bindify/` for brief templates or command specs — those are skill-only
- Do not skip the clarify gate because the request "seems clear" or the chat is short
- Do not write caveman prose into `brief.md`

---

## Acceptance criteria

- `wip-docs/brief.md` exists with `Category`, `Feature`, and `Plan` metadata
- Brief is complete enough for proposal generation and complies with the ≤150 word limit
- `Status` is `ready for proposal` only after intention, necessity, and the done check were answered by the user
- The brief records the necessity pick the user made, not an unstated assumption
- `update-links` has run for `wip-docs/`
