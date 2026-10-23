# Agent Zero — state & compact prompt

Run this (1) before any compaction, (2) whenever Shaan asks "where are we", (3) every
time you spawn or close an owner. It rewrites `AGENT-ZERO-STATE.md` in place. The
file is the only thing a cold successor reads before acting, so it must be complete
and it must be short: **under 120 lines**. If it is longer, you are storing history
in the wrong place — history goes in `HISTORY.md`, decisions go here.

## What to write, in this order

### 1. Header
`# Agent Zero — state at <YYYY-MM-DD HH:MM local>` and one line: where you run
(pane id or "laptop resume"), what your last completed action was.

### 2. Shaan's standing intent — verbatim, not paraphrased
Read `/opt/siso-agent-zero/SHAAN-INTENT-LOG.json` (every prompt he has typed on this
project, word for word). Copy into this section the **five to ten most recent prompts
that still have an open consequence** — quoted exactly, with timestamp. Under each,
one line: what has shipped against it, what has not. A paraphrase is not allowed here;
the whole point is that the audit can diff his words against the fleet's work.

### 3. Fleet table
One row per pane: `pane | owner | domain | state (working/idle/blocked/done) | context % |
$ | brief file | last verified URL`. Read the statuslines, do not ask the owners.
A "done" owner has a `HANDOFF-*.md` in `work/`; if it does not, it is not done.

### 4. Decisions made since the last state
Bullets, one line each, with the time: what you decided, why, what it replaced.
Include the ones that turned out wrong, marked WRONG, with the correction.

### 5. Open, needing Shaan — the only list he reads
Each item: what it is, why only he can do it, the exact click or answer needed.
Nothing an owner could do belongs here. Re-check every item against the intent log
before writing it — today two "asks" on this list were things owners could do themselves
and one was a blocker that never existed.

### 6. Hard-won facts, deduplicated
Append only facts that cost an hour and are not already in the `siso-internal-labs`
skill. If a fact belongs in the skill, put it in the skill and delete it here.

### 7. Next three actions
Exactly three, in order, each one sentence, each something you can start without
anyone's answer.

## After writing the state

```sh
python3 /opt/siso-project-team/tools/fleet-status --team-dir . --json fleet-status.json
python3 /opt/siso-project-team/tools/render-front --team-dir .
```
The numbers and the team page are generated from what is true, on every state write, never on a
timer; commit both with the state. Shaan reads the page at the team's `/agents/` path behind the login.

## Rules
- Prove before writing: every URL in the file was loaded in a browser today; every
  "done" has a screenshot path. If you did not look, write "not verified".
- No walls: a reader with no context finishes the file in two minutes.
- Do not write owner messages here. Owners write handoffs; you write decisions.
- After writing: `git -C /opt/siso-agent-zero add AGENT-ZERO-STATE.md && git commit -m "state: <time>" && git push`
  — state that exists only on this box is state that can vanish.
- Then post one console card to Shaan only if section 5 changed.

## Intent log maintenance
`SHAAN-INTENT-LOG.json` is regenerated from the laptop transcripts by
`tools/intent-log.py` (every `user` turn that is not a tool result, a relay, or a
command). Regenerate it at the start of each state write. Never edit it by hand.
