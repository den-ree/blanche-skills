#!/usr/bin/env bash
# scripts/verify-worktree.sh
# Manages isolated git worktrees for verifying cloud agent changes on macOS.

set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") <action> <branch> [options]

Actions:
  setup <branch>              Fetch branch and initialize worktree
  open  <branch>              Initialize worktree and open in Xcode / Finder
  test  <branch> [args...]    Run tests in worktree; capture failures to test-failure.log and push
  clean <branch>              Remove worktree and prune worktree references
  list                        List all active worktrees

Examples:
  $(basename "$0") setup plan/user-auth
  $(basename "$0") open plan/user-auth
  $(basename "$0") test plan/user-auth -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 16'
  $(basename "$0") clean plan/user-auth
EOF
  exit 1
}

ACTION="${1:-}"

if [ "$ACTION" = "list" ]; then
  git worktree list
  exit 0
fi

BRANCH="${2:-}"

if [ -z "$ACTION" ] || [ -z "$BRANCH" ]; then
  usage
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="${REPO_ROOT}/../worktrees"
SAFE_BRANCH_NAME="$(echo "$BRANCH" | tr '/' '-')"
WORKTREE_PATH="${WORKTREE_DIR}/${SAFE_BRANCH_NAME}"

ensure_worktree() {
  mkdir -p "$WORKTREE_DIR"
  if [ -d "$WORKTREE_PATH" ]; then
    echo "Using existing worktree at: $WORKTREE_PATH"
    git -C "$WORKTREE_PATH" fetch origin "$BRANCH" 2>/dev/null || true
    git -C "$WORKTREE_PATH" pull --rebase origin "$BRANCH" 2>/dev/null || true
  else
    echo "Creating worktree for '$BRANCH' at: $WORKTREE_PATH"
    git fetch origin "$BRANCH" 2>/dev/null || true
    if git show-ref --quiet "refs/heads/$BRANCH"; then
      git worktree add "$WORKTREE_PATH" "$BRANCH"
    else
      git worktree add -b "$BRANCH" "$WORKTREE_PATH" "origin/$BRANCH" 2>/dev/null || git worktree add "$WORKTREE_PATH" -b "$BRANCH"
    fi
  fi
}

case "$ACTION" in
  setup)
    ensure_worktree
    echo "Worktree ready at: $WORKTREE_PATH"
    ;;

  open)
    ensure_worktree
    # Find Xcode workspace or project
    XCODE_TARGET="$(find "$WORKTREE_PATH" -maxdepth 2 \( -name "*.xcworkspace" -o -name "*.xcodeproj" \) | head -n 1 || true)"
    if [ -n "$XCODE_TARGET" ]; then
      echo "Opening $XCODE_TARGET in Xcode..."
      open -a Xcode "$XCODE_TARGET"
    else
      echo "Opening $WORKTREE_PATH in Finder..."
      open "$WORKTREE_PATH"
    fi
    ;;

  test)
    ensure_worktree
    shift 2 # pass remaining arguments to xcodebuild / swift test
    TEST_ARGS=("$@")

    echo "Running verification in: $WORKTREE_PATH"
    cd "$WORKTREE_PATH"

    BUILD_CMD=()
    if [ -f "Package.swift" ] && [ ${#TEST_ARGS[@]} -eq 0 ]; then
      BUILD_CMD=("swift" "test")
    else
      BUILD_CMD=("xcodebuild" "test" "${TEST_ARGS[@]}")
    fi

    echo "Executing: ${BUILD_CMD[*]}"
    if "${BUILD_CMD[@]}" 2>&1 | tee /tmp/verify-build.log; then
      echo "All tests and builds passed."
      if [ -f "test-failure.log" ]; then
        git rm -f test-failure.log 2>/dev/null || rm -f test-failure.log
        git commit -m "verify: clean resolved test-failure.log" 2>/dev/null || true
        git push origin "$BRANCH" 2>/dev/null || true
      fi
    else
      echo "Build/Test failed. Saving failure log for agent..."
      cp /tmp/verify-build.log test-failure.log
      git add test-failure.log
      git commit -m "verify: report compiler/test failures for agent" || true
      git push origin "$BRANCH" || true
      echo "Pushed test-failure.log to origin/$BRANCH. Remote agent can now resolve the failures."
      exit 1
    fi
    ;;

  clean)
    if [ -d "$WORKTREE_PATH" ]; then
      echo "Removing worktree at: $WORKTREE_PATH"
      git worktree remove --force "$WORKTREE_PATH"
      git worktree prune
      echo "Cleaned worktree."
    else
      echo "No worktree found at: $WORKTREE_PATH"
    fi
    ;;

  *)
    usage
    ;;
esac
