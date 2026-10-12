# ADR 0002: One Opus owner per surface; Shaan talks to them directly; Agent Zero keeps the data

**Status:** accepted, 6 Oct 2026. **Replaces:** the 3 Oct "one Claude agent, Codex builds, no standing owners" arrangement in practice. That ran on Codex, which is out until 12 Oct 23:05.

## Context
On 6 Oct, Codex was out and Shaan wanted outcomes, not relays: "set up one opus owner ... we can message to potentially one shot the shit and he's gonna auto compact on like 30 ... get some preview urls". Over the evening that grew into seven owners: STREAMING, OPERATOR-UI, AGENT-BASE, AB-MAP, A0-PANEL, HALO-LOGO and UI-HUB. They shipped (Agent Base 293dcd0 → 0d33b3a, AB-MAP's map, A0-PANEL round 1, logo round 3) while Shaan talked to each of them in its own chat.

What broke along the way, and the rule each one taught:
- Owners waited on a "ship" word that Agent Zero never passed on. Rule: owners ship their own rounds inside their gates.
- Chats sat at 50–80% context. Rule: autocompact at 30% (`opus-chat` sets `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=30`).
  8 Oct ~19:50, Shaan: "bump auto compact to I think 35% will be better that last 5% goes a long way": now 35% (`A0_COMPACT_PCT` default;
  running owners pick it up at their next relaunch).
- New chats were filed as workers under dead owners. Rule: Agent Zero fixes the registry the moment a chat starts.
- Links sat in panes that Shaan never opened. Rule: owner cards carry the link, and the panel shows it.

## Decision
1. **An owner is one Opus chat per surface or outcome**, started with `bin/opus-chat NAME DIR BRIEF`.
   - The brief holds his words verbatim, the scope, the ship path, the gates and the hard lines.
   - The owner reasons, builds, ships within its gates, and keeps its card current: `~/.local/state/a0/owners/<NAME>.json`, protocol `_data/ab-feedback/OWNER-CARD.md`.
2. **Shaan talks to owners directly.** Agent Zero does not relay his words or re-brief them by message.
   - A handover is a file plus one line (`a0-tell <pane> "read <file>"`).
   - His verbatim feedback goes in a dated file in the owner's folder, and never gets summarised away.
3. **Agent Zero keeps the data** that the screens show:
   - the registry (owners visible under the right project);
   - the owner cards;
   - the Today pad (`.agents/a0/scratchpad.json`);
   - tasks (`a0-task`);
   - release notes (a missing note shows "Outcome not recorded").

   It also watches context and budget (ADR-0001) and cold-reads anything that goes to production.
4. **Surface ownership is written down** (`_data/ab-feedback/OWNERSHIP.md`), so two owners never write the same surface.
5. **No approval gates** (ADR 0005, later the same night): owners ship and show; what waits for Shaan is only what physically needs him.

## Consequences
- More chats are open at once, so Agent Zero watches context and the laptop (LAPTOP-PERF, from 00:20 on 7 Oct, owns making that cheap).
- When Codex is back, owners may hand bounded building to Codex per `routing.json`; the owner stays the reasoner.
