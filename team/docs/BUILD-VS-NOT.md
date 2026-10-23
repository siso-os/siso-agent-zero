# Build vs not

**The current list is on the front end: https://siso-project-team.pages.dev/#build** — what exists (verified), what was built, the ordered build list with sizes and what needs Shaan, and what not to build. Edit `docs/index.html`, then `tools/publish-front`. The table below is the 2026-09-11 11:18Z original, kept for the record.


| Need | Exists already | Build | Refuse |
|---|---|---|---|
| A resident, visible, addressable project Agent Zero | herdr panes + `agent_status`; `az-notify` | **one pane on the host** for him; retarget `az-notify`; retire the laptop resume (`new-team.sh` steps 2–4) | a second orchestrator; any headless resume of an orchestrator |
| Owners that don't cost $591/day idle | `TASK-*.md` briefs; herdr; `HANDOFF` files in `work/` | **the owner contract** (`skills/owner`): brief → browser-checkable done → handoff → exit; AZ closes panes | resident owners; "are you done" polling |
| Arms that do labour without rediscovery | Qwen pool serving (when its loop is on); Codex harness; Luna on the Codex plan; Claude sub-agents | **`JOB-*.md` contract** (`skills/worker-contract`); herdr spawn per job in the model's harness; `az-send` back | letting owners do arms' work at Opus prices; arms that read the intent log |
| One shared logged-in browser | `verify-page.mjs` + verifier account (never the human's cookie); Playwright on the host | **`tools/siso-browse`** with persisted `storageState`; delete `/tmp/pw/*` | any per-owner browser script; camofox as a second path until `siso-browse` is the only path (then camofox can sit behind it) |
| Messages that actually send | `herdr pane send-text` / `send-keys` | **`tools/az-send`** with read-back and non-zero exit | raw pane sends in any brief or skill |
| The human's intent, verbatim, auditable | laptop transcripts | **`tools/intent-log.py`** → `teams/<p>/shaan-intent-log.json`; regenerated before every AZ state write | paraphrased "requirements"; public publication of the log |
| A task spine | Plane (18 projects, CLI, loopback API) | the `tasks:` block in `team.yaml`; AZ reads Plane | a second tracker now. **beads** is re-evaluated after one week of ephemeral owners, as agents' scratch memory *beside* Plane |
| A visual plane for the human | Agents rail (`/siso-crm/herdr`), Orca (`/agents`), ttyd behind the login, docs path | **an Agent Zero tab**: his pane (ttyd), owners (herdr status + brief), tasks (Plane), shipped (releases + screenshots) — one owner, two days | a new dashboard app |
| Deploys that cannot ship a blank site | `siso-deploy.sh` with hollow gate, backwards refusal, last-good pin, per-build outDir (LABS-16) | **memory-aware second slot**; `/assets` miss → 404; `/preview/*/assets` served | hand-moved pointers; a second publisher (`siso-web-publish` is inert — keep it that way) |
| Fleet economics: budgets, routing, telemetry | `sisodias/siso-agent-playbook` | apply it per team via `team.yaml`; file findings back to it | re-deriving budget lanes here |
| Harness settings (hooks, models, betas) | `sisodias/siso-harness-lab` | file the `ANTHROPIC_BETAS` 400 and the stale-CLI auto-update failure there | ad-hoc harness edits on a team host |
| A team template that improves | this repo | **keep every hard-won fact in a skill here**, pushed; front-end via Cloudflare Pages (`docs/PUBLISHING.md`) | facts in chat; facts only in one agent's state file |

## Sequencing (from `agent-team-v2.html`)

1. AZ pane on the host + `az-notify` retarget (an hour) — removes silent death and the fleet-inbox-in-the-human's-terminal
2. `az-send` (an hour) — removes lost dispatches
3. `siso-browse` (half a day) — removes 53 scripts and unproven "renders"
4. Owner contract in force (a day, then habit) — removes the resident-context bill
5. `JOB` contract + herdr spawn of arms (a day; the pool must be serving) — removes owners doing labour
6. Agent Zero tab (one owner, two days) — removes the human flying blind
7. Caddy: `/assets` 404, `/preview/*/assets` (an hour, root) — removes blank tabs and blank previews

## Open decisions for the human, not the team

- Double the host's RAM to 16 GB ($10/month): yes, recommended — nine resident CLIs (4.6 GB) + OpenWA (2.0 GB) do not fit in 7.9 GB and produced three OOM kills.
- OpenWA on demand (stop when idle, start on click): recommended once Contact moves to Buzz; the session persists on disk.
- Compute pool loop timer: disabled since 23:43Z by someone — deliberate or not decides whether arms exist.
- Which Codex account holds the 70B: personal plan (gone forever) or API/Business (recoverable).
