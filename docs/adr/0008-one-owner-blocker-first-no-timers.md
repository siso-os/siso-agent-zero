# ADR 0008: One owner, the blocker first, what we hold, no timers

**Status:** accepted, 11 Oct 2026. **Amends:** ADR 0002 (Agent Zero no longer relays to or judges an owner's work) and ADR 0005
§4 (a sign-in to his accounts is not "physical" when we already hold the login).

## Context
Halo v2, 10-11 Oct: about 17 hours, roughly 1.15B Claude tokens between Agent Zero and HALO plus two builders. Real results
(v2 live on his rooms twice, ten failure drills, six night-breaking bugs fixed), but the goal, a full night on three sites,
never ran: it waited about 10 hours on his CamSoda and Stripchat sign-ins while the agents polished around it. Agent Zero sat
above HALO, relaying, assigning and breaking ties, and watched it on a timer.

> "you were naturally translating things to him as a bit of a worker ... he's talking about Agent Zero this, Agent Zero that,
> Shaan approved this, because we just didn't give him the full autonomy ... adding in extra agents to the top end kind of
> fucked it"
>
> "why was it waiting on logins when I told you a billion times that we already have logged in somewhere and then you could
> just use those details to do it"
>
> "how can we make sure we never waste tokens on bullshit like this again ... We wasted about 50% of our weekly budget"

## Decision
1. **One owner per product, with full autonomy.**
   - It holds the goal with Shaan and decides everything else.
   - Agent Zero hands over its reasoning once, then sends nothing. It reads the owner's card only when Shaan asks.
   - Extra builders under an owner only when the owner itself asks, and only for a stated reason.
2. **The blocker first.** Before any other work, the owner names what stands between now and the goal and removes it. Work
   that doesn't move the goal waits while a blocker stands.
3. **Use what we hold.** Logins, sessions, keys and stored passwords for his own accounts get used. They are never asked
   for again. Only a captcha or a code on his phone is his. "Hold" means our own stores and the browsers we run (the keeper's
   Chromium signs in with the stored password). Never sweep other apps' cookie, password or keychain stores: on 11 Oct 18:11
   that got HALO's chat flagged by Anthropic's classifier and ended it.
4. **No timers.** No agent wakes itself or another agent on a schedule. Wait on one event: a merged PR, a done file, a
   finished command.
5. **List what the old thing does before rebuilding it.** Every feature is marked kept, replaced on purpose (why) or
   missing.

## Consequences
- HALO owns Halo streaming alone (`partners/halo/oracle/.agents/FROM-AGENT-ZERO-2026-10-11.md`). HALO-WEB and HALO-OPS close
  once their checkpoints are in HALO's hands.
- The three rules every agent must see (blocker first, use what we hold, no timers) are in the brain, `~/.claude/CLAUDE.md`.
