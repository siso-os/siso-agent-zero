---
name: team-front-door
description: Installable front door for any agent joining a SISO project team — where the team's tasks, docs, machines, intent log and tools are, and how to behave. Install into ~/.claude/skills on every team host so owners and arms load it first. Points at AGENTS.md in sisodias/siso-project-team.
---

# Team front door

You are on a SISO project team. The team is described by one file: `team.yaml`, in the
`siso-project-team` checkout on this host (`/opt/siso-project-team/teams/<project>/team.yaml`).
Read it. Then read `AGENTS.md` in the same checkout. Then the skill for your role:
`project-agent-zero`, `owner`, or `worker-contract`.

## In one screen

- **Tasks** → the Plane project in `team.yaml` (`siso-plane-ops` skill; loopback base URL on the host).
- **What the human said** → `teams/<project>/intent/` (one verbatim file per message, `index.html` newest first) and `shaan-intent-log.json`. Quote it; never paraphrase it.
- **Docs he reads** → `project.docs` in `team.yaml`. Visual work uses a picture beside its reference; other work uses its accepted artifact or check. Never localhost as the handoff surface.
- **Machines** → `host` and `host.other_machines`. Do not probe others; do not call a box dead from a Tailscale line.
- **Deploy** → `project.deploy_script` only. It gates hollow releases and backwards pointers itself.
- **Send a message** → `tools/az-send <pane> "…"`. It proves submission or fails.
- **Start an owner or an arm** → `tools/spawn-worker` (Opus on Claude Code; Qwen/Luna on Codex). Never a raw `claude`/`codex` in a pane by hand.
- **Who is above the team** → Shaan's personal Agent Zero (`siso-agent-zero-protocol`) reads `DIGEST.md`; it is not a second orchestrator.
- **Look at the app** → `tools/siso-browse`. One logged-in session for the team. Never your own Chromium.
- **Who to talk to** → the project Agent Zero's pane in `team.yaml`. Not the human.

## How the team improves

Every hard-won fact goes into the relevant skill in `siso-project-team`, with a one-line
commit, and is pushed. A fact in a chat message is lost by tomorrow; a fact in the skill is
loaded by every agent on every team from then on. If you changed how the team works, update
`docs/` and republish the front-end (`docs/PUBLISHING.md`).

## What not to do

Rediscover the estate. Write a browser script for non-visual work. Message the human. Keep your
pane alive after your handoff. Trust any claim without the relevant artifact or check.
