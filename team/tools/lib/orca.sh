#!/usr/bin/env bash
# tools/lib/orca.sh — the one place that knows how to talk to Orca.
# Sourced by az-send, spawn-worker and fleet-status. Nothing here writes state; callers decide.
#
# WHY THIS EXISTS. herdr's `pane send-text` types without submitting, and a later bare
# `send-keys Enter` on text already at the prompt does NOT submit — the pane re-renders it and
# it looks sent. Ten dispatches were lost that way on 2026-09-11 and az-send had to guess from
# the rendered line. Orca closes the hole in the protocol instead of by heuristic:
# `terminal send --enter --wait-submit <s>` returns a durable receipt whose `stages` separate
# INPUT ACCEPTED from TURN STARTED — "it was typed" and "the agent read it" are two different
# answers, and only the second one counts. See orca_send.

ORCA_NODE_ENTRY_DEFAULT=/opt/orca-eval/orca/out/cli/index.js
orca_cli() {
  if [[ -n "${ORCA_CLI:-}" ]]; then eval "$ORCA_CLI" "$(printf '%q ' "$@")"; return $?; fi
  if command -v orca >/dev/null 2>&1; then command orca "$@"; return $?; fi
  HOME="${ORCA_HOME:-$HOME}" node "${ORCA_NODE_ENTRY:-$ORCA_NODE_ENTRY_DEFAULT}" "$@"
}
orca_available() { orca_cli terminal list --json >/dev/null 2>&1; }

# ---- targets -------------------------------------------------------------------------
# A target is `term_<uuid>`, `orca:<handle>`, or `orca:<title>` — the terminal's title OR its
# tab's, case-insensitive, and it must match exactly one.
orca_is_target() { case "${1:-}" in term_*|orca:*) return 0;; *) return 1;; esac; }

orca_resolve_handle() {
  local ref="${1:-}" want
  case "$ref" in
    term_*) printf '%s' "$ref"; return 0;;
    orca:term_*) printf '%s' "${ref#orca:}"; return 0;;
    orca:*) want="${ref#orca:}";;
    *) printf '%s' "$ref"; return 0;;
  esac
  orca_cli terminal list --include-visual-layouts --json 2>/dev/null | python3 -c '
import json, sys
want = sys.argv[1].strip().lower()
try: r = json.load(sys.stdin)["result"]
except Exception: sys.exit(3)

# A tab holds a TREE of panes (a single {"type":"terminal"} node, or splits), not a list.
def leaves(node, out):
    if not isinstance(node, dict): return
    if node.get("type") == "terminal":
        out.append(node); return
    for key in ("tabs", "children", "panes"):
        v = node.get(key)
        if isinstance(v, list):
            for c in v: leaves(c, out)
        elif isinstance(v, dict):
            leaves(v, out)

tabname = {}
for wt in r.get("visualLayouts") or []:
    for tab in ((wt.get("root") or {}).get("tabs") or []):
        got = []; leaves(tab.get("panes"), got)
        for pane in got:
            tabname[pane.get("handle")] = tab.get("title") or ""

# The TAB title is the stable one --title sets. The TERMINAL title is whatever the pty writes:
# Claude Code overwrites it with a summary of its own conversation minutes after it starts, so a
# lookup that trusted it would stop finding the agent it just spawned.
hits = []
for t in r.get("terminals") or []:
    for n in (tabname.get(t.get("handle")), t.get("title")):
        if not n: continue
        s = n.strip().lower()
        g = s.lstrip("\u2733\u25d0\u25d1\u25cf\u2726\u2736\u00b7 ").strip()
        if want == s or want == g:
            hits.append(t["handle"]); break
if len(hits) == 1: print(hits[0])
elif not hits: sys.exit(4)
else:
    sys.stderr.write("orca: title %r matches %d terminals: %s\n" % (want, len(hits), " ".join(hits))); sys.exit(5)
' "$want"
}

# ---- reading -------------------------------------------------------------------------
# --screen is the RENDERED frame. The default stream read stacks every repaint fragment, so a
# TUI comes back as `cclclecleaclear`; never judge a prompt from it.
orca_read() {
  local h="$1" n="${2:-40}"
  orca_cli terminal read --terminal "$h" --screen --json 2>/dev/null | python3 -c '
import json,sys
try: t=json.load(sys.stdin)["result"]["terminal"]
except Exception: sys.exit(1)
print("\n".join((t.get("tail") or [])[-int(sys.argv[1]):]))' "$n"
}

# ---- sending -------------------------------------------------------------------------
# orca_send <handle> <message> [wait-seconds]
#   0 SUBMITTED      an agent provider observed turn_started — the agent has it.
#   0 queued         no turn start was observed, but the agent is plainly mid-turn and nothing is
#                    stranded at its prompt. Claude Code queues input during a turn and reads it
#                    when the turn ends; this is the herdr contract too ("queued behind its turn").
#   0 unproven       the provider cannot observe delivery (a plain shell, or an old host);
#                    input WAS accepted and nothing is stranded at the prompt.
#   2 NOT-SUBMITTED  no turn start AND the agent is idle with text sitting at its prompt, or no
#                    evidence of either — the Enter was swallowed. Do NOT resend: reissue the exact
#                    command with --retry-request <id>, which replays the receipt rather than
#                    delivering the prompt twice.
#   1 unreachable / rejected.
#
# WHY THE BUSY CHECK EXISTS. "No turn start within N seconds" is not the same claim as "the agent
# does not have it", and the first version of this function conflated them. Measured 2026-09-12
# against a live owner blocked on a 5m30s bash call: the send reported exit 2, and the message had
# in fact been queued, read and acted on. Orca cannot tell a swallowed Enter from a message waiting
# behind a long tool call inside the wait window — so we look at the screen before we call it.
orca_send() {
  local h="$1" msg="$2" wait="${3:-25}" out rc
  out="$(orca_cli terminal send --terminal "$h" --text "$msg" --enter --wait-submit "$wait" --json 2>&1)"
  printf '%s' "$out" | python3 -c '
import json,sys
raw=sys.stdin.read()
try: d=json.loads(raw)
except Exception:
    sys.stderr.write("orca_send: unparseable reply: %s\n" % raw[:300].replace("\n"," ")); sys.exit(1)
if not d.get("ok"):
    sys.stderr.write("orca_send: %s\n" % raw[:300].replace("\n"," ")); sys.exit(1)
s=d["result"]["send"]
if not s.get("accepted"):
    sys.stderr.write("orca_send: input NOT accepted on %s\n" % s.get("handle")); sys.exit(1)
p=s.get("prompt") or {}
stages=p.get("stages") or []; prov=p.get("provider"); obs=p.get("observation"); rid=p.get("requestId")
h=s["handle"]
if prov not in ("unsupported","old-host"):
    if "turn_started" in stages:
        print("SUBMITTED %s (%s: %s)" % (h, prov, " -> ".join(stages))); sys.exit(0)
    if obs == "permission":
        sys.stderr.write("NOT-SUBMITTED %s: the provider is waiting on a permission prompt. Resolve it in the terminal, then reissue with --retry-request %s.\n" % (h, rid)); sys.exit(2)
    if obs == "incarnation_replaced":
        sys.stderr.write("NOT-SUBMITTED %s: the terminal process was replaced. Inspect it; do NOT retry this request id.\n" % h); sys.exit(2)
    # undetermined: the caller looks at the screen before deciding. rid is printed so the caller
    # can hand the operator the only safe retry.
    sys.stderr.write("no turn start within %ss on %s (retry-request %s)\n" % (sys.argv[1], h, rid)); sys.exit(4)
print("unproven %s (provider %s cannot report delivery; input was accepted)" % (h, prov)); sys.exit(3)
' "$wait"
  rc=$?
  case $rc in
    0) return 0;;
    2) return 2;;
    4) sleep 2   # no turn start observed: ask the screen which of the two things happened
       local screen; screen="$(orca_read "$h" 12)"
       if printf '%s\n' "$screen" | grep -qE '^❯ .{3,}'; then
         echo "orca_send: NOT SUBMITTED on $h — text is sitting at an idle prompt." >&2; return 2
       fi
       if printf '%s\n' "$screen" | grep -qE '\([0-9]+[ms] ?[0-9]*s? · |Running…|esc to interrupt'; then
         echo "submitted $h (queued behind its running turn; no new turn start to observe yet)"; return 0
       fi
       echo "orca_send: NOT SUBMITTED on $h — no turn start and no sign of a running turn. Read the terminal; reissue with --retry-request rather than resending." >&2
       return 2;;
    3) sleep 2   # provider cannot observe: fall back to the herdr-era heuristic, on the RENDERED screen
       if orca_read "$h" 8 | grep -qE '^❯ .{3,}'; then
         echo "orca_send: STRANDED on $h — text still sitting at the prompt." >&2; return 2
       fi
       echo "submitted $h (unproven: this provider cannot report delivery; nothing stranded at the prompt)"
       return 0;;
    *) return 1;;
  esac
}
