# Agent Zero's runbook: how I actually run the fleet

Every command here was run and checked on 6 Oct 2026. The why is in `docs/adr/`; this file is the how. Paths are relative to this repo unless they start with `~`. When a command stops working, fix it here the same turn.

## Teams, owners, asks and returns (A53, 21 Oct 2026)

`bin/a0 board --json` is the full reconciliation view. It enumerates `teams`, `owners`,
`child_runs`, every canonical `ask` (including attended and closed ones), `dispatches`
and `receipts`. The compact text board shows their counts. `--since` controls the
wake summary only; it never removes asks or historical receipts from reconciliation.

Dispatch IDs derive from the existing append-only dispatch records. Each dispatch
keeps its parent, thread, task IDs, receipt ID and outcome; `missing-return` remains
visible until an exactly correlated receipt arrives. Owner entries link asks and
dispatches. Child runs include Codex metadata, recorded subagent dispatches and local
SISO Code run/lineage metadata under dispatched threads. No transcript scan is used.
`coverage` names missing stores, unreadable tasks and unavailable child-run metadata;
a missing store is not evidence that no work ran there. This is a local-store view,
not a claim that remote machines have been fully mirrored.

After dispatch, the existing `a0-await SEAT` background waiter now publishes its
completed, blocked and needs-input observations into the existing events ledger and
canonical task-event sidecar. Its exit remains the automatic wake. Receipts carry
thread/run/dispatch/task identifiers and an outcome, never copied prompts or private
seat text. Duplicate observations are idempotent. A newer send or replacement thread
cannot consume an old run's receipt; uncorrelatable historical work remains
`missing-return` for reconciliation. A receipt reports an observed owner outcome;
it does not mark its task live or prove deployment.

Initial audit and checks: [A53 reconciliation](audits/a53-t0691.md).

## After a compaction (boot, about 2 minutes)
1. Read `AGENTS.md` → **Now**, then the five ADRs (`docs/adr/`, short), then the top entry of `.agents/HANDOFF.md`.
2. `bin/owners`: who is running, at what context, and their latest link.
3. `bin/ask queue <OWNER>` for anyone who looks stuck. `bin/a0-task list --stage thought` lists the parked ideas.
4. `curl -s http://127.0.0.1:5401/api/version` and `uptime; sysctl -n vm.swapusage`. That gives what's live and how hot the laptop is.

## When Shaan speaks
- **An ask for an owner:** `bin/ask new --project P --owner NAME --his "<verbatim>" "<title>" --touches area[,area] [--supersedes t-N]`.
  - Long feedback goes in a verbatim file first, linked with `--spec FILE`.
  - Nothing else is needed: the owner pulls it (ADR 0004).
- **Something only I do** (data, a fix to an owner's brief, the registry): do it now and tell him what changed.
- **A new owner:** write `BRIEF.md` (his words verbatim, scope, ship path, the ADR 0004/0005 section, hard lines), then run:
  ```
  bin/opus-chat NAME DIR BRIEF
  ```
  It autocompacts at 30%, and `--effort max` can be passed through to siso-host. Then:
  1. fix the registry (below);
  2. write its card;
  3. give it an ask.
- **Reply** in plain Claude markdown with links (ADR 0003).

## Owners
- **Host records:** `~/.local/state/agent-base/hosts/w7_pNN.json`, with `name`, `state` (working/idle), `ctx.pct`, `port` and `token` (never print the token).
- **Cards:** `~/.local/state/a0/owners/<NAME>.json`, with `status`, `subtitle` (the step), `page` (URL), `summary` and `updated`. Protocol: `~/SISO_Workspace/_data/ab-feedback/OWNER-CARD.md`. My own picks are `_a0.json`.
- **Registry:** `~/.local/state/agent-base/registry.json` → `agents[NAME] = {main, workspace, project, domain, kind: owner|worker, role, owner?}`.
  - New chats get auto-filed as `kind: worker` under a dead owner, which makes them invisible in the tree.
  - Fix it with an atomic rewrite (tempfile + `os.replace`): set `kind: owner`, the project, and `main: true` for the project's main owner.
- **Handover:** a file plus one line, `bin/a0-tell <pane> "A0: read <file> ..."`.
  - Use the pane id (`w7:p4D`). Tab names fail for hosted chats.
  - The line is queued and starts a turn when the chat is idle, so only send it when the work is worth a turn now.
- **Delayed handover** (after a limit reset): a background `until`-loop on the clock, then `a0-tell`. Never a foreground sleep.
- **Compact an owner:** after it has written its checkpoint, and only when it is idle, run `bin/a0-tell --sync <pane> "/compact"`.
  - A long or queued `/compact` arrives as pasted text and does nothing.
  - Then watch `ctx.pct` drop and send a one-line "resume from your HANDOFF". In a zsh wait loop, split the reading with `set -- ${=c}`; a plain `$c` stays one word in zsh.
- **Stop a runaway:** `bin/host-stop <pane>` lists what's running (a dry run); `bin/host-stop <pane> go` stops every sub-agent and job, then interrupts. Escape via herdr doesn't reach hosted chats.
- **Stop a process:** `bin/jobstop <pid>`. Never use `pkill -f`.

## Agent Base (live at http://127.0.0.1:5401)
- **Ship:**
  ```
  cd ~/SISO_Workspace/_data/worktrees/siso-internal-labs-agent-base/ship-runner && heavy -- tools/ab-live <sha> && heavy -- tools/ab-smoke http://127.0.0.1:5401
  ```
  Then merge the PR. The live sha shows in `/api/version`, `git rev-parse live` and the `LIVE` file.
- **`ab-live` refuses (exit 4)** if:
  - a checkout file differs from both HEAD and live: archive it to `_archive/YYYY-MM-DD-subject/` with a MANIFEST, then restore it from live;
  - the change touches `apps/desktop`;
  - the sha doesn't descend from live.
- **`ab-queue add` is refused by the writer gate** ("cannot be uniquely observed"). Use a PR, then `ab-live` by hand.
- **Release notes** (a missing note shows "Outcome not recorded" in Activity):
  - in the PR at `services/node/releases/notes.jsonl`, or
  - appended to `~/.local/state/agent-base/live/notes-0bad3f5e005ad632.jsonl`.

  Shape: `{sha, title, why, what[], see}`, in human words.
- **Today pad:** `.agents/a0/scratchpad.json` → `{date, updated, items:[{id, text, at, done}]}`. Write it atomically; the panel reads `/api/scratchpad`.
- **Tasks and asks:** `bin/a0-task` and `bin/ask`. The API is `/api/a0/tasks`. Moving a task to `live` needs `--evidence`.
- **Board sticky note:** `node --experimental-strip-types services/node/bin/ab-note.mjs apply < request.json` with `{action:create, requestId, by, source, text, why}`.
- **Screenshot** (WebKit, closes itself): import Playwright from `~/SISO_Workspace/SISO_Agency/apps/siso-internal-labs/siso-internal-labs-agent-base/node_modules/.pnpm/playwright@1.55.0/node_modules/playwright/index.mjs`, then run with `heavy -- node script.mjs`. An example is `~/SISO_Workspace/_data/a0-home/shots/` (home-1440.png).
- **Usage feed:** `curl -s http://127.0.0.1:5401/api/usage`. It said "Waiting for the burn source" on 6 Oct; FLEET-COST is fixing it.

## Git without touching anyone else's work
- **Commit only my lines:**
  ```
  export GIT_INDEX_FILE=$(mktemp); git read-tree HEAD; git add <my paths>; git commit ...; unset GIT_INDEX_FILE; git reset -q -- <my paths>
  ```
- **A shared file with others' uncommitted lines** (like AGENTS.md): apply my edit to `git show HEAD:file` as well, `git hash-object -w` it, then `git update-index --cacheinfo` in the temp index.
- **Never a bare `git reset`.** It cleared the whole index once.
- **Put work on main:** commit on a work branch, `bin/land --prove` (runs the affected checks and stores a proof per command), then `bin/land` (verifies the proofs, about 6 s). Prove rebases onto main first, so its proofs match what land checks; a proof miss on a suite slower than the land bound exits 7 naming the package and why: prove again. Land exits: 2 usage or dirty tree, 3 fetch, 4 conflict, 5 check failed, 7 slow proof miss, 8 secrets, 9 private path, 10 checkout drift, 124/125 environment or timeout. Never `git push origin HEAD:main`. Products go through PRs.

## This Bash tool's quirks
- `grep`, `find` and `stat` are broken shell functions here: use `/usr/bin/grep`, `/usr/bin/find`, `/usr/bin/stat`.
- zsh history modifiers eat `$var:r…`, so write `${var}`. `echo ===` can fail too, so use `echo ---`.
- No foreground `sleep` chains: use `run_in_background` with an `until`-loop.
- `self-compact` refuses under `SISO_A0=1`. Shaan compacts me; write HANDOFF before he does.

## Laptop
- Look with `uptime`, `sysctl -n vm.swapusage`, and `ps -axo pid,ppid,rss,%cpu,etime,comm | sort -k3 -nr | head`.
- The usual heavy users:
  - the Agent Base app's WebKit view (about 0.9 GB);
  - camoufox (`camofox-browser` on :9377, `/tabs`, `/pressure/cleanup`);
  - the `tsc`/`vitest` checks;
  - the Claude SDK binaries (60–260 MB per chat).
- Builder slots are held by a flock on each slot file (`agents/harness/bin/builder_local.py`). Test the lock before calling a slot bug; `lsof` also lists paused builders (21 Oct: a flock test showed the slots were honest).
- FLEET-COST owns making this cheap (`_data/fleet-cost/`).
