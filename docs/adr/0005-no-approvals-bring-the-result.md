# ADR 0005: No approvals; bring Shaan the result

**Status:** accepted, 6 Oct 2026. **Supersedes:** "wait for his word on each exact action" wherever it appears in Agent Zero's briefs, except for the physical limits below.

## Context
> "i don't like approvals as well i hate approving stuff i almost end up always missing it and never approving i don't want any approvals approval should be based off first principles and you should just be bringing me the result bringing me the work so i can look at a url reason hopefully if it ui work for the agent base it be before and after screenshots ... once i see something i can tell you improvements but i have to like see it right"
>
> "i'm literally giving you full full authority and full reign"

Approval steps cost time, and they got missed: AGENT-BASE held two finished rounds for a "ship" word.

## Decision
1. **Agent Zero and its owners decide from first principles and act.** The question isn't "may I?". It's three questions:
   - Is it reversible?
   - Who does it touch outside SISO?
   - Is it proven on DEV?
2. **Every result comes to Shaan as something to look at:**
   - one URL;
   - for UI, before/after screenshots of the changed components, at the sizes he uses (1440, and 1008 for HALO);
   - three lines on what changed.

   He reacts by voice, and his reaction becomes the next ask (ADR 0004).
3. **Ship by default:**
   - Agent Base (his own tool) ships every round.
   - Product DEV ships every round.
   - **Production and main for products:** Agent Zero decides after a cold read of the proof, with a rollback ready, and reports with the URL. No approval round-trip.
4. **What still waits for Shaan is physical, not permission.** These need him or someone else to be there, so they're booked as sittings, not asked as approvals:
   - his identity, documents or accounts (sign-ins, KYC, a UK passport upload);
   - a real person on camera (a model going live);
   - money beyond the agreed budget;
   - speaking as him to other people (messages, posts).
5. **The hard lines stay:**
   - no secrets in output;
   - no private data in git;
   - never message anyone as him;
   - never open URLs on his screen;
   - no force-push or deletes (archive instead);
   - Cam's code stays in Cam's repo. (superseded 23 Oct 2026, Shaan: the CRM is HALO code in HALO-AGENCY/halo)

## Consequences
- Briefs drop "when Shaan says ship". Owners ship and show.
- Agent Zero carries the judgement. Production calls get a written cold read in the owner's HANDOFF, with the rollback step.
- A mistake is fixed forward and recorded in the ledger, in one line.
