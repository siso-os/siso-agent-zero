#!/usr/bin/env bash
# new-team.sh — stand up a SISO project team: the folder, the manifest, the herdr space, the Agent Zero pane.
#
#   tools/new-team.sh <slug> --label "Name" --plane CODE [--host SSH_ALIAS] [--checkout /path/on/host]
#                     [--site URL] [--deploy /path/to/deploy.sh] [--into /companion/repo/team] [--code-repo /path]
#                     [--camofox-port N]   the team's own camofox on the host (systemd siso-camofox@<slug>, loopback)
#                     [--herdr] [--az-pane] [--retarget-notify]
#
#   <slug>            lowercase team id; also the camofox userId and the intent folder name
#   --into            put the team folder in the project's companion repo (the knowledge repo that is
#                     symlinked into its code repos as .agents/) instead of teams/<slug>/ here.
#                     A team folder never lives in a product repo.
#   --herdr           create the team's herdr workspace on --host (or here) and record its id
#   --az-pane         open the Project Agent Zero's pane in that space (a tab, cwd = checkout) and record it
#   --retarget-notify point az-notify on the host at that pane — a LIVE-FLEET change; only with Shaan's go
#
# Prints what it did. Does not start the Agent Zero session (do that with
# tools/spawn-worker --harness claude), does not commit, does not touch other teams' spaces.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
slug=""; label=""; plane=""; host=""; checkout=""; site=""; deploy=""; into=""; code_repo=""; camofox_port=""; do_herdr=0; do_pane=0; do_notify=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) label="$2"; shift 2;; --plane) plane="$2"; shift 2;; --host) host="$2"; shift 2;;
    --checkout) checkout="$2"; shift 2;; --site) site="$2"; shift 2;; --deploy) deploy="$2"; shift 2;;
    --into) into="$2"; shift 2;; --code-repo) code_repo="$2"; shift 2;; --camofox-port) camofox_port="$2"; shift 2;; --herdr) do_herdr=1; shift;; --az-pane) do_pane=1; shift;;
    --retarget-notify) do_notify=1; shift;; -h|--help) sed -n 2,16p "$0"; exit 0;;
    -*) echo "new-team.sh: unknown flag $1" >&2; exit 64;; *) slug="$1"; shift;;
  esac
done
[[ -n "$slug" && -n "$label" && -n "$plane" ]] || { echo 'usage: new-team.sh <slug> --label "Name" --plane CODE [...]' >&2; exit 64; }
slug="$(echo "$slug" | tr 'A-Z' 'a-z')"
T="${into:-$here/teams/$slug}"
[[ -e "$T/team.yaml" ]] && { echo "new-team.sh: $T/team.yaml exists — edit it, do not re-init" >&2; exit 1; }
mkdir -p "$T"/{intent,briefs,handoffs,workers}

hrun() { if [[ -n "$host" ]]; then ssh -o BatchMode=yes -o ConnectTimeout=8 "$host" "$(printf '%q ' herdr "$@")"; else herdr "$@"; fi; }
ws=""; pane=""
if [[ $do_herdr -eq 1 ]]; then
  res="$(hrun workspace create --cwd "${checkout:-/}" --label "Team: $slug" --no-focus)"
  ws="$(printf '%s' "$res" | python3 -c 'import sys,json; r=json.load(sys.stdin)["result"]; print(r["workspace"]["workspace_id"])')" \
    || { echo "new-team.sh: workspace create returned: ${res:0:200}" >&2; exit 1; }
  echo "==> herdr space $ws on ${host:-this machine}"
  if [[ $do_pane -eq 1 ]]; then
    res="$(hrun tab create --workspace "$ws" --cwd "${checkout:-/}" --label agent-zero --no-focus)"
    pane="$(printf '%s' "$res" | python3 -c 'import sys,json; r=json.load(sys.stdin)["result"]; print(r["root_pane"]["pane_id"])')" \
      || { echo "new-team.sh: tab create returned: ${res:0:200}" >&2; exit 1; }
    echo "==> Agent Zero pane $pane (empty shell; start him with tools/spawn-worker --harness claude)"
  fi
fi
if [[ -n "$camofox_port" ]]; then
  [[ -n "$host" ]] || { echo "new-team.sh: --camofox-port needs --host" >&2; exit 64; }
  scp -q "$here/ops/siso-camofox@.service" "$host:/etc/systemd/system/siso-camofox@.service"
  ssh "$host" "mkdir -p /etc/siso-camofox && printf 'CAMOFOX_PORT=%s\nPORT=%s\nCAMOFOX_BIND_HOST=127.0.0.1\n' $camofox_port $camofox_port > /etc/siso-camofox/$slug.env && systemctl daemon-reload && systemctl enable --now siso-camofox@$slug >/dev/null 2>&1 && sleep 5 && curl -s -m 10 http://127.0.0.1:$camofox_port/health | head -c 80 && echo && echo '==> camofox for $slug on 127.0.0.1:$camofox_port (needs /opt/camofox-browser with its binary fetched)'"
fi
if [[ $do_notify -eq 1 ]]; then
  [[ -n "$pane" && -n "$host" ]] || { echo "new-team.sh: --retarget-notify needs --host, --herdr and --az-pane" >&2; exit 64; }
  ssh "$host" "f=\$(command -v az-notify || echo /home/siso/bin/az-notify); cp -a \$f \$f.bak-\$(date +%Y%m%d%H%M) && sed -i 's|^PANE=.*|PANE=$pane   # project Agent Zero — $slug|' \$f && echo \"==> az-notify on $host now targets $pane (backup beside it)\""
fi

cat > "$T/team.yaml" <<YAML
# team.yaml — the manifest of one SISO project team. Schema and reference instance: the root team.yaml.
template: {repo: sisodias/siso-project-team, version: v$(cat "$here/VERSION")}   # tools/team-upgrade shows what changed since
team: $slug
label: $label
human: shaan
created: $(date +%F)

project:
  repo: TODO                                   # the product repo(s) being built
  checkout: ${checkout:-TODO}                  # ONE shared clone on the host; the git index is shared
  site: ${site:-TODO}
  docs: TODO                                   # everything the human reads, with a picture
  deploy_script: ${deploy:-TODO}               # the ONLY thing that moves pointers
  companion_repo: ${into:+$into}${into:-"(this repo: teams/$slug)"}   # where this folder lives; symlinked into code repos as .agents/

host:
  name: ${host:-laptop}
  ssh: ${host:-""}
  agents_run_as: siso

herdr:
  space: ${ws:-null}                           # the team's workspace on the host
  agent_zero_pane: ${pane:-null}
  send: tools/az-send                          # never raw pane send-text/send-keys

# Where this team's agents actually run. herdr is the safe default: it needs nothing but a
# herdr server. Switch to orca on a host where orcad runs and the team shows up on the Agents
# tab with live status — fill the block below from orca repo list --json and
# ~siso/.orca/orca-runtime.json, then flip substrate. See skills/project-agent-zero.
substrate: herdr

orca:
  runtime: null                                # ws://127.0.0.1:7777
  repo_id: null                                # orca repo list --json
  worktree: null                               # branch:<the shared branch> — not a per-owner lane
  cli: node /opt/orca-eval/orca/out/cli/index.js
  runs_as: siso

tasks:
  system: plane
  workspace: siso-crm
  project: $plane                              # Plane project code; every brief cites Plane: $plane-nn
  base_url_on_host: http://127.0.0.1:80

agent_zero:
  harness: claude                              # Opus on Claude Code
  skill: skills/project-agent-zero
  charter: AGENT-ZERO.md
  compact_prompt: skills/project-agent-zero/COMPACT.md
  briefs_dir: briefs
  handoffs_dir: handoffs
  intent: intent/                              # one verbatim file per message; index.html newest first
  intent_log: shaan-intent-log.json            # flat, oldest first; tools/intent-capture writes both
  reports_to_human_via: console
  reports_to_personal_agent_zero: DIGEST.md    # one dated line per material change; tier 0 reads only this

owners:
  model: opus
  harness: claude
  lifecycle: ephemeral                         # brief → browser-checkable done → handoff → exit
  context_budget_tokens: 60000
  skill: skills/owner
  spawn: tools/spawn-worker --harness claude
  live_today: []

arms:
  contract: skills/worker-contract
  spawn: tools/spawn-worker --harness codex    # herdr starts them in this space; they message back with az-send
  pools:
    - {name: qwen, model: siso-kaggle-worker/qwen3.8-27b, harness: codex, codex_provider: siso-pool, config: codex/config.pool.toml}
    - {name: luna, model: gpt-5.6-luna, harness: codex, codex_profile: SISO}
  fallback: the owner does it or uses its own built-in sub-agents, and says which in the handoff

browser:
  tool: tools/siso-browse
  camofox: {port: ${camofox_port:-null}, userId: $slug}   # one instance per team (siso-camofox@$slug); sessions never cross teams
  login: TODO                                  # the team's verifier account env file; never the human's cookie
  storage_state: TODO

verify:                                                      # from Oracle: one gate, a ratchet, one human gate
  command: TODO                                              # the one command that judges a landing (JSON per layer, exit 0/1/2, PARTIAL 3)
  baseline: TODO                                             # committed red baseline from a clean main; the gate refuses NEW red only
  sensitive_paths: [credentials, tokens, deploy scripts, schema, wipe paths]   # the only diffs that get a cold review
  human_gate: HUMAN-GATE.md                                  # the public live window and anything else only Shaan touches

trunk:
  max_live_lanes: 3                                          # owners' worktrees; refuse a 4th
  worktree_root: .worktrees                                  # under the code repo; gitignored
  delete_on_merge: true                                      # Agent Zero removes the lane when the handoff lands

front_end: https://siso-project-team.pages.dev/

human_only: [credentials, money, production data]
YAML

cat > "$T/AGENT-ZERO.md" <<MD
# $label — Project Agent Zero

You are the Agent Zero of **$label** (team \`$slug\`, Plane project \`$plane\`). Read the
\`project-agent-zero\` skill first — it is your front door. Then \`team.yaml\` beside this file,
\`intent/index.html\` (newest first), \`handoffs/\`, and \`plane tasks $plane\`.

## This team's specifics
- Checkout: \`${checkout:-TODO}\` on \`${host:-laptop}\` · herdr space \`${ws:-TODO}\` · your pane \`${pane:-TODO}\`
- Estate skill: TODO — the skill that carries this project's deploys, traps and machines

## Domains (one owner each, ephemeral)
| Domain | What "done" looks like in a browser | Owner pane | State |
|---|---|---|---|

## Decisions log (newest first)
MD
cat > "$T/OWNERS.md" <<MD
# Owners — $label (replace rows; keep under 40 lines)

| surface | seat (pane) | lane / branch | last landed |
|---|---|---|---|
MD
printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Decision log — %s</title></head><body><h1>Decision log — %s</h1><p>One entry per decision or trap: date · what · why · what it replaced. Newest first. Never a per-unit receipt.</p><ul></ul></body></html>\n' "$label" "$label" > "$T/DECISION-LOG.html"
printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Proven ledger — %s</title></head><body><h1>Proven ledger — %s</h1><p>One row per claim that was proven: date · claim · receipt (URL, screenshot path, release id). A claim without a receipt is not here.</p><table><tr><th>date</th><th>claim</th><th>receipt</th></tr></table></body></html>\n' "$label" "$label" > "$T/PROVEN-LEDGER.html"
printf '# Human gate — %s\n\nThe only things that wait for Shaan: credentials, money, production data, and the public live window named here. Everything else the team decides.\n\n- public live window: TODO\n' "$label" > "$T/HUMAN-GATE.md"
if [[ -n "${code_repo:-}" && -d "$code_repo/.git" ]]; then
  ln -sfn "$T" "$code_repo/.agents"; grep -qx '.agents' "$code_repo/.git/info/exclude" 2>/dev/null || echo '.agents' >> "$code_repo/.git/info/exclude"
  [[ -f "$code_repo/AGENTS.md" ]] || printf '# %s — code repo\n\nProcess, state and briefs live in .agents/ (the companion repo). Build/test/verify commands: TODO. Keep this file under 120 lines.\n' "$label" > "$code_repo/AGENTS.md"
  echo "==> code repo wired: $code_repo/.agents -> $T (gitignored via .git/info/exclude)"
fi
printf '# Digest for the personal Agent Zero — %s\n\nOne dated line per material change: what moved, what was verified, what needs Shaan.\n' "$label" > "$T/DIGEST.md"
printf '# Workers of %s\n\nYou are an arm of this team. Before anything: read the `worker-contract` skill\n(`skills/worker-contract/SKILL.md` in sisodias/siso-project-team). One brief, one result, one message back, then stop.\n' "$label" > "$T/workers/AGENTS.md"
echo "==> created $T (plane=$plane space=${ws:-none} az_pane=${pane:-none})"
echo "next: fill the TODOs in team.yaml and AGENT-ZERO.md; capture intent with tools/intent-capture --team $slug <transcripts>; start the brain with tools/spawn-worker --harness claude --workspace ${ws:-<space>}"
