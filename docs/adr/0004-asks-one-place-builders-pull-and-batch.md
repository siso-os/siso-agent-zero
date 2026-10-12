# ADR 0004: Every ask goes to one place; builders pull it and batch it

**Status:** accepted, 6 Oct 2026.

## Context
Shaan talks mostly to Agent Zero now. On the evening of 6 Oct, his asks were spread across verbatim files in `_data/ab-feedback/`, `_data/a0-home/` and `_data/ui-hub/`, task records and one-line pings. One builder sat on two finished rounds waiting for a word that never came. He said:

> "there should be a spec location where all of the stuff we write gets dropped in a place, tracked in the state or something that the agent-based builder always knows to check, and he can check multiple tickets at once and see if they can be done in one run ... they can understand the nuance on their timestamps as well, so it sees what might overwrite others ... newer specs might supersede other stuff unless agent zero disagrees"

## Decision
1. **An ask is a task with a spec**, filed by Agent Zero the moment he speaks:
   ```
   bin/ask new --project P --owner OWNER --his "<verbatim>" "<title>" [--touches area,area] [--supersedes t-N]
   ```
   - It writes `asks/<project>/<YYYY-MM-DD-HHMM>-<slug>.md`, or links an existing spec with `--spec`.
   - It creates the task (`tasks/t-NNNN.json`) at stage `specced`.
   - His words stay verbatim in both.
   - There's one store: no second tracker and no separate inbox.
2. **Builders pull; nothing pings them.** At the start of every round, an owner runs `ask queue <OWNER>`. It shows:
   - its open asks, oldest first;
   - asks grouped by the area they touch, so one run can take a whole group;
   - superseded asks folded under their replacement.
3. **Timestamps decide overlaps.** Where two asks touch the same thing, the newer words win, unless Agent Zero has written otherwise in the newer spec. Agent Zero sets `--supersedes` when it files an ask that replaces an older one. The builder can also see overlaps by area and should say which way it read them in its HANDOFF.
4. **Ideas aren't asks.** Stage `thought` stays out of the queue until Agent Zero specs it.
5. **Done means shown:** `ask done <ids> --evidence "<sha, URL, before/after shots>"` moves the asks to live (ADR 0005).

## Consequences
- Agent Zero's job when Shaan speaks: file the ask and set the owner, the touched areas and any supersession.
- An owner's brief only needs one rule: run `ask queue <NAME>` first.
- Ask history is in git (`tasks/`, `asks/`), and the Tasks panel in Agent Base already reads the same store.
