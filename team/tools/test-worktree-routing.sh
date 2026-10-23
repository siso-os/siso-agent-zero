#!/usr/bin/env bash
# Offline fixture for worktree branch selection, zero-lane counting, and capacity refusal.
set -euo pipefail
D=$(mktemp -d "${TMPDIR%/}/.siso-ephemeral-worktree-routing.XXXXXX")
trap 'rm -rf -- "$D"' EXIT HUP INT TERM
REPO="$D/repo"; ORIGIN="$D/origin.git"; TEAM="$D/team"; BIN="$D/bin"
mkdir -p "$TEAM" "$BIN"
git init --bare -q "$ORIGIN"
git init -q -b siso/main "$REPO"
git -C "$REPO" config user.email test@example.invalid
git -C "$REPO" config user.name test
printf 'fixture\n' > "$REPO/README.md"
git -C "$REPO" add README.md
git -C "$REPO" commit -qm base
git -C "$REPO" remote add origin "$ORIGIN"
git -C "$REPO" push -q -u origin siso/main
printf '%s\n' 'project:' '  branch: siso/main' 'substrate: herdr' > "$TEAM/team.yaml"
cat > "$BIN/herdr" <<'SH'
#!/bin/sh
printf '%s\n' "$*" >> "$HERDR_LOG"
if [ "$1" = tab ] && [ "$2" = create ]; then
  printf '%s\n' '{"result":{"root_pane":{"pane_id":"fixture-pane"}}}'
fi
SH
chmod 755 "$BIN/herdr"
S="$(cd "$(dirname "$0")" && pwd)/spawn-worker"
export HERDR_LOG="$D/herdr.calls"
export PATH="$BIN:$PATH"
bash "$S" --name first --harness raw --cwd "$REPO" --workspace fixture --worktree --max-lanes 1 --team-dir "$TEAM" -- noop >/dev/null
test "$(git -C "$REPO/.worktrees/first" branch --show-current)" = lane/first
test "$(git -C "$REPO/.worktrees/first" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse refs/remotes/origin/siso/main)"
calls=$(wc -l < "$HERDR_LOG")
if bash "$S" --name second --harness raw --cwd "$REPO" --workspace fixture --worktree --max-lanes 1 --team-dir "$TEAM" -- noop >/dev/null 2>&1; then exit 1; fi
test "$(wc -l < "$HERDR_LOG")" = "$calls"
git -C "$REPO" remote set-url origin "$D/missing-origin.git"
if bash "$S" --name fetch-failure --harness raw --cwd "$REPO" --workspace fixture --worktree --max-lanes 2 --team-dir "$TEAM" -- noop >/dev/null 2>&1; then exit 1; fi
test ! -e "$REPO/.worktrees/fetch-failure"
test "$(wc -l < "$HERDR_LOG")" = "$calls"
echo 'PASS worktree routing regressions'
