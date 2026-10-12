# ADR 0001: Reason from the budget; no hard caps on agents

**Status:** accepted, 6 Oct 2026 (Shaan). **Applies to:** Agent Zero and every agent it briefs.

## Context
At 23:10 on 6 Oct, UI-HUB launched 15 Sonnet sub-agents and 5 background jobs at once. Agent Zero's brief had told it to
run "one per library". Several other chats had sat at about 80% context for a while, so the 5-hour Claude window was
already mostly spent. The fan-out finished it off, and the laptop (load 32, swap full) took the rest.

Agent Zero's first fix was a hook that refused a fourth sub-agent. Shaan reversed it the same evening:

> "it shouldn't have a hard cap. None of these agents should have a hard cap. It's just like, I don't know, he should have
> checked the usage allocation available and figured out and reasoned if it was a more effective way to do it, you know?
> ... some agents genuinely might need more than three ... that's good just reasoning principles. Like, surely Agent Zero
> should have his own ADR so he knows how to make right decisions"

And on the work itself: "all of the sites have repos so like if it just scraped the sites itself it would be able to find all
of the repos and all of the free comps ... he didn't really do too much brain [reasoning] himself".

## Decision
Agents decide how much to spend by reasoning about the budget in front of them. Nothing caps them in code. A wrong call is
fixed in the reasoning (the brief, this ADR, a principle), not by adding a gate.

## How to decide before spending (any agent, any fan-out)
1. **Look at the budget first.** Before anything bigger than one turn:
   - the plan window left: the Agent Base usage orb or `curl -s http://127.0.0.1:5401/api/usage`;
   - who else is burning it: the hosted chats and their context (`~/.local/state/agent-base/hosts/*.json`, `ctx.pct`);
   - the laptop: `uptime`, `sysctl vm.swapusage`.

   A thin window or a hot laptop means fewer, cheaper moves now and the big fan-out after the reset.
2. **Does this need a model at all?** Fetching a sitemap, a registry JSON, a repo or a licence is a script (`curl`, `git
   clone --depth 1`). A model is for judging and writing. Scrape first, reason over the result.
3. **Cost it.** Tokens ≈ calls × context. Fifteen sub-agents each re-reading a brief plus a site cost about fifteen times
   one good script plus one reader. Say the rough number to yourself before launching.
4. **Pick the shape that wins on cost × quality × time.**
   - Parallel is right when the jobs are independent, the window can carry them, and waiting costs Shaan.
   - Batch related items into one sub-agent instead of one per item.
   - Keep the judging yourself; sub-agents fetch and summarise.
5. **Check the laptop's load, not just tokens.** Browsers, dev servers and checks share one machine. Close what you open.
   Use one headless browser with tabs, not one per worker.
6. **Write the reasoning down in one line** in your HANDOFF or card, for example: "window ~40% left, 11 libraries: script the
   registries, then 3 batched readers". It makes the call reviewable.

## How Agent Zero applies it
- **Briefs give intent and the budget question, never a per-item fan-out.** Agent Zero's UI-HUB brief said "one per
  library"; that was the bug.
- **Before starting or waking owners, Agent Zero looks at the window and the laptop.** Big starts wait for a reset when
  the window is thin; that's what Shaan did with LAPTOP-PERF ("queue right when the next hour resets").
- **Compaction is spend too.** Chats sitting at 80% context burn every call. Owners compact at about 30%, and Agent Zero
  checks this.
- **When something goes wrong, the fix order is:** fix the reasoning (brief, ADR) → fix the information (make the budget
  visible where agents look) → only then code, and never as a cap Shaan didn't ask for.

## Consequences
- Agents can spend more when it's worth it.
- Agent Zero owes them a visible budget: the usage endpoint has to be fresh. It said "Waiting for the burn source" at
  23:25 on 6 Oct, and LAPTOP-PERF and AGENT-BASE should fix that.
- The retired cap hook is in `_archive/2026-10-06-subagent-cap-hook/` (siso-harness-lab commits bc1a3e3 and a4c1cef).

## Addendum, 7 Oct: pick the cheapest model that can do each job
Shaan: "Surely we can use haiku subagents Haiku subagents might be dumb But they can search stuff and pull in data".
- **Haiku 4.5:** searching, fetching pages, pulling data, listing files, extraction to a fixed shape. Cheapest, and fine wherever the output is checked.
- **Sonnet 5.5:** reading code and docs and summarising them against a question.
- **Opus:** the reasoning, judging and writing. The owner keeps that.
- **One level only.** Sub-agents never launch sub-agents. Shaan, 7 Oct: "I would be wary though too many sub-agent chains ... would cause issues". The owner fans out; nobody below it does.
