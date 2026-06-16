# Command: coordinate-updates

Create or update `coordinator.md` for a feature by summarizing the current conversation.
Initiated by the human at any point during a chat session.

---

## When to use

- After any planning conversation — capture what was discussed and decided
- After `brief.md` or `proposal.md` was created — register the new plan
- After a plan step or full plan completes — record the outcome and update status
- Whenever the human says "let's coordinate updates" or "update the coordinator"

---

## Step 1 — Detect which path to take

Check if `coordinator.md` exists at:
```
.bindify/development/<category>/<feature-name>/coordinator.md
```

- **Does not exist** → follow the [Create path](#create-path)
- **Already exists** → follow the [Update path](#update-path)

---

## Create path

Run this when `coordinator.md` does not exist yet.

1. Create the feature folder: `.bindify/development/<category>/<feature-name>/`
2. Create `coordinator.md` using the template at `.bindify/templates/coordinator.md`
3. Fill **Intent** — what this feature is and why, inferred from the conversation
4. Write the first session log entry (see [Session entry format](#session-entry-format) below)
5. If a `brief.md` or `proposal.md` was created this session, add it to the **Plans** table with status `proposed`

---

## Update path

Run this when `coordinator.md` already exists.

1. Read the full existing `coordinator.md`
2. Read the current conversation — identify what is new since the last session entry
3. Write a new session log entry summarizing **only what happened in this conversation**
4. Prepend it at the top of the session log section (newest first)
5. Update the **Plans** table if any plan status changed this session
6. Update the top-level **Status** field if the feature moved to `paused` or `done`

**Never rewrite or remove existing session entries.** Append only.

---

## Session entry format

```markdown
### YYYY-MM-DD — [short title of what was discussed]

**Discussed:**
[What was talked about. Key questions raised. Context given to the AI.]

**Decided:**
[What was settled. Approach chosen. What was ruled out.]

**Pivots:**
[Anything that changed from a prior decision, and why. Omit if none.]

**Next:**
[What the human intends to do next.]

**Linked plan:** `plans/<plan-name>/` — `proposed` | `in progress` | `done`
[Omit if no plan was created or updated this session.]
```

---

## Summarization rules

- Summarize from the actual conversation — do not invent decisions not made
- Keep each section to 2–4 sentences maximum
- **Discussed** — the questions and context, not a transcript
- **Decided** — concrete: name the approach, file, or pattern chosen
- **Pivots** — only if something explicitly changed from a previous decision
- **Next** — what the human actually said they want to do
- Omit empty sections rather than leaving placeholders

---

## Inputs

| Input | Required | Description |
|---|---|---|
| `FEATURE_NAME` | yes | kebab-case name — infer from conversation if not stated |
| `CATEGORY` | yes | `features` \| `fixes` \| `refactor` \| `chore` — infer if not stated |
| `PLAN_NAME` | no | If a plan was created or updated this session |
| `PLAN_STATUS` | no | `proposed` \| `in progress` \| `done` |

---

## Output path

```
.bindify/development/<category>/<feature-name>/coordinator.md
```

---

## Post-step

After writing `coordinator.md`, run `update-links` for the feature/plan context so related docs stay connected via `[[wiki-links]]` and `## Related` backlinks.
