# The Elon pass on the agent stack (A0, 4 Oct 2026 ~01:45)

Shaan, 4 Oct: "I thought we were going through with Elon. What would Elon do at this point? What would Elon must do?"

## The honest answer
Elon would stop me building. Tonight I deleted some, then built a new repo, six tools, four skills and a job runner plan: step 5
(automate) before steps 1-2 were finished. The algorithm's order is the point: an automated broken process is still broken.

## Step 1: every requirement has a named person
Each tool, hook, skill, launch job, test suite, instruction section and app feature must name the Shaan quote (with date) that
requires it. "An agent thought it was useful" is not a requirement. No quote: it is deleted. Most of the stack was asked for by
agents, not by him.

## Step 2: delete, with targets (counted 4 Oct 01:45)
| Part | Now | Target | Notes |
|---|---:|---:|---|
| Launch agents | 35 | 10 | keep: Agent Base app + queue runner, caffeinate, A0 watchdog, herdr restore, backups, renewals, Contacts fix, voice |
| Hooks (every Claude session) | 21 | 5 | each hook runs or injects on every session or tool call |
| Instruction file every Claude agent loads | 21 KB | 4 KB | a map, no models, no owners, no messaging |
| Instruction file every Codex agent loads | 20 KB | 4 KB | same |
| Claude skills / Codex skills | 55 / 22 | 15 / 8 | |
| Agent-stack tools (harness-lab bin) | 33 | 12 | |
| Agent Zero script folders | 34 bin-az + 190 upstream | 0 | siso-firstmate retires |
| Agent Base test suites | 99 | ~20 behaviour suites | delete the 13-25 already red on main and every layout/copy assertion |
| Task records | 272 (153 done, 57 dropped, 51 owned by closed agents) | one short open list | |
| Links in ~/.local/bin | 70 | 0 | launchers or nothing |
If we never add back about 1 in 10 of what we delete, we did not delete enough.

### Progress (4 Oct ~02:30, each read before cutting, archive `_archive/2026-10-04-elon-pass/MANIFEST.md`)
| Part | Before | Now | Note |
|---|---:|---:|---|
| Brain (Claude / Codex / omp) | 21 / 20 / ~20 KB | 3.1 / 3.2 / 2.8 KB | harness-lab e26aa22; budgets enforced by compose-brain.mjs |
| Hooks (Claude + Codex) | 21 + 6 | 5 + 2 | harness-lab 30fd904; both harnesses start and answer |
| Launch agents | 35 | 34 | target 10 was set before reading: most are business services (HALO, clients, guest gateway, Postgres) or real repairs (memory guard, Contacts fix); only spine-delta-sync was dead |
| Skills Claude / Codex | 55 / 82 | 47 / 70 | old-org, duplicates, cmux (not running) |
| Harness tools | 32 | 28 | the rest have callers in Agent Base or the login launchers |
| ~/.local/bin links | 68 | 18 | 44 now launchers, 6 dead removed; the 18 are package-manager links (uv, pipx, cursor), which re-create them |
| Live smoke false rollback | - | fixed | the runner had no playwright; Agent Base 709640b live |

## Step 3: simplify what survives
One job format, one loop, one board, one source per fact, one Agent Zero repo, one instruction map per harness.

## Step 4: accelerate
The one number: minutes from his words to live. Landing is now 45 s; the slow part left is everything before landing.

## Step 5: automate, last
The job runner (best-of-2 cheap, check outside the model, 2 rounds, up a tier) waits until steps 1-4 are done.

## The idiot index
Elon's measure: what a thing costs against the cost of its raw materials. Ours: tokens per change that went live. 2-3 Oct:
8.2 B Claude tokens for a few dozen landed changes; 3 Oct Fahmy A/B: 25.6 M Codex tokens for 9 fixes. Measure weekly; it must fall.

## Order of work from here
1. Agent Zero compacts (it is the most expensive part: ~500 k context).
2. Delete to the targets above, area by area, each with its requirement check, reversible, checked after.
3. Only then the job runner.
