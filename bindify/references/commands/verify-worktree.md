# Command: verify-worktree

Run macOS verification of an agent branch in an isolated git worktree. The main editor checkout stays on its current branch.

This is a bindify command. It is not a separate skill.

---

## When to use

- Open an agent branch in Xcode without switching the main workspace
- Build or test that branch on macOS
- Push compiler or test failures back to the branch as `test-failure.log` so a cloud agent can fix them
- Remove the worktree when verification is done

---

## Script

Run the script shipped with this skill:

```
<bindify-skill-root>/references/scripts/verify-worktree.sh
```

`<bindify-skill-root>` is the directory that contains `SKILL.md` (repo path `bindify/`, or the installed skill directory).

Worktrees are created at `../worktrees/<branch-with-slashes-replaced-by-dashes>` relative to the repo root.

---

## Actions

| Action | Command | Result |
|---|---|---|
| setup | `verify-worktree.sh setup <branch>` | Fetch branch and create or update the worktree |
| open | `verify-worktree.sh open <branch>` | Setup, then open `.xcworkspace` / `.xcodeproj` in Xcode, or the folder if none exists |
| test | `verify-worktree.sh test <branch> [xcodebuild args...]` | Run tests in the worktree |
| clean | `verify-worktree.sh clean <branch>` | Remove the worktree and prune |
| list | `verify-worktree.sh list` | List active worktrees |

Example:

```bash
verify-worktree.sh test plan/auth-flow -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'
```

If `Package.swift` exists and no extra args are passed, the script runs `swift test` instead of `xcodebuild test`.

---

## Test outcome

- **Pass:** remove a stale `test-failure.log` if one exists, commit that removal, and push the branch.
- **Fail:** write the log to `test-failure.log` at the worktree root, commit it, and push. The next `iterate-planning-mode` run on that branch must read the log first, fix the errors, and delete the file.

Do not run this command on a Linux cloud agent. Cloud agents edit source only; this command is the macOS verification step.
