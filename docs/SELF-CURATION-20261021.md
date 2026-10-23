# Agent Zero self-curation delivery, 21 Oct 2026

- AGENTS.md: 177 lines at the initial live snapshot; 99 after current Haiku, fleet and skill-link instructions.
- Self map: rules/Now, AGENT-ZERO soul/PRINCIPLES, words, tools/routing, memory/daily notes,
  HANDOFF/history, role/spawn ledgers, ADR 0010/runner/hooks, existing skills/upgrade verdicts.
- Event sources are the existing a0-await seat returns and a0-wire codex-run/Haiku-team events.
  look / a0 board is the wake-time view. No owner-subagent supervision or polling added.
- Next fresh Agent Zero/orchestrator thread uses the registered live/agents/zero project.
  Read-only statev2.sqlite probe confirmed project 5ad8f4f5-c864-4cb9-a2c1-d918da4164b0;
  the model/login are preserved. No current thread or SISO Code process was restarted.
- Stop checkpoints use final response only, tools-free pinned Haiku, a secret scan and deduplication;
  HANDOFF history is retained and daily memory gets a short index pointer. A controlled real Haiku
  probe wrote HANDOFF and memory successfully under a task-local fixture, never the live source.

## Legacy state preservation

Selected A0_DATA_HOME was siso/main/agents/zero. The legacy plan is dated 20 Oct 07:34;
the selected plan is dated 21 Oct 13:07 and remains authoritative. Task/scratch/settings working
copies are byte-identical to selected state. The newer legacy HANDOFF (288 lines vs selected 175)
is retained in HANDOFF-HISTORY.md, with a new 21 Oct top entry in the monorepo HANDOFF.
A read-only lsof inventory returned exit 0 with zero open files/cwds in the legacy repository.
No claim is made that an intermittent writer can never return; originals are retained.

The five named working files were snapshotted through the estate WIP helper's private index:
`.agents/A0-plan.json`, `.agents/HANDOFF.md`, `.agents/a0/scratchpad.json`, `.agents/a0/tasks.json`,
`.claude/settings.json`. Secret scan clean. Remote SHA verified:
`a9ba48bbfeef18020220982f31dd26294ba37405`, branch `estate/wip-2026-10-21-a0` in
sisodias/siso-agent-zero. The original checkout, staged index and 1,555 other status entries
were left intact; no archive/removal was authorized by this task. No statev2.sqlite mutation.

The a0-wire builder stopped before landing. Its existing committed branch was integrated without
rewriting its implementation. The inherited CI fixtures were kept isolated from live heavy admission;
the first landing timeout remains in a0-self-land.log. No real admission gate was waived.
