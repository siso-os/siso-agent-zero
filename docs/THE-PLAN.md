# The plan: how everything SISO is building fits together

Every owner reads this first. It's the whole picture, so no agent works from a slice.

Shaan, 7 Oct 01:50: "we're being too lazy and we're partitioning gate keeping too much of the intent ... you've got to tell me how this all flows together".

His own words outrank this page. Read them in full (they are thousands of words, and they matter):

| Topic | His words (verbatim) |
|---|---|
| The UI system | `~/SISO_Workspace/_data/ui-hub/SHAAN-2026-10-06-2300-verbatim.md` |
| A million free sites | `~/SISO_Workspace/_data/siso-sites/SHAAN-2026-10-07-0015-verbatim.md`, `SHAAN-2026-10-07-0100-maps-research.md` |
| The Operator / HALO UI | `~/SISO_Workspace/_data/operator-design/OPERATOR-UI-OPUS-BRIEF.md` ("My words") |
| Agent Base | `~/SISO_Workspace/_data/ab-feedback/*verbatim*.md` |
| How agents work | `docs/adr/0001`–`0005` (in this repo) |

## The north star (Shaan, 7 Oct 05:20–05:30)
"by the end of the year we could have a million businesses ranked made by sisal agency and we might not have even collected a dollar off of it" · "make something best in the world and sales will follow".

**Inbound only.** The money ladder:
1. about 1% pay a little, which funds everyone's small changes;
2. trust builds;
3. the coolest ~10,000 businesses;
4. replace their software bill with their own business OS (Action Model);
5. business-agency extras.

**Corrections, 7 Oct 04:37** (`_data/siso-agency/asks/2026-10-07-0437-shaan-corrections.md`):
- Real, sourced prices may show; only invented ones are banned, and it depends on the industry.
- Phone-first is a restaurant pattern; every site must be good on desktop too.
- Restaurants first (Shaan judges them), then a list of every industry for him to decide on.
- Footer: ❤️ plus the SISO Agency icon, low key, linking out. No "claim it / take it down" line. The way in is a multilingual onboarding agent, later.
- He'll buy a cleaner domain if one is better than pages.dev.

**SISO Agency's plan, step by step with task ids:** `~/SISO_Workspace/_data/siso-agency/PLAN.md`.

**Usage rule (Shaan, 7 Oct 08:05):** "we have to chill out on the usage on SISO agency and agent base and allocate everything to halo once we get to about 50 percent of our weekly".
- At ~50% of the week: SISO Agency, Agent Base, Rolodex, Library and Life owners checkpoint and pause.
- HALO's owners (STREAMING, MODEL-APP, OPERATOR-UI, HALO-EFFICIENCY, HALO-PLATFORMS) get the rest.
- Agent Zero watches `burn-rate` and makes the call.

**Budget update (Shaan, 7 Oct ~20:00), supersedes the 50% pause for SISO Agency:** "opus ... super high reasoning ... i can buy another clawed account if needs be halfway during the week ... it just needs to make sure we don't go over two clawed accounts per week."
- The ceiling is **two Claude accounts per week**, not 50% of one. SISO Agency's system work runs on Opus at max reasoning.
- When claude-siso-3 nears full, Agent Zero tells Shaan the day before so he can buy the second one; never a third in a week.

## The four things, and why each exists
1. **HALO streaming goes live with real models.** This is the revenue now, for a client (Cam).
   - First real model on 8 Oct.
   - It's also SISO's first real **business operating system for a client**: models onboard, platform accounts run on a VPS behind each model's IP, and an operator watches the live wall.
2. **SISO Agency: a million free sites in a year.** "our whole problem was distribution ... don't talk to me I will talk to you. We'll just set up the sites."
   - The process: find businesses on Google Maps with no website, build each one a good static site, host it free on Cloudflare Pages, and let the site be the outreach.
   - The footer badge leads to the SISO Agency site.
   - "the websites are ... get your foot in the door for business OSs". A claimed site turns into a client, and the client into a business OS.
3. **The UI system (UI hub): the engine that makes all of it look good without iteration rounds.**
   - It has five layers:
     1. principles as ADRs (hover shows a preview card, and so on);
     2. **one catalogue**: open-source components "robbed out of the box", plus ours, each with when to use it, when not to, install, usage and API;
     3. **one inventory** of what every project actually uses (library or custom), with a swap list;
     4. use cases;
     5. intake of new UI libraries at scale.
   - "80% of the tokens can be standardised."
4. **Agent Base: where Shaan runs all of it.** He talks to Agent Zero and the owners there; asks queue up there (ADR 0004); results come back there as URLs.
   - Later it also becomes the **agency base**: HALO and the other main clients, plus the free-sites pipeline (found → built → live → claimed).

## How they feed each other
- **One component catalogue serves four kinds of surface:**
  - **dashboards and business operating systems:** the Operator, Agent Base, a future agency base, a client's business OS;
  - **the native app:** the model app, SISO's nicest UI so far;
  - **consumer landing sites:** Café 89, Kikas, every free site, and the SISO Agency site;
  - **the SISO Agency site itself.**

  Some components suit every kind of surface; some suit only one. UI-HUB says which, and why.
- **HALO teaches the business-OS pattern.**
  - What the Operator proves becomes the vertical template that free-site clients grow into: onboarding, account setup on a VPS, a live desk, per-client workspaces on a VPS and Cloudflare.
  - So **the Operator's UI matters to the million-sites goal**, not just to HALO: its dashboard components are the business OS that free sites sell into.
- **The free sites are a vertical in the UI system.**
  - Shape: one static skeleton plus tokens (colours, fonts, logo, language), versioned components (one fix rolls out to every site), a basket of images per industry, and per-industry research (the top 20–100 competitors, open source, then an Elon pass).
  - UI-HUB owns the skeleton and components. SISO-SITES owns the data, the build, the deploy and the tracking.
- **The SISO Agency site is the front of the engine.**
  - It shows the flex: X sites, Y industries, "built within 10 km of you", a globe.
  - It has a page per industry with our thesis and research, plus a gallery of the sites, and the claim / change / get-a-domain path.
  - Opus designs it with Shaan, from UI-HUB components.
- **Agent Base is both a customer and the control room.**
  - It's a dashboard built from the same catalogue (UI-HUB's 6 swaps go to AGENT-BASE).
  - It's also where every ask is filed and every result is shown.
- **FLEET-COST keeps this affordable.** All of it runs on a Claude subscription, so token burn and laptop load are real limits. It moves agents off the laptop.

## What waits on what (and what doesn't)
- **Going live waits on nothing in the UI.** "making it functional and making the ui nice are two different things". STREAMING signs in, goes live and stops by itself, using stored credentials on the VPS browser. Shaan is needed only for his phone (a 2FA code or a captcha) or his face on camera.
- **Operator polish was waiting only for UI-HUB's swap list. That has landed.** OPERATOR-UI is swapping components now, not doing more iteration rounds.
- **Free-site proofs don't wait.** They start from the Café 89 and Kikas patterns and move onto UI-HUB's skeleton when it lands. Every component used gets recorded in the inventory.
- **The SISO Agency site waits for Shaan's feel plus UI-HUB's first components.** Then it's one design conversation, and Opus builds it.
- **Model-app swaps wait until after go-live.** Nothing touches streaming before then.

## Who owns what now
| Owner | Owns |
|---|---|
| STREAMING | HALO go-live: DEV, then production, then the first model on 8 Oct |
| OPERATOR-UI | The Operator and its one UI + docs hub: function first; component swaps from UI-HUB; no mobile |
| SISO-AGENCY | **The head of SISO Agency** (7 Oct 06:40, `_data/siso-agency/HEAD.md`): owners never message Shaan, they report through state (card, HANDOFF, URLs) and A0 reads it every turn; it holds the whole picture, files asks to UI-HUB and SISO-SITES, accepts their work before Shaan sees it, and runs Haiku/Sonnet sub-agents for research and labelling. A0 no longer relays agency work |
| UI-HUB | The UI system: principles, catalogue, inventory and swaps across every project, surface kinds, verticals, and **`siso-site-kit`**, the one versioned design every free site is built from (`_data/siso-sites/A0-DECISION-site-kit.md`) |
| SISO-SITES | The free-sites engine (Maps data → generator → Cloudflare → tracking → claims), the SISO Agency site's data and pages, and `SISO_Agency` `DIRECTION.md`. **It never designs**: every site is data plus the kit |
| BROWSER | The SISO browser inside Agent Base (tabs, rail, folders, its own window); browser files only; started 7 Oct to redesign the browser with Shaan |
| AGENT-BASE | Everything in Agent Base except the browser, working its ask queue (including A0-PANEL's and AB-MAP's items and UI-HUB's swaps) |
| Agent Zero | This plan, the asks, the data, cold reads, and keeping every owner's picture whole |

Closed on 7 Oct (handoffs in `_archive/2026-10-07-closed-owners/`): FLEET-COST (its fixes are live; the plan to move owners onto the mini is in `_data/fleet-cost/HANDOFF.md`), A0-PANEL and AB-MAP (their items are in AGENT-BASE's queue; the census lives on in UI-HUB's inventory), and HALO-LOGO (round 3 is at https://halo-logo.pages.dev/).

## What the plan was missing: nuance from rereading every word (A0, 7 Oct ~02:45)
Shaan: "what nuance are we missing if you read that thing as a whole ... i feel like you're missing stuff". Each item below is his, with where it lands.
1. **Agents act; they don't come back to him.** "nothing should be authorized the agents have access to do whatever the fuck they need". Asking him is a bug, except for a code from his phone or his face on camera. → every owner (ADR 0005, enforced by Agent Zero).
2. **The product past the site is an agent that makes changes.** "if you want to message us and set up a domain and do any changes, you can message an agent or do a voice chat and it will get done ASAP ... you might have to pay us for the compute". So a claimed site comes with a **change agent** (chat and voice) that edits the site from the kit, and the client pays for compute. That's the ladder from free site to client to business OS. → SISO-SITES (spec), UI-HUB (the widget with an agent face).
3. **The paid ladder:** a domain hookup, changes, "want the code", custom image generation "as a package", then the business OS. Price it so "they'll cover compute and their own cost". → SISO-SITES.
4. **Claim onboarding:** "they put in the URL and then they can see the app request changes and we'll talk to them". A simple portal where the owner enters their site, sees it, and asks for changes, which leads into the change agent. Later this is the agency base in Agent Base. → SISO-SITES, then AGENT-BASE.
5. **The footer badge goes to sisolabs.space,** the real domain, with the "coming soon" lion logo. The sites live there too (subdomain or path, reasoned for ranking). → SISO-SITES.
6. **The tracker counts tokens as well as sites:** "how many sites we've deployed how many tokens we've spent ... how many verticals". The numbers get posted to Twitter and Instagram as social proof. FLEET-COST's token data feeds it. → SISO-SITES and FLEET-COST.
7. **Free updates on a schedule:** "We'll give you free updates every so often anyways". Kit version bumps roll out to every site, and that is the promise to owners. → UI-HUB (versioning), SISO-SITES (rollout).
8. **Look at every vertical we've already worked in.** "him whole look at everything in SISO agency like the UI bases the other client verticals". `SISO_Agency/clients/` already has cafe-89, kikas, restaurant-app, bike-rental, tour-guides, visa-run-da-nang, home-essentials, construction, a dispensary and more. Each is a candidate vertical with a design we've already built. This survey stays on even though the landing page is later. → SISO-SITES.
9. **Industry choice is partly his call:** "per industry, maybe I'll give some a green light, some might just auto be whatever". Rank industries by value and ease of scaling. Cafés now because we have the designs; dispensaries next; "higher value industries" after that. → SISO-SITES (rank), Shaan (green lights).
10. **Industry research stacks into a library:** "one HTML or one MD per ... that data stacks and scales ... distilled reasoning". One file per competitor and site, plus one distilled file per industry, kept forever. It belongs in the Great Library, and its theses become pages on the agency site. → SISO-SITES with the Librarian's shape.
11. **The data shapes the template:** "Scrape the top 10 companies from Google Maps, see what data we have, see how that fits in and shapes the sites". What Maps actually gives (menus, photos, hours) decides what the kit can fill without inventing anything. → UI-HUB and SISO-SITES together.
12. **Images:** "find the API keys" for image generation. Use a basket per industry plus generation for heroes, and make the images we already made swappable. → UI-HUB (kit), SISO-SITES (pipeline).
13. **One package system for every client, not just free sites:** "reuse all of the code across the ecosystem infinitely for any other clients and infinitely update it". The kit's packages (shells, navs, chat widget, faces) are how every client app gets cheaper, HALO included. → UI-HUB.
14. **More than one page:** "maybe there should have been more pages ... a side nav and not one page". The kit supports multi-page sites as well as the one-pager. → UI-HUB.
15. **UI intake at scale is still owed:** using Twitter to find hundreds of thousands of UI sites, deduped and tracked. It's a plan until he says go. → UI-HUB.
16. **Usage is the real limit:** "i don't think we have enough usage Claude usage to justify it". Every owner reasons its spend (ADR 0001), and the mini takes load off the laptop, not off the plan. → FLEET-COST.

**Outreach is his** (7 Oct 02:40): Google Maps "suggest an edit", plus review partners paid on commission. Our side is the machine: lead + spec + kit → site, at mass, plus a list (business, Maps URL, site URL, status) he works from.
