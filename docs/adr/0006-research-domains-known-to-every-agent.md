# 0006: Research domains: map everything once, world class for us, known to every agent

**Date:** 8 Oct 2026, ~22:20 +07. **Status:** decided.

## His words (verbatim; they outrank the decision below)
> "you can have a long running opus of the goal to map how everything on the internet, and do it all, per domain"

> "people have done it, we're just taking all of their shit, just I don't think they look at other people's shit properly, so
> we're going to look through everything properly, github, everything, on the internet and try and find all of these websites and
> everything that people have collated for us and put it in one place"

> "There's no point doing this unless it's world class for ourselves, right? So that's the UI hub, agent based voice app and any
> other systems that go along with it"

> "we have tokens to spend today ... We don't want to do it inefficiently, that's why it needs to be reasoned and that's why agents
> need to go deep"

> "make it aware for the rest of the agents so other agents can leverage this knowledge in whatever they're doing it's pointless if
> the agent just makes the doc and then no one's aware of it right and this stuff's just made once and seen never"

> ~22:25: "Before we immediately map though, let's make our base ... And we'll probably have done research in the background as well
> because we have tokens."

## Decision
1. **A domain is something we build and use daily.** UI Hub, agent bases (SISO OS) and voice first; the god questions later. No
   domain without a sub-project that uses it.
2. **One engine: the Foundry** (`sisodias/siso-foundry`, built for exactly this: "scrape the content, scrape the people who make it,
   watch them, then research over the result"). Records live in git. Heavy payloads such as previews and videos live outside git, on the Mac
   mini's vault. There is no second research store. What already exists is the domain's starting point, never redone:
   - UI Hub's 1,182 items;
   - `research/harness-rob`;
   - the 735-item stack index.
3. **Every kind of source, per domain.** Each find is one record: where it came from, its licence, a preview where there is one,
   and why it matters. Prose comes after the records. The kinds:
   - code on GitHub;
   - the lists other people already made (awesome lists, galleries, directories), taken first;
   - showcases, such as award-winning sites, with previews;
   - free assets: 3D, images, icons;
   - the people: YouTube, X and blogs;
   - the newest videos.
4. **Leads are kept, not chased.** A related search found on the way goes into the domain's frontier with a reason and a rank. It
   is worked when it ranks top, and never lost.
5. **Known to every agent, or it didn't happen.**
   - Any agent can run one lookup command (an MCP later).
   - It is found through `estate where` and `recall`, and named in the brain's "look before you build" line.
   - Lookups are counted: a pack nobody reads counts as a failure.
6. **In the background, never in the way.**
   - One Opus researcher (RESEARCH) runs on the Mac mini, with Haiku helpers for breadth.
   - It runs on spare tokens: fuzeheritage's weekly window, which would otherwise lapse.
   - It yields the 5-hour window to the base owners, AGENT-BASE and SISO-LANDING. The base comes first.
7. **Public later.** Once the data is world class for us:
   - nice UIs on Cloudflare Workers (free plans);
   - a CLI and MCP, so people and agents use the UI Hub and the rest;
   - each god question gets its own page.

## Consequences
The Foundry gets an owner (RESEARCH; its door said "not yet assigned"). The SISO map (`docs/maps/siso.json`) lists RESEARCH as a
helper that serves every sub-project. Research packs attach to the sub-project they feed (t-0563).
