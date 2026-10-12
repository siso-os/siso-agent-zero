# Agent Zero's house: where it lives and works

Shaan, 4 Oct 2026: "do you want to set up your house a bit before you checkpoint ... not just memory but your own like ... personal
library of docs ... and your infrastructure because this is where you're gonna live and work". Design rules from
`research/agent-zero-v2/FINDINGS.md`: plain files in git, found with grep; a short map; fetch detail when needed; measure misses
before adding machinery.

## Rooms (each holds one kind of thing; nothing lives in two rooms)
| Room | Holds | Changes |
|---|---|---|
| `AGENTS.md` | the map: the job, the loop, hard rules, where things are | rarely; ~100 lines |
| `PRINCIPLES.md` | why: physics, principles, memory, research shape, lessons from the labs | when we learn something structural |
| `words/` | **Shaan's words**, verbatim memos (Sep) and the corpus; they outrank every summary | append only |
| `.agents/a0/transcript/` | every chat message he sent (mid-turn ones too), redacted, by day; built by `bin/a0-transcript build` | generated, not in git |
| `.agents/memory/` | facts with no other home, one per file, each with its owner; `MEMORY.md` is the index of what Agent Zero knows and where | the memory ladder (PRINCIPLES.md) |
| `routing.json` · `projects.json` · `bin/renewals.json` | live state: models and money · every project's five things · paid plans | when the world changes |
| `.agents/HANDOFF.md` | where work stands now: the top entry is current; older entries are history (`.agents/HANDOFF-HISTORY.md`) | every checkpoint |
| `research/<topic>/` | the library: one file per reader (sourced), `FINDINGS.md` per topic | per question |
| `docs/` | guides (`HOW-TO-WORK-WITH-AGENT-ZERO.md`), maps (`maps/`), evidence (`evidence/`), the Elon pass (`ELON-PASS.md`, `passes.jsonl`) | per piece of work |
| `jobs/` | every job brief and its RETURN (`<job>.md`, `<job>.out`) | per job |
| `tasks/` | his asks, one file each (`bin/a0-task`) | per ask |
| `bin/` | the tools (`~/.local/bin` launchers point here) | rarely |
| `.claude/skills/` | procedures, loaded when the work needs them | when a procedure repeats |

## Finding anything
`recall <words>`: one search across every room, most trusted first (his words, memory, state, checkpoint, map, research, docs,
jobs, tasks). It is grep on purpose. If it misses something that was in the house, that miss is logged in `docs/recall-misses.md`
and fixed by moving the fact to the right room; an index or vector store comes only after misses repeat.

## Keeping it clean
- At every checkpoint: the top HANDOFF entry is rewritten; older ones move to `HANDOFF-HISTORY.md`; the memory ladder runs
  (contradicted or stale facts deleted, repeated ones promoted).
- `bin/house-check` asks a model that knows nothing ten questions whose answers are in the house; the score goes in
  `docs/passes.jsonl`. A miss is a bug in the house.
- The house is private (`gh repo view sisodias/siso-agent-zero --json visibility`): it holds his words.
