"""Private pipe adapter: existing seat-fresh authentication, read-only sweep metadata."""
import json
import os
from pathlib import Path
import runpy
import sqlite3
import sys
from types import SimpleNamespace


FRESH = Path(__file__).resolve().parents[2] / "harness/bin/seat-fresh-t3"
HOME = Path.home()
DB = HOME / ".local/state/siso-code/userdata/statev2.sqlite"
ACTIVE = ("queued", "preparing", "starting", "running", "waiting", "pending")


def snapshot(db_path):
    # Never open the live database writable or load messages/private turn payloads.
    with sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5) as db:
        db.execute("BEGIN")
        projects = [dict(id=r[0], title=r[1]) for r in db.execute(
            "select project_id,title from projection_projects where deleted_at is null")]
        threads = [json.loads(r[0]) for r in db.execute(
            "select payload_json from orchestration_v2_projection_threads "
            "where archived_at is null and deleted_at is null")]
        busy = set()
        latest = {}
        for tid, status, completed, started in db.execute(
                "select thread_id,status,completed_at,json_extract(payload_json,'$.startedAt') "
                "from orchestration_v2_projection_runs order by ordinal"):
            latest[tid] = (status, completed, started)
            if status in ACTIVE:
                busy.add(tid)
        # Conservatively retain any outstanding provider work, including secret requests.
        for table, predicate in (
            ("runtime_requests", "status='pending'"),
            ("provider_threads", "status='active' or "
             "coalesce(json_array_length(payload_json,'$.pendingBackgroundTasks'),0)>0"),
            ("subagents", "status in ('pending','running','waiting')"),
            ("turn_items", "type in ('command_execution','dynamic_tool','subagent','secret_request') "
             "and status in ('pending','running','waiting')"),
        ):
            busy.update(r[0] for r in db.execute(
                f"select distinct thread_id from orchestration_v2_projection_{table} where {predicate}"))
        rows = []
        for thread in threads:
            tid = thread["id"]
            status, completed, started = latest.get(tid, ("idle", None, None))
            row = {k: thread.get(k) for k in (
                "id", "projectId", "title", "updatedAt", "archivedAt", "deletedAt", "pinnedAt", "lineage")}
            if row["lineage"] and not row["lineage"].get("parentThreadId"):
                row["lineage"] = None
            row.update(status="running" if tid in busy else status,
                       latestRunCompletedAt=completed, activityRunStartedAt=started)
            rows.append(row)
        return {"projects": projects, "threads": rows}


def client():
    # Import the implementation itself: expiry, private atomic cache and 401 renewal
    # stay owned by seat-fresh-t3. run_name prevents its seat-rotation entrypoint.
    fresh = runpy.run_path(str(FRESH), run_name="sweep_shared_auth")
    runtime = json.loads((DB.parent / "server-runtime.json").read_text())
    override = os.environ.get("A0_SWEEP_URL")
    if override and override.rstrip("/") != runtime["origin"].rstrip("/"):
        raise ValueError("Sweep URL must match the local SISO Code runtime.")
    return fresh["Mcp"](SimpleNamespace(
        db=DB, seats=HOME / ".local/state/agent-base/t3-seats.json"))


def serve():
    mcp = None
    for line in sys.stdin:
        request = json.loads(line)
        try:
            if mcp is None:
                mcp = client()
            if request["tag"] == "orchestration.subscribeShell":
                result = snapshot(DB)
            elif request["tag"] == "orchestration.dispatchCommand":
                payload = request["payload"]
                if payload["type"] != "thread.archive":
                    raise ValueError("Unsupported sweep command.")
                result = mcp.call("t3_thread_organize", {
                    "threadId": payload["threadId"], "action": "archive"})
            else:
                raise ValueError("Unsupported sweep request.")
            reply = {"id": request["id"], "result": result}
        except Exception:
            # No private data, bearer, CLI output or API response in launchd logs.
            reply = {"id": request["id"], "error": "Sweep MCP/read-only metadata request failed (details withheld)."}
        print(json.dumps(reply), flush=True)


if __name__ == "__main__":
    serve()
