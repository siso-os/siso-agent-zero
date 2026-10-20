# ADR 0010: Self-upgrade loop and the upgrade log

**Status:** accepted, 19 Oct 2026. **Builds on:** ADR 0005 (no approvals) and ADR 0009 (standing authorization); the
`a0-upgrade` pipeline (`bin/a0-upgrade`, u001-u011).

## Context
Shaan, 19 Oct: "every so often you should be upgrading yourself and send off haikus to come up with ideas ... there
should also be a tracking log in ADR for Agent Zero on what you're upgrading and why and what I've noticed to be good
upgrades and what I've noticed to be bad upgrades".

## Decision
1. **The loop.** Every 30 minutes a fresh thread reads the new lines of `~/.claude/lessons/LEDGER.md`, Shaan's new words
   (`siso/intent/source/`) and seat failures (`a0-upgrade brief`). It files at most three ideas with `a0-upgrade add`
   and hands each id to an `upgrader` Haiku sub-agent. The schedule is set up separately; this ADR fixes its shape.
2. **Auto or ask**, as in the `a0-upgrade` header. Auto: A0's own wording, checks, logs and Haiku prompts. Ask: anything
   Shaan sees or does differently, a seat he is working with, model or spend routing, a safety rule, or removing a rule.
   An upgrader may move auto to ask, never ask to auto.
3. **Every upgrade is logged** with its why in the store (`~/.local/state/a0/upgrades.jsonl`). `docs/upgrades/LOG.md` is
   generated from it by `a0-upgrade log`: one row per upgrade (id, date, idea, why, status and PR, verdict).
4. **Shaan's verdict** is the column that counts. `a0-upgrade verdict ID good|bad --note TEXT` stores it, in his words
   where he gave them, and regenerates the log. Until he gives one the row says *pending Shaan*. A verdict is set only
   from something Shaan said or did, never by the upgrader that shipped the change.

## Seeds
- u013-u017: pending Shaan (open ask PRs).
- u019-u021 (the a0-await series): bad. Shaan 18 Oct: false done pings, stop pinging on sub-agents.

## Consequences
The log is the record of what Shaan has noticed to be good and bad. Before filing an idea, the loop reads it and does
not repeat a bad upgrade's approach without a reason.
