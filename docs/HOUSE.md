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
| `.agents/a0/transcript/` | optional local transcript cache built by `bin/a0-transcript build`; completeness and redaction require verification; never copy private payloads to git or logs | generated, not in git |
| `.agents/memory/` | facts with no other home, one per file, each with its owner; `MEMORY.md` is the index of what Agent Zero knows and where | the memory ladder (PRINCIPLES.md) |
| `routing.json` · `projects.json` · `bin/renewals.json` | dated model direction · project/source pointers and historical audit observations · recorded paid-plan decisions; none alone proves current billing or runtime | when verified evidence or direction changes |
| `.agents/HANDOFF.md` | where work stands now: the top entry is current; older entries are history (`.agents/HANDOFF-HISTORY.md`) | every checkpoint |
| `research/<topic>/` | the library: one file per reader (sourced), `FINDINGS.md` per topic | per question |
| `docs/` | guides (`HOW-TO-WORK-WITH-AGENT-ZERO.md`), maps (`maps/`), evidence (`evidence/`), the Elon pass (`ELON-PASS.md`, `passes.jsonl`) | per piece of work |
| `jobs/` | every job brief and its RETURN (`<job>.md`, `<job>.out`) | per job |
| `tasks/` | his asks, one JSON file each (`bin/a0-task`); `tasks/INDEX.json` and `.agents/A0-plan.json` are generated views | per ask |
| `bin/` | the tools (`~/.local/bin` launchers point here) | rarely |
| `.claude/skills/` | procedures, loaded when the work needs them | when a procedure repeats |

## Cold entry (source pointers checked 6 Oct 2026; runtime must be observed separately)
Start in `~/SISO_Workspace/SISO_Agents/agent-zero/siso-agent-zero`: `AGENTS.md`, then `.agents/HANDOFF.md` and
`.agents/memory/MEMORY.md`. `routing.json` is current direction; source code for A0 commands is `bin/`.

| Need | Owning source or observation path |
|---|---|
| Current upgrade owners, outcomes and next gates | `.agents/runs/2026-10-06-upgrade/plan.json`; its `intentMap` links intent to owners and acceptance. `intent-recovery.json` beside it records recovered user intent; treat source locators as private. Read these directly: `recall` does not index this runs directory. |
| Tasks and decisions | `tasks/` through `bin/a0-task`; Agent Base `services/node/src/hub.ts` reads this repo's generated `.agents/A0-plan.json`. `words/`, `.agents/HANDOFF.md` and project-local handoffs provide prior decisions and feedback. |
| Hosted agents, ownership and returns | `~/.local/state/agent-base/hosts/name-*.json` (or configured `AB_HOSTS_DIR`) is runtime metadata; `~/.local/state/a0/owners/` and `~/.local/state/a0/locks.json` record ownership; `~/.local/state/a0/dispatch.jsonl` links dispatches to return paths and `~/.local/state/a0/souls/done.log` records returns. Source: Agent Base `services/host/src/service-runner.ts`, `services/node/src/owners.ts`, and A0 `bin/soul`. Metadata/card/return existence is not delivery proof; check its timestamp, result and current owner before new work. |
| Agent Base code and acceptance | `~/SISO_Workspace/SISO_Agency/apps/siso-internal-labs/siso-internal-labs-agent-base/AGENTS.md`, then `.agents/HANDOFF.md`, `.agents/TASK-TREE.md` and `.agents/OWNER-PLAN.md`: AB-RESEARCH integrates. Checkout HEAD is not runtime; use that front door's `LIVE`/`live`/`/api/version` probes, then behavioral evidence. |
| Oracle code and acceptance | `~/SISO_Workspace/SISO_Agency/partners/halo/oracle/AGENTS.md`; code in `core/` and `operator-app/`, each with its own instructions. ORACLE-RESEARCH integrates via `.agents/plan/oracle-integration.json` and `.agents/ORACLE-INTEGRATION.md`; direct Operator/UI lanes retain scope. |

These pointers authorize discovery, not agent launches, runtime restarts or promotion. Current protected-action gates remain
in `AGENTS.md`; source, historical checks, DEV acceptance and live behavior are separate evidence.

## Finding anything
Inside A0, `recall <words>` searches its configured layers, most trusted first (his words, memory, state, checkpoint, map,
research, docs, jobs, tasks). It is grep on purpose; it is not a complete estate or runtime index. If it misses something that was in the house, that miss is logged in `docs/recall-misses.md`
and fixed by moving the fact to the right room; an index or vector store comes only after misses repeat.

For an unknown physical home, use `estate where <words>` and `~/SISO_Workspace/AGENTS.md`; estate owns placement,
repository locations and restore metadata. For reusable capability/source discovery, use
`~/SISO_Workspace/Great_Library_of_SISO/AGENTS.md` and its `node bin/gls search "<capability>"`: the Library's
`registry/` owns public Work/Release/source records, and `site/` is a generated reading surface. Follow the selected source
and access boundary; do not copy private A0 words, transcripts or runtime locators into the public Library. Existing private
HTML/artifacts remain with their owning project and its handoff; this map is not a second Docs catalog. A known owner needs
no full estate/Library inventory. `roles/scout.md` describes Agent Base research coverage, not estate authority or code ownership.

## Keeping it clean
- At every checkpoint: the top HANDOFF entry is rewritten; older ones move to `HANDOFF-HISTORY.md`; the memory ladder runs
  (contradicted or stale facts deleted, repeated ones promoted).
- `bin/house-check` launches a model using `docs/house-check.json` and writes scores to `docs/passes.jsonl`. Its policy
  question follows the 6 October usage direction; historical questions are dated observations, not current runtime gates.
  Use direct source/path checks for this cold-entry map; do not launch a model merely to read it.
- The house contains private words and state. A recorded repository visibility claim is not a fresh access check; verify
  visibility before any publication and keep private content out of public catalogs and logs.
