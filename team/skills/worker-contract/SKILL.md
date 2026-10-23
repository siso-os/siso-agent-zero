---
name: worker-contract
description: The arms contract — how owners dispatch bounded jobs to Qwen-pool or Luna workers (or their own sub-agents), what a JOB brief contains, what a result looks like, and which harness each model runs in. Load when writing a JOB-*.md, when started as a worker, or when deciding whether a task is owner work or arm work.
---

# Worker contract — the arms

Arms do not think about the project. They do exactly what a brief says and return a result an
owner can check without re-doing the work. If a job needs judgement about the project, it is
not a job — the owner does it.

## Which arm, which harness

| Arm | Model | Harness | When |
|---|---|---|---|
| **qwen** | Qwen3.8-27B on the compute pool | Codex CLI harness (Codex is model-agnostic; points at the pool endpoint) | the pool is serving (`tools/pool-env --check` on the pool box says `ok`) |
| **luna** | GPT via the Codex plan | Codex CLI harness | the Codex plan is active |
| **opus/sonnet** | Claude | Claude Code harness | judgement-adjacent labour the owner wants close |
| **own sub-agents** | whatever the owner runs | the owner's harness | no pool serving; same brief format |

Arms are spawned by herdr in the team space, one pane per job, in their harness:
```sh
tools/spawn-worker --harness codex --model qwen --name <job> --brief /abs/JOB.md --cwd <dir> --workspace <space>
tools/spawn-worker --harness codex --model luna --name <job> --brief /abs/JOB.md --cwd <dir> --workspace <space>
```
Qwen runs in Codex through `[model_providers.siso-pool]` (`codex/config.pool.toml`, key from the
environment as `SISO_POOL_KEY`, never in a file in this repo); Luna through profile `SISO`.
The worker is told one thing: *"Read and execute the brief at <path>. It ends with RETURN and
STOP; obey both."* A Codex arm reads `teams/<slug>/workers/AGENTS.md` first, which points here.
They message back with `tools/az-send <owner-pane>` and stop; the owner closes the pane.
Ruled by Shaan 2026-09-11: Opus on Claude Code, Qwen and Luna on Codex, herdr spawns, the
arm messages back.

## The JOB brief (`JOB-<owner>-<n>.md`)

```
# JOB <id> — <one line>
OWNER PANE: w1:pX                       # where az-send delivers
INPUT: <exact files / paths / URLs>     # nothing outside this list may be read
DO: <the command(s) or the transformation, precisely>
DO NOT: <edits forbidden; usually: anything outside OUTPUT>
OUTPUT: <exact path(s) the arm writes>
CHECK: <a command the OWNER can run that returns 0 iff the job is correct>
RETURN: STATUS / CHANGED / VERIFY / EVIDENCE   # ≤ 200 words, written to OUTPUT.report.md
        then exactly one: tools/az-send <owner-pane> "[<job>] done|failed — <one line>; result: <OUTPUT>"
STOP:   exit after the message
```

Rules for writing one: no "figure out", no "investigate", no "improve". If you cannot write
`CHECK`, the job is not bounded — keep it. A job that needs the arm to read more than the
`INPUT` list is two jobs.

## What arms are for (examples that worked)

- run `siso-browse shot` on twelve URLs and write the twelve PNGs plus a one-line-per-URL report
- convert a directory of Markdown to the HTML template; `CHECK`: every source has a target, no `<script>`
- grep a tree for a pattern and produce a table; `CHECK`: `grep -c` matches the row count
- apply the same mechanical edit to N files from a spec; `CHECK`: the spec's test passes
- draft boilerplate from a template and a data file; the owner reviews, never trusts

### Worked example — the Sweep (from Oracle)

```
# JOB sweep-1 — rank what is broken in <corpus>
OWNER PANE: w1:pX
INPUT: <the corpus: a directory of logs, a docs tree, a set of pages>
DO: read every item once; produce ONE ranked list, worst first
OUTPUT: handoffs/sweep-1.md — one row per finding: rank · what · where · a command that reproduces it
CHECK: every row has a repro command that runs (grep -c '^| ' == rows with a `$` command)
RETURN: az-send w1:pX "[sweep-1] done — N rows; result: handoffs/sweep-1.md"
STOP
```
No other agent reads the corpus. The owner reads the list.

## What arms are not for

Deciding what "done" means. Touching shared state (index, pointers, Caddy). Reading the intent
log to reinterpret a brief. Reporting to the human. Anything where being wrong costs more than
redoing the job.

## The result

`OUTPUT.report.md`, ≤ 200 words:
```
STATUS: done | partial | failed
CHANGED: <paths>
VERIFY: <the CHECK command and its exit code>
EVIDENCE: <one window of the output, not the whole log>
```
The owner runs `CHECK` itself before using anything. An arm's word is not evidence; its `CHECK`
exit code is.

## Cost discipline

An arm's context is small by construction: the brief, the `INPUT` list, and its own work. If a
job's inputs exceed ~30k tokens, split it. The owner never pastes the project into a job.
