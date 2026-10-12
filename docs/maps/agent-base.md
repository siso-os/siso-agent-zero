# Agent Base: one-go map

Baseline: `origin/main` at `22a6324b0b977330fd1c054da735c5fc6a52703b` (read-only); GET probes against `127.0.0.1:5401` on 2026-10-03. Source references use `path:line` in this baseline. A probe describes the live instance only.

## 1. What it is (5 lines)

| Moving piece | What runs / starts / state | Source |
|---|---|---|
| Web | React 19 + Vite screens, served as `apps/web/dist`; browser dev server `pnpm web` (5410 per SPEC), desktop production page served by node. | `docs/SPEC.md:39-58`; `package.json:4-9`; `services/node/src/server.ts:103-109` |
| Node service | Laptop Node 22 HTTP/WS server, default `127.0.0.1:5401`; `pnpm node` / desktop sidecar. WebSocket bridges herdr terminals and chat streams. | `services/node/src/server.ts:103-108,1900-1958,2368`; `docs/SPEC.md:61-84` |
| Desktop | Tauri 2 macOS app; `pnpm desktop` builds web then `.app`; app launches node child and owns its lifetime. | `apps/desktop/src/lib.rs:1-`; `package.json:7-9`; `services/node/src/server.ts:2353-2368` |
| Edge / tty / launchd | Repo has no launchd plist; `herdr` owns agent panes and terminals; edge is an external/local service, not a repo process. WebSocket tty attach runs `herdr terminal attach … --takeover`. | `services/node/src/server.ts:105,1900-1908`; repo plist search: none (`git ls-tree … | rg '\.plist$'` found only `apps/desktop/Info.plist`) |
| Ship / state | `tools/ab-queue` merges in `_data/worktrees/.../merge`, post-checks in sibling `queue-post`, then invokes `tools/ab-live`; live node/web assets build in a detached temporary worktree, desktop app separately. Runtime state under `~/.local/state/agent-base/`; queue state `~/.local/state/agent-base/ship-queue/`. | `tools/ab-queue:10-28,34-37,248,681-`; `tools/ab-live:1-20,73-85`; `services/node/src/server.ts:110-134` |

## 2. Screen map

App shell: left tool rail + optional side nav; center chat/page/tab; right panel; top tab strip. Side nav rows come from live `/api/agents` plus `/api/org` domain/project registry: pinned rows, Agent Zero, owners with folded crews, workers, empty/error rows. Agent Zero is first/pinned; its own home page opens via its row. On narrow screens the side nav becomes a sheet. App local state persists with `agent-base:` localStorage keys. Sources: `apps/web/src/App.tsx:86-110,1123-1258,1288-1370`; `apps/web/src/components/Sidebar.tsx:101-180,746-`; `apps/web/src/lib/agents.ts:1-`.

| Page / reachable sub-page or panel | How to reach | Shows | Component | API / data |
|---|---|---|---|---|
| Home → Agent Zero, owners, folded workers | Home rail / ⌘B; select face/row; Needs You shortcut | Agent chat, terminal, tasks; hierarchy, pinned agents, empty/down states | `Sidebar.tsx:101-180`; `AgentPanel.tsx:40-141`; `ChatView.tsx:136-` | `/api/agents`, `/api/org`, `/api/agents/:id/read`, chat WS; `App.tsx:1169-1190` |
| Agent Zero page + widget pages | Select Agent Zero; page strip in identity | Hub summary, configurable widgets and task/spend/announcement surfaces | `AgentZeroPage.tsx:77-`; `lib/a0-widgets.ts:1-` | `/api/hub/a0`, `/api/a0/tasks`, `/api/asks`, `/api/reviews`, `/api/announcements`, `/api/spend` |
| Tasks | top row icon; header task count; agent Tasks | A0 tasks / owner tasks and answer panel; phone task sheet | `TasksPage.tsx:1-`; `OwnerTasks.tsx:1-`; `OwnerTasksPanel.tsx:1-`; `phone/TasksSheet.tsx:1-` | `/api/a0/tasks`, `/api/asks`, `/api/agents/:id/timeline` |
| Org chart / project dashboard | top row; select a group/project/mini lane | organization, group/project summary, members and activity | `OrgChart.tsx:1-`; `OrgPage.tsx:1-`; `GroupDashboard.tsx:1-`; `ProjectDashboard.tsx:1-`; `MiniLanes.tsx:1-` | `/api/org`, `/api/hub/org`, `/api/hub/project/:name`, `/api/mini/lanes` |
| Stats / fleet stats | top row Stats | Usage, fleet/agent stats, drill-down | `StatsPage.tsx:1-`; `FleetStats.tsx:1-` | `/api/usage`, `/api/spend`, `/api/agents/:id/stats`, tokens |
| Starred | pinned app page / saved top tab | Starred links | `StarredPage.tsx:1-` | localStorage; browser tab state |
| What’s new / version | version pill | release notes and not-landed changes | `WhatsNew.tsx:1-` | `/api/version`, `/api/version/changes`, `/api/releases`, `/api/not-landed` |
| Servers | top row Servers; can pop to right panel | machine health, agents, tokens, logs | `ServersSpace.tsx:270-`; `panel/OrgCard.tsx:1-` | `/api/servers`, `/api/machines`, optional `/api/servers/:id/logs` |
| Tokens | top row Tokens; can pop to right panel | account spend, limits, usage breakdown | `TokensSpace.tsx:1-`; `SpendPanel.tsx:1-` | `/api/tokens`, `/api/tokens/money`, `/api/tokens/split`, `/api/tokens/fleet`, `/api/spend` |
| Voice → history, stats, dictionary, settings, dated day | Voice rail; side-nav page or day calendar | dictation history/metrics, dictionary and settings | `VoiceSpace.tsx:28-64,132-`; `DictationSpace.tsx:1-` | `/api/voice/{status,history,stats,activity,dictionary,settings}`, `/api/dictation/*` |
| Rolodex → sources, people, person detail | Rolodex rail; choose person/source | People, relationship sources, person entity page | `RolodexSpace.tsx:1-`; `RolodexList.tsx:1-`; `EntityPage.tsx:1-` | `/api/rolodex`, `/api/rolodex/sources`, `/api/rolodex/everyone`, `/api/rolodex/lookup` |
| Life → Today, XP, day history | Life rail (feature/config gated); side nav | routine, counters, checkout, XP | `LifeSpace.tsx:16,132-`; `App.tsx:1241-1248` | `/api/life/*`; local queued events before sync |
| WhatsApp → chats/groups | WhatsApp rail (feature/config gated) | WhatsApp conversation and group proxy | `WhatsAppSpace.tsx:1-`; `App.tsx:1216-1225` | `/api/whatsapp/*` proxy |
| Library → catalog tabs, building/entity, live strip | Library rail; select tab/item; panel | Works, products, assets, live pages, building details | `LibrarySpace.tsx:63-111,317-`; `page/HubPage.tsx:1-`; `page/Figures.tsx:1-` | `/api/library`, `/api/library/building`, console/library data |
| Browser tabs / setup / sign-in / downloads | Browser rail; ⌘T; chat link; agent page strip; tab drop | Per-agent web tabs, suggestions, account setup, downloads, page errors | `Browser.tsx:1-`; `PageRow.tsx:1-`; `browser/SetupSheet.tsx:1-`; `browser/SignInSheet.tsx:1-`; `browser/DownloadToast.tsx:1-` | `/api/browser/*`, `/api/open`; persisted browser tabs |
| Estate world | Estate rail | 3D repo/agent/machine estate iframe | `App.tsx:1242-1248`; `/estate-world/` server route `server.ts:1857-1873` | estate world served by node |
| Agent right panel / chat beside page | Agent row hover/panel control; drop page on chat; pop top page | Org card, subagent pages/asks, chat split, selected app page | `App.tsx:1699-1855`; `panel/SubagentsPage.tsx:1-`; `SubagentsPopover.tsx:130-` | `/api/agents/:id/subagents`, `/api/agents/:id/timeline`, page-specific API |
| Header controls / page strip / folder pop-out / Today chip | Header: back/forward, tabs, new tab, version, spend; ⌘T. Side-nav five page icons can pop to panel. | Navigation history; active-agent tabs + web pages; “⌄ N more” fold; Tasks/Org/Stats pop-out. Agent Zero desktop chat gets a “Today” scratchpad chip; it opens checklist items stored for the day. | `TopNav.tsx:6-32`; `PagePop.tsx:6-49`; `HistoryButtons.tsx:1-`; `Scratchpad.tsx:17-80`; `SpendChip.tsx:1-`; `App.tsx:1157-1180,1368` | local tab/nav storage; `/api/scratchpad`, `/api/version`, `/api/spend` |
| Docs rail item | Rail “Docs” | **Not reachable:** item is rendered as `later`; no Docs page mounted | `App.tsx:1170-1172` | none |

## 3. API map

Node router is `services/node/src/server.ts:1297-1855`; delegated handlers listed below are invoked at `1317-1327`. `GET` probes below are read-only. Mutation routes are documented, not called.

| Area / route templates | Method | Purpose; data read or written | Source |
|---|---|---|---|
| `/api/health`, `/api/version`, `/api/version/changes` | GET | Liveness, running SHA/version, changes | `server.ts:1301-1308,1328` |
| `/api/agents`, `/api/agents/:id/read`, `/api/agents/:id/{timeline,stats,subagents}`, `/api/agents/:id/subagents/:child` | GET | herdr inventory/read; transcript-derived timeline/tokens; sub-agent session summaries/events | `server.ts:1331-1336,1812-1855`; `subagents.ts:1-` |
| `/api/org`, `/api/org/tour`, `/api/org/thumb`, `/api/org/project/:id` | GET; org and project also POST | Organization / project registry; mutations write org registry/files and thumbnails | `server.ts:1337-1357,1592-1597,1689-1732`; `org.ts:1-` |
| `/api/registry`, `/api/order`, `/api/agents/:id/{settle,unsettle,snooze,unsnooze,seen}` | POST | Pin/domain/agent registry and row ordering/status; writes local registry/rows | `server.ts:1734-1764`; `store.ts:1-` |
| `/api/agents/:id/move`, `/api/agents/:id/to-host`, `/api/agents/start`, `/api/open` | POST | Move/spawn/start agent or open local URL; invokes herdr/node/host or OS | `server.ts:1358-1367,1528-1540,1791-1809` |
| `/api/agents/:id/notifications[/…]` | GET, POST | Notifications read, mark/reply/react; local notification store and agent tell | `server.ts:1541-1574`; `notifications.ts:1-` |
| `/api/agents/:id/read` + `/term/:id/ws`, `/chat/:id/ws`, `/host/:id/ws`, `/shell/:id/ws` | GET/WS | Recent pane output, tty attach, terminal transcript chat, hosted SDK seat, local shell; terminal WS takeover changes terminal attachment | `server.ts:1847-1855,1900-1958`; `transcript.ts:1-`; `codex-transcript.ts:1-` |
| `/api/browser/state`, `/api/browser/import`, `/api/browser/blank`, `/api/browser/suggest`, `/api/browser/{chrome-passwords,reveal,download-info,open-download,reach,open-in-chrome}` | GET, PUT, PATCH, POST | Browser tabs/state/history; import reads browser history; other actions access local browser/downloads/Chrome | `server.ts:1368-1470`; `browser-state.ts:1-`; `browser-import.ts:1-`; `browser-downloads.ts:1-`; `browser-reach.ts:1-` |
| `/api/rolodex[/sources|/everyone|/lookup]` | GET | Contact/relationship source and lookup data | `server.ts:1471-1495`; `rolodex.ts:1-` |
| `/api/whatsapp/*`, `/api/life/*` | proxied GET/POST | WhatsApp / Life service; allowed subroutes pass to configured upstream; events/settings read/write there | `server.ts:1496-1509`; `whatsapp.ts:27-70`; `life.ts:26-55` |
| `/api/library`, `/api/library/building`, `/api/library/open-app`, `/api/library/reveal` | GET, POST | Library catalog/building; opens app or reveals local path | `server.ts:1510-1527`; `library.ts:1-` |
| `/api/hub/agents`, `/api/hub/a0`, `/api/hub/org`, `/api/hub/project/:name`, `/api/hub/zeros/desk-digest` | GET | Local/VPS hub agents, A0 and org/project snapshots/digest; cached hub files / task data | `server.ts:1575-1600`; `hub.ts:1-`; `hub-zeros.ts:1-` |
| `/api/a0/tasks[/…]`, `/api/a0/tasks/events`, `/api/a0/tells`, `/api/a0/tells/events`, `/api/a0/transcript`, `/api/a0/tell` | GET, POST | Agent Zero task state/events, tell ledger/stream, transcript; tells write coordination state/send agent tell | `server.ts:1601-1659`; `a0-tasks.ts:1-`; `a0-transcript.ts:1-`; `tells.ts:1-` |
| `/api/selection`, `/api/scratchpad` | POST; scratchpad GET too | Current UI selection log; scratchpad read/write | `server.ts:1308-1316,1606-1625`; `scratchpad.ts:1-` |
| `/api/asks`, `/api/reviews`, `/api/reviews/:id/opened`, `/api/announcements`, `/api/announcements/:id/seen` | GET; mark routes POST | External asks/reviews/announcement records; opened/seen markers | `server.ts:1662-1681`; `asks.ts:1-`; `reviews.ts:1-`; `announcements.ts:1-` |
| `/api/tasks` | GET plus supported task mutation methods | Task query/updates through configured task adapter | `server.ts:1682-1688`; `tasks.ts:1-` |
| `/api/uploads`, `/api/uploads/:image` | POST, GET | Save/read image attachments in local uploads folder | `server.ts:1766-1790` |
| `/api/ended`, `/api/machines` | GET | Recently ended local agents; machine registry | `server.ts:1810-1811` |
| `/api/releases`, `/api/not-landed`, `/api/ship`, `/api/spend`, `/api/usage` | GET | Deploy log, branches absent from live/main, ship queue, spend, token burn | `releases.ts:131-`; `landing.ts:78-`; `ship.ts:137-`; `spend.ts:76-`; `usage.ts:95-` |
| `/api/servers[/…]`, `/api/mini/lanes[/…]` | GET, event stream | Machine health, remote agents/logs; opt-in SSH Mac mini lanes | `servers.ts:764-`; `mini-lanes.ts:207-` |
| `/api/tokens`, `/api/tokens/{money,split,fleet}` | GET | Account usage/limits and spend rollups; source/cache files and service reports | `tokens.ts:1097-`; `tokens-money.ts:253-` |
| `/api/voice/{status,history,stats,activity,dictionary,settings}`, `/api/voice/dictionary/{terms,rules}`, `/api/voice/dictionary/rules/toggle`, `/api/voice/restart`, `/api/voice/speak`, `/api/voice/transcribe` | GET, POST, DELETE | Voice health/history/settings/dictionary; edits write voice state; speak/transcribe call local voice services | `voice.ts:463-590`; `voice-speak.ts:87-`; `voice-transcribe.ts:88-` |
| `/api/dictation/{status,history}` GET; `/api/dictation/{owner,native,events,transcribe}` POST | GET, POST | Dictation status/history, native capture, ownership/events, transcription | `dictation.ts:35-65` |
| `/api/whatsapp/*`, `/api/life/*` mutation routes | POST/other allowed by route table | Configured upstream proxy; no direct local persistence in proxy | `whatsapp.ts:27-70`; `life.ts:26-55` |

WebSockets additionally expose `/term/:id/ws`, `/chat/:id/ws`, `/codex/:id/ws`, `/host/:id/ws`, `/shell/:id/ws`, `/servers/:id/events`; sources: `server.ts:1900-1958`; `servers.ts:743-763`.

## 4. Agents in the app

| Mechanism | How it works | Source |
|---|---|---|
| Local agents | `herdr agent list` is authoritative; node normalizes pane/id, name/title/status/tool/cwd/project/machine/session. Agent Zero recognized from A0 title or its `siso-firstmate` cwd. | `services/node/src/server.ts:94-113,300-365,787-` |
| Transcripts / Codex | Claude JSONL session files and Codex session files provide chat history, token/model/tool calls and child-agent activity; transcript readers poll while viewed. | `transcript.ts:1-45,420-438`; `codex-transcript.ts:1-` |
| Mac mini / remote | `/api/servers` polls machine sources; `/api/mini/lanes` is opt-in SSH for Codex lanes. Org/hub views may separately load Agent Zero and project state. | `servers.ts:59-80,700-`; `mini-lanes.ts:1-35`; `hub.ts:1-` |
| Chat seat vs terminal | Host/SDK chat gets an `siso-host` process and metadata under `hosts/`, streams on `/host/:id/ws`; ordinary Claude/Codex chat is projected from its transcript and sends text through its herdr pane. Term view uses tty WS. This is not a single transport. | `server.ts:131-134,1961-1982,1900-1958`; `ChatView.tsx:136-`; SPEC `docs/SPEC.md:226-257` |
| Sending | Composer routes agent messages through hosted seat when available, else queues pane paste + Enter through herdr; stop is Escape. A0 “tell” has its own endpoint/ledger. | `server.ts:1961-1982,1569-1574,1626-1650`; `Composer.tsx:1-`; `a0-tasks.ts:1-` |
| HUD / tokens / context | HUD reads session context JSON (`~/.local/state/context-ping/ctx`), seat state, model, token/spend caches; chat transcript usage estimates activity/tokens. Fleet tokens from `tokens.ts`; local velocity `/api/usage`; per-agent stats endpoint. | `server.ts:106,723-802,1120-1164`; `seat-hud.ts:1-`; `tokens.ts:705-715`; `Hud.tsx:1-` |
| Sub-agents / flights | Subagent rows derive from Claude transcript tool records and session summaries; events stream; popover groups running/done/crew and token rate. | `subagents.ts:1-`; `SubagentsPopover.tsx:1-160`; `server.ts:1812-1827` |

## 5. Background jobs and loops

| Loop / interval | Behavior and approximate spawn cost | Source |
|---|---|---|
| Agents client poll: 5s; A0 tasks 5s; ended 15s; pings 30s; spend 60s | While views are active; agents request invokes herdr list (up to 12/min per active client; shared node cache/coalescing); other requests are HTTP/file/cache reads. | `agents.ts:87-`; `a0-tasks.ts:26-`; `ended.ts:34-`; `pings.ts:57-`; `spend.ts:26-` |
| Node agent watch: 5s while transcript chat watchers exist | One `listAgents()` per tick regardless of watcher count; about 12 herdr process calls/minute while watched. | `server.ts:787,1966-1980` |
| Transcript watchers: 500ms while chat stream open | Re-read active Claude/Codex transcript; zero subprocesses/minute (file reads). | `transcript.ts:432`; `codex-transcript.ts:147` |
| Server fleet refresh: 30s; health probes: 30s open / 300s idle; mini cache: 30s | Remote SSH/health process calls only for enabled/active machines. | `servers.ts:59,713-`; `servers-probe.ts:27-28`; `mini-lanes.ts:30` |
| Tokens warm: 60s; spend cache: 60s; usage cache: 5 min; landing poll: 5 min | File/adapter/cache reads, not one process per component. | `tokens.ts:705-715`; `spend.ts:8-`; `usage.ts:8-`; `landing.ts:17-` |
| Voice health: 60s, restart retry 4s; app parent watchdog: 1s | Local service checks; parent PID check once/sec, no child process until parent absent. | `voice-health.ts:36-39,184-`; `server.ts:2353-2365` |
| Tells stream / page-watch / command timeout | Event streams tick while connected; the remaining timers are per-operation debounce or timeout, not periodic background work. | `tells.ts:111-`; `webview.ts:166-`; `whatsapp.ts:62` |
| Launchd jobs in repo | None. Voice service or herdr may have external launchd-managed jobs; repo does not define them, so interval/cost cannot be established here. | repository plist inventory; `voice-health.ts:1-` |

## 6. Data files outside the repo

`~` below means the machine running the node (default laptop). Environment overrides are supported. “Other writer” identifies explicit shared producers or possible concurrent app/CLI writers in source, not a claim that they were running during probe.

| Path | Owner / app access | Other writer / source |
|---|---|---|
| `~/.local/state/agent-base/rows.json`, `registry.json`, `ended.jsonl`, `selection.jsonl` | node stores row state, pinned/org registry, ended agents and selection history | owner UI actions / other node or seed tools; `store.ts:1-`; `server.ts:113-124` |
| `~/.local/state/agent-base/browser.json`, `browser-history.json` | node persists browser state and imported suggestions | app browser actions, import reads Chrome/Arc; `server.ts:125-127`; `browser-state.ts:1-`; `browser-import.ts:1-` |
| `~/.local/state/agent-base/hosts/`, `uploads/` | `siso-host` per-seat metadata; node receives image drops | host lifecycle / app composer; `server.ts:131-134` |
| `~/.local/state/agent-base/ship-queue/queue.jsonl`, `deploy.jsonl`, lock/pid | ab-queue events, landed/deploy receipts | `tools/ab-queue:34-37,227-248`; release reader `ship.ts:1-` |
| `~/.local/state/agent-base/live/` | ab-live deploy journal and rollback metadata | `tools/ab-live:18-24,114-` |
| `~/.local/state/context-ping/ctx/<session>.json` | node/HUD reads context gauge | context-ping writes it; `server.ts:106`; `Hud.tsx:1-` |
| `~/.local/state/herdr-resurrect/snapshot-*.json` | node reads historical pane identity during row migration | herdr-resurrect; `server.ts:117-124,370-` |
| `~/.claude/projects/**`, `~/.codex/sessions/**` | node reads chat transcripts, usage, tool calls and subagent links | Claude Code / Codex write live sessions; `transcript.ts:1-`; `codex-transcript.ts:1-`; `server.ts:802-` |
| `~/.claude/console/state/events.jsonl` | node reads pages posted by SISO Console for agent page strip | Console writes events; `server.ts:128-130`; `PageRow.tsx:1-` |
| `~/SISO_Workspace/SISO_Agents/siso-estate/plan/machines.json` | node reads machine identity map | estate source repo; `server.ts:110-112` |
| `~/SISO_Workspace/SISO_Agents/agent-zero/siso-firstmate/.agents/a0/tasks/` | Node reads A0 task index/files; `/api/a0/tell` writes task coordination through the A0 adapter | Firstmate task owner / A0 task tools; `a0-tasks.ts:26-`; `server.ts:69,1626-1659` |
| `~/SISO_Workspace/SISO_Agency/apps/siso-internal-labs/siso-internal-labs-agents/intent/ASKS.json` and `ASKS-STATUS.json`; review console data | Asks are read; review list comes from Console; opened status is written to configured review state | Internal Labs intent tooling / Console; `asks.ts:1-18`; `reviews.ts:1-50`; `server.ts:76-77,1662-1671` |
| Library / usage / token source files under `~/SISO_Workspace/Great_Library_of_SISO`, SISO agent stack and machine state | library, account tokens, spend and usage handlers read JSON/API caches | Great Library, token meter, and service report producers; `library.ts:1-`; `tokens.ts:1-`; `spend.ts:1-`; `usage.ts:1-` |
| WhatsApp / Life / Voice service state | node proxies configured upstreams or local voice service; voice history/settings/dictionary handlers | SISO services own their DB/files; `whatsapp.ts:27-70`; `life.ts:26-55`; `voice.ts:1-` |
| Browser source history / downloads | import reads local Chrome/Arc history; download routes read/reveal files | browsers and user downloads; `browser-import.ts:1-`; `browser-downloads.ts:1-` |

## 7. Known broken or half-built (observed evidence)

| Finding | Evidence and impact | Source |
|---|---|---|
| Docs is a dead rail item | App explicitly renders Docs with `later`; no click handler, mounted page, or Docs API. | `App.tsx:1170-1172` |
| Live `/api/tasks` disagrees with source router | Source handles `/api/tasks` at `server.ts:1682`; GET probe got **404**. Live service is not behaving like this `origin/main` router for this path. | `server.ts:1682-1688`; GET `127.0.0.1:5401/api/tasks` → 404 |
| Live desk digest route disagrees with source router | `GET /api/hub/zeros/desk-digest` is explicitly routed; probe got **404**. | `server.ts:1576-1580`; GET → 404 |
| Live optional proxies did not resolve | GET `/api/whatsapp` and `/api/life` returned 404; app gates their pages by configuration/feature flags, so those services are currently unavailable or unconfigured at this live endpoint. | `whatsapp.ts:27-70`; `life.ts:26-55`; GETs → 404 |
| Two agent inventories coexist | Main nav uses local herdr `/api/agents`, while hub dashboards query `/api/hub/agents` and `/api/hub/org`; stale/divergent sources can show different agents/org state. | `App.tsx:1-60`; `server.ts:1331-1336,1575-1600`; `hub.ts:1-` |
| SDK seat and terminal chat are parallel mechanisms | A hosted SDK chat uses host metadata/WS; ordinary chat mirrors transcript and sends into the terminal. Capabilities and delivery state can differ by seat type. | `server.ts:131-134,1900-1982`; `docs/SPEC.md:226-257` |

Live GET snapshot (status and byte counts only): `/api/health` 200/42; `/api/version` 200/390; `/api/scratchpad` 200/1758; `/api/org` 200/112248; `/api/tokens` 200/32279; `/api/servers` 200/7625; `/api/library` 200/101266; `/api/voice/status` 200/489; `/api/reviews` 200/112; `/api/asks` 200/47498; `/api/a0/tasks` 200/154722; `/api/hub/a0` 200/21422; `/api/hub/org` 200/9291; `/api/agents/no-such-agent/read` 200/86. No response bodies (which may contain private agent data) were printed. `/api/pages` 404 was an unregistered probe path, not a UI route.

## 8. Numbers

| Measure | Count / largest | Method |
|---|---|---|
| Reachable top-level app spaces | 10: Home/agents, Voice, Rolodex, Life, WhatsApp, Browser, Estate, Library, Servers, Tokens; Docs is disabled | `App.tsx:1169-1304` |
| App page routes in center | 5 app page ids (Tasks, Org chart, Stats, Starred, What’s new), plus agent pages, browser/terminal tabs, and nested pages above | `App.tsx:86-95,1630-` |
| Node API templates | 70+ across server and handler modules (literal, parameterized and wildcard paths; WS excluded) | `services/node/src/server.ts:1297-1855`; `services/node/src/dictation.ts:35-65` |
| Web component TS/TSX files | 100 | `apps/web/src/App.tsx:1-60`; component tree counted with `git ls-tree -r origin/main apps/web/src/components` |
| Test files | 297 (`.mjs/.js/.ts/.tsx` under test/tests directories) | `services/node/test/check.mjs:1-`; repo test tree counted with `git ls-tree -r origin/main` |
| Largest text files (lines) | `services/node/src/server.ts` 2370; `apps/web/src/App.tsx` 1897; `apps/web/src/components/ChatView.tsx` 1599; `apps/web/src/components/Sidebar.tsx` 1219; `apps/web/src/components/TokensSpace.tsx` 1203; `services/node/src/tokens.ts` 1107; `apps/web/preview/group-dashboard-v2.tsx` 1034; `services/host/src/host.ts` 938; `services/node/src/servers.ts` 788; `apps/web/src/components/ServersSpace.tsx` 768 | `server.ts:1`; `App.tsx:1`; `ChatView.tsx:1`; `Sidebar.tsx:1`; `TokensSpace.tsx:1`; `tokens.ts:1`; `group-dashboard-v2.tsx:1`; `host.ts:1`; `servers.ts:1`; `ServersSpace.tsx:1` (`origin/main` blob line counts) |
