#!/usr/bin/env bash
# Offline regression coverage for task-aware brief linting and launch resolution.
set -euo pipefail
D=$(mktemp -d "${TMPDIR%/}/.siso-ephemeral-brief-routing.XXXXXX")
trap 'rm -rf -- "$D"' EXIT HUP INT TERM
TEAM="$D/team"; mkdir -p "$TEAM/custom-intent" "$TEAM/nested/briefs" "$D/ref"
printf '%s\n' '---' 'id: one' '---' 'Human requested a build for Buzz and this sentence continues beyond eighty characters so suffix matching matters.' > "$TEAM/custom-intent/one.md"
printf '%s\n' 'agent_zero:' '  intent_log: custom-intent' > "$TEAM/team.yaml"
touch "$D/ref/ui.png"
L="$(cd "$(dirname "$0")" && pwd)/brief-lint"; S="$(cd "$(dirname "$0")" && pwd)/spawn-worker"
quote='> "Human requested a build for Buzz and this sentence continues beyond eighty characters so suffix matching matters."'
brief() { printf '%s\n' "$quote" "$@"; }
brief 'Task-kind: build' '## Acceptance' 'Acceptance: the output receipt records the generated build identifier.' > "$TEAM/nested/briefs/TASK-build.md"
brief 'Task-kind: visual' '## Done' 'Compare the result beside the reference.' > "$TEAM/nested/briefs/TASK-visual.md"
brief "Reference: $D/ref/ui.png" '## Done' 'Compare the result beside the reference.' > "$TEAM/nested/briefs/TASK-legacy.md"
printf '%s\n' '> "Human requested a build for Buzz and this sentence continues beyond eighty characters so suffix DOES NOT match."' 'Task-kind: build' '## Acceptance' 'Acceptance: the output receipt records the wrong suffix after the first eighty characters.' > "$TEAM/nested/briefs/TASK-mismatch.md"
printf '%s\n' "$quote" 'Task-kind: build' '## Acceptance' 'Acceptance: the output receipt records the generated build identifier.' > "$TEAM/CHARTER.md"

python3 "$L" --team team --intent-dir "$TEAM/custom-intent" "$TEAM/nested/briefs/TASK-build.md" >/dev/null
if python3 "$L" --team team --intent-dir "$TEAM/custom-intent" "$TEAM/nested/briefs/TASK-visual.md" >/dev/null 2>&1; then exit 1; fi
python3 "$L" --team team --intent-dir "$TEAM/custom-intent" "$TEAM/nested/briefs/TASK-legacy.md" >/dev/null
if python3 "$L" --team team --intent-dir "$TEAM/custom-intent" "$TEAM/nested/briefs/TASK-mismatch.md" >/dev/null 2>&1; then exit 1; fi

# Owner lint is scoped to TASK briefs; a charter/bootstrap brief reaches ordinary launch validation.
if "$S" --name bootstrap --harness claude --brief "$TEAM/CHARTER.md" --team-dir "$TEAM" --substrate invalid >/dev/null 2>&1; then exit 1; fi
# Explicit and ancestor team resolution both lint before the invalid substrate exit; no worker starts.
if "$S" --name build --harness claude --brief "$TEAM/nested/briefs/TASK-build.md" --team-dir "$TEAM" --substrate invalid >/dev/null 2>&1; then exit 1; fi
if "$S" --name build --harness claude --brief "$TEAM/nested/briefs/TASK-build.md" --substrate invalid >/dev/null 2>&1; then exit 1; fi
if "$S" --name missing --harness claude --brief "$TEAM/no-such/TASK-missing.md" --substrate invalid >/dev/null 2>&1; then exit 1; fi
echo 'PASS brief routing regressions'
