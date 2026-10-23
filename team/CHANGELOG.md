# Changelog — siso-project-team

Teams pin a version in `team.yaml → template.version`; `tools/team-upgrade` shows what changed since.

## v0.5.0 — 2026-09-12
- **Two substrates, one set of tools.** `orca` joins `herdr`: `spawn-worker --substrate orca` starts an owner as an Orca terminal in the team's worktree (titled `<domain> · <brief id>`) and returns its handle; `az-send`, `az-notify` and `az-dispatch` take a handle or `orca:<title>` and route themselves; `fleet-status` lists both with a `substrate` column. herdr stays the substrate on the laptop and the Mac Mini.
- **Submission is observed, not inferred.** Orca's `terminal send --enter --wait-submit` returns a receipt whose stages separate `input_accepted` from `turn_started`. `az-send` exit 0 means the agent has it (a turn started, or it is mid-turn and the input is queued behind it); exit 2 means it does not, and the fix is `--retry-request <id>`, which replays the receipt instead of delivering the prompt twice. This is the end of the stale-line trap that lost ten dispatches on 2026-09-11.
- A receipt that reports no turn start is **not** proof of failure, and treating it as one lies to you: an owner blocked on a 5m30s bash call reports exactly that and has already queued and read the message. `az-send` reads the rendered screen before it calls a send failed.
- `tools/lib/orca.sh`: the one place that knows how to talk to Orca (CLI resolution, title→handle, `--screen` reads, the send verdict).
- One switch for Agent Zero: `az-notify` reads its target from a single file, so moving him between substrates — and rolling back — is one word.
- `team.yaml` gains `substrate:` and `orca: {runtime, repo_id, worktree, cli, runs_as}`; `new-team.sh` writes both, defaulting to `herdr`.
- `skills/project-agent-zero` and `skills/owner`: a dated Orca section each — spawn, send, read, migrate at a boundary, and the two traps below.
- Two traps found on the box, written into the tools: `orca agent hooks on` flips the flag but does **not** install the Claude hooks (status stays `not_installed` behind `ok: true`); and a terminal has two titles — the tab's, which `--title` sets and every tool addresses, and the pty's, which Claude Code overwrites with its own summary and status glyph and which is what the Agents tab shows. Forcing the pty title with `terminal rename` costs the live status glyph.

## v0.3.0 — 2026-09-11
- Second team from one command: Bykonz Yard (`new-team.sh --into … --herdr --az-pane`), Agent Zero in its own space, companion repo, own camofox.
- `tools/intent-to-plane`: his verbatim entries become labelled, back-linked Plane items (`plane new-label` added to the siso-plane-ops CLI).
- `tools/fleet-status` + `tools/render-front`: the three numbers and a private team page generated on every state write; served at the team's `/agents/` behind the login.
- `tools/az-deliver` (host-side forced command) gains a read-only `__fleet__` verb so the agents user can see root's herdr without owning it.
- camofox per team: `ops/siso-camofox@.service`, `new-team.sh --camofox-port`.
- `siso-browse` runs from its home (ESM ignores NODE_PATH); the 53 ad-hoc scripts retired.

## v0.2.1 — 2026-09-11
- Lessons from Oracle (`docs/lessons-from-oracle.html`) folded in: owner Landing section + "wasted" handoff line; Agent Zero watches three numbers, never a status; the only cold review (sensitive paths → SHIP/FIX-FIRST/RETHINK); Sweep job example; AGENTS.md rule 6 (one ledger per kind); `team.yaml` verify/trunk blocks; `new-team.sh` seeds OWNERS.md, DECISION-LOG.html, PROVEN-LEDGER.html, HUMAN-GATE.md and wires `--code-repo` (.agents symlink + nested AGENTS.md); `spawn-worker --worktree` lanes capped at 3.
- Labs deployed: Agent Zero pane `w1:pP`, az-notify retargeted, Codex 0.154 on the VPS (Luna proven), companion repo `siso-internal-labs-agents` with sessions.

## v0.2.0 — 2026-09-11
- Tier 0 above every team: Shaan's personal Agent Zero reads `DIGEST.md`; one Project Agent Zero per project.
- Harness by role: Opus on Claude Code; Qwen and Luna arms on Codex (`codex/config.pool.toml`), spawned with `tools/spawn-worker`, messaging back.
- `tools/az-send` clears with the raw Ctrl-U byte (herdr rejects `ctrl-u`); proven on the VPS.
- `tools/intent-capture` replaces `intent-log.py`: one verbatim file per message, idempotent, padding filter, flat json kept.
- `tools/sessions-import`: conversation history into the team repo, redacted, with a manifest.
- `tools/new-team.sh`: correct herdr JSON, real Agent Zero tab, `--into` a companion repo, `--retarget-notify` explicit.
- `tools/publish-front`; front end live at https://siso-project-team.pages.dev/.
- `tools/team-upgrade`: what changed between a team's pinned version and the template's HEAD; relinks skills.

## v0.1.0 — 2026-09-11 (11:18Z draft)
- AGENTS.md front door, team.yaml, skills project-agent-zero/owner/worker-contract/team-front-door, az-send, siso-browse, intent-log, new-team.sh.
