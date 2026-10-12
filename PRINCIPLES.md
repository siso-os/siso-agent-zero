# First principles for running agents (SISO)

The one document for how SISO runs agents. Evidence and history: siso-firstmate
`.agents/a0/specs/2026-10-03-stack-first-principles/` (FINDINGS, ORG, ROOT-CAUSE, SYSTEM v1+v2, index/). Started 3 Oct 2026 by
Agent Zero with Shaan: "we've been optimizing to run a human company ... first principles what the best system is for running
agents across all of the tasks and different projects".

## The goal
His words become working, live outcomes, fast, and he spends no minutes operating the machine. Two numbers: minutes from his
words to live; his minutes spent on the machine (restarts, relaying, testing, debugging agents). Both go down or it is wrong.

## What is physically true
1. Every model call re-reads its whole context: tokens = calls x context.
2. A model's output is a claim. Only a check that runs outside the model makes it a fact.
3. Generating is cheap and parallel; landing is serial. Past the landing rate, more writers add waiting and conflicts.
4. Models differ in price and pass rate (Luna ~70% first-time pass, cheap; Sol ~6x tokens; Opus scarce).
5. Memory inside a session dies and drifts; memory in files is shared, cheap and lasts.
6. Two kinds of checks exist: correctness (a machine can run it) and value (only Shaan can judge it: taste, ideas, direction).

## The principles
1. **Delete before building** (Musk: question, delete, simplify, accelerate, automate, in that order). Every moving part can
   break and must be read. The default answer to a problem is removing the thing that causes it.
2. **A compiler, not a company.** His intent is the source; jobs with checks are the units; the ship queue links; live is the
   binary. No owners, seats, managers, reports or relays.
3. **One writer per codebase.** Parallel agents read, research, review, or attempt the same job (best-of-N). They never write
   the same codebase at once: actions carry implicit decisions and parallel writers make incompatible ones (Cognition).
   Parallelism lives across projects and in breadth work (research, ideas, variations), not inside one repo.
4. **React to state, never to events** (Kubernetes is level-triggered). No pings, notices, alarms or agent-to-agent
   messages: an event is lost when its reader is down. State lives in files; loops look at it and act; screens show it.
5. **Scripts wait, models work.** Waiting, polling, checking, git, tests, deploys are deterministic code around a small
   creative core (Stripe's blueprint). A model is started for a job and ends with it.
6. **The checker is the bottleneck.** Invest first in agents verifying their own work: the app boots per worktree, agents
   drive it in a browser, tests run in parallel. Shaan is never the tester. A bug he finds becomes a permanent check first.
7. **Fresh context per job, memory in files.** Every job starts from the project's map and plan files and ends by updating
   them (Ralph loop, Anthropic's long-running harness, OpenAI's map-not-manual AGENTS.md).
8. **Cheap tries before expensive ones, by measurement.** Route each job to the cheapest model whose measured pass rate clears its
   check; two cheap attempts in parallel before one expensive one (3 Oct numbers: a 70% first-pass model run twice passes ~91%
   for about a third of one strong run's tokens); at most 2 fix rounds per tier (Stripe), then up a tier, then Agent Zero.
   Which models exist and what they cost changes weekly; it lives in `routing.json`, never in a principle.
9. **One source per fact.** Views are computed from the truth (herdr, git, the queue, files), never stored twice.
10. **Effort scales by rule.** Default one job. More only when the work splits into independent pieces. Entropy is
    permanent: small recurring cleanup jobs, not cleanup days.
11. **Shaan is the outer loop: taste and direction.** See below.

## The human loop (Shaan, 3 Oct ~21:00: "the biggest steps in innovation i've seen when we have human in the loop feedback")
Two loops. The inner loop is machines: generate, check, critique, refine; fast and cheap, as many rounds as it takes. The
outer loop is Shaan: he looks and says what is right or wrong; slow and the most valuable signal in the system, because only
he can judge value. Innovation rate = outer-loop cycles x information per look. So everything is built to make his looks
frequent, early and dense:
1. **He never sees what a machine could have rejected.** Only things that pass their correctness checks reach him.
2. **Options, not one thing.** Choosing between 3-4 distinct variations is faster and says more than critiquing one. Breadth is
   cheap: a Luna fleet generates variations, a critique pass against his recorded taste prunes to the distinct best.
3. **Early and small.** A mock in minutes before a build in hours (3 Oct: the Agent Zero view mock on real data, then the build).
   The outer loop should turn over in hours, not days.
4. **Where he already is, by voice.** A "Look" lane on his board: the artifact, the variations side by side, a screenshot,
   one line of why. He answers by voice; nothing is a form.
5. **Every answer is kept and compounds.** His words go verbatim beside the artifact, become jobs, and become taste memory
   (the ui-bank notes are the start) that the next generation round is critiqued against, so he repeats himself less.
6. **Where the loop applies:** UI, ideas, product direction, anything outward-facing: the outer loop is required.
   Plumbing (deploys, infra, the agent stack's mechanics): machine checks only; he hears about it only if it needs money,
   power or a decision only he can make.

## Research (Shaan, 3 Oct ~22:20: "a place where we can see the research fleet ... a proper system for it")
Research is breadth work, the one place many parallel agents pay off. Nothing about it is standing except what it learns:
- **Topics persist**: one folder per question (`research/<topic>/FINDINGS.md` in this repo), with sources.
- **One output shape** (4 Oct, `research/agent-zero-v2/research-outputs.md`): each reader writes one file: Question · Answer (≤8
  claims) · Evidence (URL · date · ≤25-word quote · what it shows) · For us (≤5) · Confidence · Unknown. The completion note only
  points at the file. Later agents grep `research/` first and treat old findings as leads: recheck anything volatile.
- **Fleets are temporary**: `fleet run <name> <briefs...> --topic <dir> --then <synthesis.md>`: Lunas fan out, each brief with
  an objective, output format, sources to prefer and a boundary (Anthropic's four); one synthesis job (Sol: judgment) reads
  every output and updates FINDINGS.md. Effort by rule: 1 reader for a fact, 3-5 for a comparison, up to 10 for a survey.
- **Visible**: the manifest is the state; Agent Base's Research page shows running fleets (a dot per job), the synthesis step,
  and every topic. A finished topic that changes a decision becomes a Look for Shaan.

## Memory (Shaan, 4 Oct: "make your own memory systems ... which doesn't add complexity"; research/agent-zero-v2)
Memory is files in git, found with grep: every lab and Letta's 2026 design converge there, and fancier retrieval measured
marginal for coding agents. What we add is that **memory shrinks as the system learns**:
1. **Four places, one job each:** AGENTS.md is the map (how; stable); `.agents/HANDOFF.md` is where work stands (top entry only
   matters); `.agents/memory/` holds one fact per file plus an index; his words stay verbatim and outrank every summary.
2. **Every fact has an owner:** his quote with a date, or an evidence path. No owner, no fact.
3. **The ladder:** a correction becomes a fact. A fact that keeps mattering becomes a rule in AGENTS.md. A rule that must never
   be missed becomes a check (test, hook, `stack-doctor`). Each promotion deletes the step below it, so the best memory is a
   mistake that can no longer happen.
4. **Consolidate at the checkpoint, not in the background:** when HANDOFF is written, delete contradicted or stale facts and
   promote repeated ones. No memory agent, no extra model calls.
5. **Budgets:** the index stays under 25 lines; `count.py` (skill `deletion-pass`) measures it. Add a vector or graph store only
   after file search measurably misses on real jobs.

## What the big companies taught us (researched 3 Oct 2026; sources in siso-firstmate .agents/a0/specs/2026-10-03-stack-first-principles/SYSTEM.md v2)
| Who | What they learned | What we do with it |
|---|---|---|
| **Musk** (the algorithm) | Question every requirement; delete parts and steps; only then simplify, then speed up, then automate. If you are not adding back ~10% of what you deleted, you did not delete enough. | Every clean-up starts with a deletion pass (the stack index, 735 items). New tools are the last resort, not the first move. |
| **Cognition** (Devin) | Actions carry implicit decisions; parallel writers make incompatible ones. What works: many agents add intelligence (review, a second strong model, map-reduce) while writes stay single-threaded. "The open problems are all communication problems." | One writer per codebase. Parallelism across projects and in breadth work only. |
| **Anthropic** (multi-agent research) | Multi-agent pays for breadth-first research, not coding; ~15x the tokens of chat; early versions spawned 50 sub-agents for simple questions; outputs go to files, not through the lead; a brief needs objective, output format, tools/sources, boundaries. | Research fleets (Luna fan-out, Sol synthesis); effort-scaling rules in every brief; results land in topic files. |
| **Anthropic** (long-running harnesses) | Each session starts fresh, reads a progress file and git log, checks the app still works, does one failing feature from a feature list, commits small. | Fresh context per job; plans and maps are files; one job, one check, one commit. |
| **OpenAI** (harness engineering, 1 M lines, no human code) | The repo is the only truth; AGENTS.md is a ~100-line map, not a manual; plans are versioned files; the app boots per worktree and agents drive it in a browser to verify themselves; agent-to-agent review; recurring clean-up jobs encode golden principles; "corrections are cheap, waiting is expensive". | Short-map boot files; agents verify their own UI; few blocking gates, fast fixes after. |
| **Stripe** (Minions, 1,300 PRs/week) | One-shot unattended agents; a blueprint where git, lint, tests and PR are code and only the change is a model; at most 2 CI rounds; isolated pre-warmed boxes; started from where the work is discussed. | Deterministic chain around a small creative core; 2-round cap, then up a tier. |
| **Ralph loop** (Huntley) | `while :; do cat PROMPT.md | agent; done`: fresh context each turn, one task, a check that cannot lie. | Jobs are one-shot with a machine check. |
| **Cursor** | Up to 8 agents on isolated worktrees, often on the same task; keep the one that works. | Best-of-N on cheap models before one expensive try. |
| **Gas Town** (Yegge) | Rebuilt a human org (mayor, watchers, refinery) and learned: structure beats agent count; start with 2-3. | A warning: the human-org metaphor creeps back; we watch for it. |
| **Kubernetes** | Level-triggered controllers: act on the current state every loop, never on an event, so a lost event is harmless. | No pings or notices; state files plus loops; screens show state. |

## Build principles (how a change gets made and shipped)
1. **Question the requirement in his words first.** If you cannot quote what he asked, you are building the wrong thing.
2. **Add beside his design; never swap it out** (3 Oct: the side nav). Mock first when anything he already uses moves.
3. **One writer per codebase, on its dev branch; Agent Zero lands dev to main; live only from main.**
4. **Test what must never break, look at what is taste.** A small, fast gate (the app boots, chat sends, an agent opens, no
   page errors, data routes answer) decides landing in minutes. Layout and style are judged by a screenshot beside the mock
   and by Shaan's eye, not frozen into tests that break every time the design changes (3 Oct: "our way of doing the testing.
   This is stupid. This is extra stuff in the loop"). Slow suites run after live, never in front of it; a red smoke check
   after live rolls back by itself.
5. **The queue is visible.** What is waiting to go live, and why, shows in Agent Zero's Shipping chip; nothing waits silently.
6. **Every job ends with evidence**: the check output and, for UI, a screenshot of the real app.
7. **Small and often.** A change he can look at today beats a perfect one next week.

## The shape
- **Shaan** <-> **Agent Zero** (one Claude agent): one conversation for intent; one board for state and looks.
- **Agent Zero** compiles intent into jobs (goal in his words, a check, map pointers, budget, tier) and judges results against
  his words; reads the board, not chats; if it dies, a fresh one reads the board.
- **Jobs** run one-shot on Codex (Luna first) in a fresh worktree; a script runs the check; pass goes to the ship queue.
- **Fleets** run breadth work in parallel (research, variations, audits): `fleet run <name> <briefs...>`; their manifest is the
  state the board reads.
- **The reconciler** keeps declared states true with known safe remedies; only the irreducible reaches him, as a line that
  clears itself.

## The plan (in Musk order)
1. **Index** every moving part (fleet `stack-index`, 3 Oct: launch agents, hooks, skills, Codex setup, tools, scripts, brain,
   memory, Agent Base's old-org code, state dirs), each classified by reading: keep / merge / delete / rewrite.
2. **Delete and merge** from the index: reversible (estate archive), committed per area, checked after each.
3. **Simplify** to one job format, one loop, one board, one source per fact; rewrite the brain and AGENTS.md as short maps.
4. **Accelerate** the checker: Agent Base boots per worktree on its own port, agents drive it; parallel suites; auto-revert.
5. **Automate**: job dispatcher (best-of-N, tiers, 2-round cap), reconciler, the Look lane and taste memory.
