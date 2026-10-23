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


## 21 Oct 2026: curate the existing self files (Shaan's correction)
The existing 30-minute runner is pinned Haiku, never Opus. Each run first checks the self-file map
in AGENTS.md: ≤150 lines, today's Now, memory index <25 lines and HANDOFF's top timestamp ≤24 h.
`python3 bin/a0_self.py` and `look` Stack report staleness as amber warnings; these are not land gates.
The runner consolidates sourced corrections → facts → rules → checks (PRINCIPLES.md). Promote repeated
lessons to short memory lines or file a0-upgrade work; archive superseded text in docs/HISTORY.md or
HANDOFF-HISTORY.md. Source edits use the existing upgrade/land path; mutable state uses a0_data_home.py.
Never touch other builders' dirty files or write into live. No new memory service or framework.

The project Claude Stop hook calls the short a0_self.py checkpoint driver, which detaches its worker
before returning. This survives CLI/SDK teardown, which can cancel async hooks. Stop is a turn boundary,
so it also covers the last completed turn of a session. A tools-free pinned Haiku summarizes only
last_assistant_message into decisions, owner/builder spawns and lessons; no transcript or thinking
blocks are read. The checkpoint lock, session/report hash and A0_SELF_CHECKPOINT recursion marker
prevent duplicate/reentrant writes. HANDOFF retains all previous entries; daily memory notes and
an index pointer retain new lessons. Failure is a warning, never a parent/land refusal. No content
is printed. A missing final report produces no invented entry. Existing running sessions are not restarted.
Hook contract: https://code.claude.com/docs/en/hooks (Stop input, async hooks).

## Existing-source intake (21 Oct 2026)

`a0-upgrade ingest --limit 3` files final corrections from the workspace lesson ledger,
Haiku coaches' `IMPROVE.jsonl`, existing orchestration events' `learned` fields and
harness token findings into the same `upgrades.jsonl`. Explicit source arguments can
also name builder final reports. Content hashes make repeated intake idempotent;
raw transcripts and reasoning are never sources. Candidate scope requires review:
read its evidence, check current source and existing fixes, then choose one concrete
edit; drop already-fixed or irrelevant candidates with evidence. Escalate any safety,
routing, spend or user-experience change through the existing ask path.

The Haiku `a0-review` entrypoint ingests first and ships at most one queued upgrade.
`add`, `ingest`, `ship`, `approve` and `drop` regenerate the existing local upgrade
LOG at `~/.local/state/a0/upgrades.md`; the committed `docs/upgrades/LOG.md` is the
historical snapshot. Runtime lesson text stays in the ignored upgrade store.



Source publication retains a dirty authoring sync (exit 4) and still runs `siso live`, whose own
landed-ancestry and live-edit checks remain mandatory. Other sync failures and any live refusal
still fail the upgrade. This keeps unrelated task/UI edits intact while the self-files advance.
