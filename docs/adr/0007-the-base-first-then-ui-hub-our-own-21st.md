# 0007: The base first; then UI Hub, our own 21st.dev, as a SISO OS module

**Date:** 8 Oct 2026, ~22:30 +07. **Status:** decided. His words in full: `words/source/2026-10-08-2230-research-base-first-ui-hub-21st-verbatim.md`.

## His words (verbatim excerpts)
> ~22:25: "Before we immediately map though, let's make our base, this app, this site, the back end, figure out how this all fits
> together, the estate, it needs to be fitted together and reasoned and put in a way where I can see it and we can work with it
> and improve it ... I should have a task list for that agent-based project ... if we do have spare compute like right now then we
> would know what to be doing and it wouldn't be wasted tokens"

> ~22:29: "we could literally make our own version at 21st.dev ... they literally have the whole UI schematic on how it should work.
> All the pages you should have and, like, we'll add in our own pages ... Or at least it's just an internal tool for us ... my own
> 21st.dev with all of my comps ... with my own bookmarks And my private stuff ... Which my agents can see and interact with Which is
> kind of like the key fucking thing here ... Draggable widget system, this is exactly what we fucking needed ... we've got our own
> agent base, we can have our own UI base and have that sub moduled as a module in the agent base ... they get bookmarked and then
> we can use, they get used across the board and the agent skills and all of that shit that are needed for that are within that
> package ... Agent Zero, State, New Direction ... AgentBase is made, now it's UiHub Because we actually needed to help us because
> the UI we're making on the operator UI And just in general was just dog shit ... we need to go one step beyond components like
> shells, layouts ... maybe even image gen tools ... once we get the base done we can get agents to do peripheral research which is
> where we 10x we just need the base"

> On the side nav: "there needs to be a clean way to actually see this and display this In my side map, I can't have all of those
> shown at once It would make my shit way too messy"

## Decision
1. **The base first.**
   - Agent Base is made: it runs on the Mac mini, working its own queue.
   - The SISO site is being built.
   - The backend becomes one agent record per agent (t-0562).
   - The SISO map (`docs/maps/siso.json`) shows how it all fits together, with a task list per owner.
   - Peripheral research runs behind all of this, on spare tokens (ADR 0006).
2. **UI Hub is the next base: our own 21st.dev.**
   - Take 21st.dev's structure as it is: its pages and how they work. That covers browse, categories, the component page with a
     live preview, code and an install line, bookmarks, and widgets, including the draggable widget system.
   - Fill it with our data: UI Hub's catalogue (1,182 items, his 138 curated picks), his bookmarks, our own components and his
     private things.
   - Go a step beyond components: shells, layouts, sections, pages and the tools we found, such as image generation.
3. **Internal first.** It is his and his agents'. Agents use it through the CLI (`bin/uihub`, which exists) and an MCP. The agent
   skills for using UI ship inside the package. Public later, if at all, on free Cloudflare hosting.
4. **Licences.** Structure and ideas are taken freely. Code is copied only where its licence allows; record the licence on each
   item, as UI Hub's ADRs already require.
5. **A SISO OS module.** It lives in its own repo (sisodias/siso-ui-hub), and Agent Base takes it as a module. UI-HUB builds it;
   AGENT-BASE integrates it.
6. **Owner: UI-HUB again.** It is its own Opus on the Mac mini, with Haiku helpers. SISO-AGENCY keeps Sites and the claim engine,
   which is tabled.
7. **The side nav stays clean.**
   - Projects collapse to one line.
   - Only sub-projects that are working, or need him, surface.
   - Everything else is one click into the project (t-0563).
