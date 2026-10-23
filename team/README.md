# siso-project-team

**A project team in a box: one Agent Zero, autonomous owners, disposable arms, one shared
browser, one task spine, and every word the human said — repackaged so any new SISO project
gets the same team on day one, and every improvement sticks to this repo.**

**Front end: https://siso-project-team.pages.dev/** — the shape, his words → mechanisms, what
exists, what to build in order, what not to. Agents: after any change to `docs/`, run
`tools/publish-front` (see `docs/PUBLISHING.md`). Agents joining a team read `AGENTS.md`.

## Why this exists

On 2026-09-11 the SISO Internal Labs fleet — nine Opus owners under one Agent Zero — shipped
Health with storage, Budgets, Devices, a hardened deploy path and the token explanation. It
also: lost its orchestrator silently for nine hours, routed every owner report into Shaan's
own terminal, wrote 53 throwaway browser scripts, held 4.6 GB of idle context, took production
down for two minutes by hand, and spent $591 by midday. The structure worked; the plumbing
between tiers leaked. This repo is the plumbing, written down once.

Design: the front end above. [`docs/agent-team-v2.html`](docs/agent-team-v2.html) is the record of what broke → what fixes it.

**Three tiers, ruled 2026-09-11.** Shaan's *personal* Agent Zero (`siso-agent-zero-protocol`,
tier 0) sees every project and reads each team's `DIGEST.md`. Each project has its own
**Project Agent Zero** (Opus on Claude Code, one pane in the team's herdr space). Owners are
Opus on Claude Code, ephemeral. Arms are **Qwen and Luna on the Codex harness**, spawned by
herdr, messaging back when done; an owner without arms does the work itself or with built-in
sub-agents and says which.

## The shape

```
Shaan  ──his words──▶  personal Agent Zero  (siso-agent-zero-protocol — tier 0, not this repo)
                                   │ reads DIGEST.md · can talk to any project Agent Zero
                          ┌────────▼─────────┐
                          │ PROJECT Agent Zero │  resident · Opus · ONE herdr pane in the team space
                          └────────┬─────────┘
             spawns with a brief   │   closes on handoff
        ┌──────────────┬───────────┼───────────┬──────────────┐
     Owner           Owner       Owner       Owner        …as needed
   (Opus, ephemeral: brief in → task-appropriate acceptance → handoff → exit)
        │ dispatches bounded jobs, checkable results
   ┌────▼────────────────────────────────────────────┐
   │ ARMS: Qwen pool (Codex harness) · Luna (Codex)   │  no judgement, no rediscovery
   │ fallback: the owner's own sub-agents             │  spawned by herdr, one message back
   └─────────────────────────────────────────────────┘
   shared: herdr space · camofox (userId = team) · siso-browse · Plane project · intent ledger · az-send · this front end
```

One team = one herdr **space** (workspace) on the machine that hosts the project. The space
holds the project Agent Zero's pane and every owner pane. Arms are spawned by herdr too, in
their own harness, and message back with `az-send`.

## What this repo composes (and does not re-implement)

| Concern | Lives in | This repo adds |
|---|---|---|
| Shaan's intent, estate, plan — the personal Agent Zero | `sisodias/siso-agent-zero-protocol` | nothing; `team.yaml` links to it |
| Fleet economics: fresh-context workers, budget lanes, model routing, telemetry | `sisodias/siso-agent-playbook` | the team-space contract that applies them per project |
| A project's tasks/docs spine and anti-drift checks | `sisodias/siso-project-os` | the Plane link in `team.yaml`; the project OS stays the project's |
| Harness tuning (Claude Code / Codex settings, hooks, routing) | `sisodias/siso-harness-lab` | nothing; findings from teams are filed there |
| The app being built | the project's own repo | nothing |

## Layout

```
AGENTS.md                      front door for any agent joining any team (read first)
team.yaml                      the manifest schema, with the first real team filled in
skills/project-agent-zero/     the project Agent Zero's skill + COMPACT.md (state prompt)
skills/owner/                  the owner contract: autonomy, done-check, handoff, exit
skills/worker-contract/        the arms contract: brief in, checkable result out, harness per model
skills/team-front-door/        installable pointer to AGENTS.md for owners' ~/.claude/skills
tools/az-send                  clear, type, submit, read back — or fail loudly (the fix for 10 lost dispatches)
tools/spawn-worker             start an owner (Claude Code) or an arm (Codex: qwen|luna) in the space, brief in hand
tools/siso-browse              one logged-in browser for the whole team (replaces 53 scripts)
tools/intent-capture           every word the human said, verbatim: one file each + index + flat json
tools/new-team.sh              folder, manifest, herdr space, Agent Zero pane (--into a companion repo)
tools/publish-front            docs/ → Cloudflare Pages, hash-checked
codex/config.pool.toml         the Codex model provider that makes Qwen an arm
docs/index.html                the front end (live); agent-team-v2.html the record of what broke
teams/<slug>/                  one folder per live team: AGENT-ZERO.md, DIGEST.md, intent/, briefs/, handoffs/, workers/
```

## Instantiating a team

```sh
tools/new-team.sh byk --label "Bykonz Yard" --plane BYK --host siso-vps --checkout /opt/bykonz --herdr --az-pane
tools/spawn-worker --harness claude --name byk-zero --brief "$PWD/teams/byk/AGENT-ZERO.md"   --cwd /opt/bykonz --workspace <space from team.yaml> --host siso-vps
```

The first line makes the folder, `team.yaml`, the herdr space and the Agent Zero's pane; the
second starts him. `--retarget-notify` (az-notify → that pane) is a live-fleet change and is
never implied. `--into <companion>/team` puts the folder in the project's companion repo — the
knowledge repo symlinked into its code repos as `.agents/` — which is where a team folder
belongs once the project has one; never in a product repo. Owners are then spawned by the
project Agent Zero, never by hand.

## Rules that are not negotiable

- Owners message the **project Agent Zero**, never the human. The project Agent Zero posts
  console cards to the human only for **credentials, money, or production data**.
- Every claim of "done" carries a screenshot from `siso-browse`. A 200 proves nothing.
- Pointers, releases and production move only through the project's deploy script.
- One resident agent per team: the project Agent Zero. Everyone else exits on handoff.
- The intent log is regenerated before every state write and is **never public**.

**Private repo — keep it that way.** `teams/*/shaan-intent-log.*` holds the human's verbatim prompts by his explicit request; never mirror this repo to a public remote and never publish `teams/` through the front-end.
