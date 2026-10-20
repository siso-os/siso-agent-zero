import json
import io
from pathlib import Path
import runpy
import sqlite3
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
bridge = runpy.run_path(str(ROOT / "zero/bin/a0-sweep-mcp.py"))
fresh = runpy.run_path(str(ROOT / "harness/bin/seat-fresh-t3"))
Mcp = fresh["Mcp"]


class SweepAuthTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.args = SimpleNamespace(db=self.home / "statev2.sqlite", seats=self.home / "seats.json")
        (self.home / "server-runtime.json").write_text(json.dumps({"origin": "http://127.0.0.1:5490"}))
        self.cache = self.home / "seat-fresh-auth.json"
        fresh["atomic_json"](self.cache, {
            "origin": "http://127.0.0.1:5490", "token": "fixture", "expiresAt": time.time() + 3600})

    def test_cached_auth_401_renews_once(self):
        calls = []
        def rpc(client, method, *args, **kwargs):
            calls.append(method)
            if len(calls) == 1:
                client.session = "stale"
                raise ValueError("SISO Code /mcp returned HTTP 401")
        def authorize(client, userdata):
            self.assertIsNone(client.session)
            client.token = "renewed-fixture"
        with patch.object(Mcp, "rpc", rpc), patch.object(Mcp, "authorize", authorize):
            self.assertEqual(Mcp(self.args).token, "renewed-fixture")
        self.assertEqual(calls, ["initialize", "initialize", "notifications/initialized"])
        self.assertEqual(self.cache.stat().st_mode & 0o777, 0o600)

    def test_expiry_and_non401(self):
        value = json.loads(self.cache.read_text())
        value["expiresAt"] = 0
        fresh["atomic_json"](self.cache, value)
        with patch.object(Mcp, "rpc"), patch.object(Mcp, "authorize") as auth:
            Mcp(self.args)
            auth.assert_called_once_with(self.home)
        value["expiresAt"] = time.time() + 3600
        fresh["atomic_json"](self.cache, value)
        with patch.object(Mcp, "rpc", side_effect=ValueError("HTTP 503")), patch.object(Mcp, "authorize") as auth:
            with self.assertRaisesRegex(ValueError, "503"):
                Mcp(self.args)
            auth.assert_not_called()

    def test_loopback_and_cache_permissions(self):
        for origin in ("http://example.com", "http://user@127.0.0.1", "http://127.0.0.1/redirect"):
            (self.home / "server-runtime.json").write_text(json.dumps({"origin": origin}))
            with self.assertRaisesRegex(ValueError, "loopback"):
                Mcp(self.args)
        (self.home / "server-runtime.json").write_text(json.dumps({"origin": "http://127.0.0.1:5490"}))
        self.cache.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "600"):
            Mcp(self.args)

    def test_redirect_is_rejected_without_following(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer
        class Redirect(BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(302)
                self.send_header("Location", "http://example.com/should-never-be-called")
                self.end_headers()
            def log_message(self, *args):
                pass
        with HTTPServer(("127.0.0.1", 0), Redirect) as server:
            worker = threading.Thread(target=server.handle_request)
            worker.start()
            mcp = Mcp.__new__(Mcp)
            mcp.origin = f"http://127.0.0.1:{server.server_port}"
            with self.assertRaisesRegex(ValueError, "HTTP 302"):
                mcp.post("/mcp", {}, headers={"Authorization": "Bearer fixture"})
            worker.join(timeout=2)
            self.assertFalse(worker.is_alive())

    def test_bridge_uses_shared_client_and_archives_via_mcp(self):
        from unittest.mock import Mock
        mcp = Mock()
        mcp.call.return_value = {"accepted": True}
        requests = [
            {"id": "1", "tag": "orchestration.subscribeShell"},
            {"id": "2", "tag": "orchestration.dispatchCommand",
             "payload": {"type": "thread.archive", "threadId": "fixture"}},
            {"id": "3", "tag": "not-supported"},
        ]
        output = io.StringIO()
        with patch.dict(bridge["serve"].__globals__, {
            "client": lambda: mcp, "snapshot": lambda _: {"threads": []},
        }), patch("sys.stdin", io.StringIO("\n".join(map(json.dumps, requests)))), patch("sys.stdout", output):
            bridge["serve"]()
        replies = list(map(json.loads, output.getvalue().splitlines()))
        self.assertEqual(replies[0]["result"], {"threads": []})
        self.assertEqual(replies[1]["result"], {"accepted": True})
        self.assertIn("details withheld", replies[2]["error"])
        mcp.call.assert_called_once_with("t3_thread_organize", {"threadId": "fixture", "action": "archive"})

    def test_readonly_snapshot_keeps_busy_and_pinned_guards(self):
        with sqlite3.connect(self.args.db) as db:
            db.executescript("""
                create table projection_projects(project_id,title,deleted_at);
                create table orchestration_v2_projection_threads(payload_json,archived_at,deleted_at);
                create table orchestration_v2_projection_runs(thread_id,status,completed_at,payload_json,ordinal);
                create table orchestration_v2_projection_runtime_requests(thread_id,status);
                create table orchestration_v2_projection_provider_threads(thread_id,status,payload_json);
                create table orchestration_v2_projection_subagents(thread_id,status);
                create table orchestration_v2_projection_turn_items(thread_id,type,status);
            """)
            db.execute("insert into projection_projects values ('p','Fixture',null)")
            for tid in ("done", "queued", "request", "background", "subagent", "secret", "pinned"):
                db.execute("insert into orchestration_v2_projection_threads values (?,null,null)", (
                    json.dumps(dict(id=tid, projectId="p", pinnedAt="old" if tid == "pinned" else None,
                                    lineage={"parentThreadId": "seat", "relationshipToParent": "subagent"})),))
                db.execute("insert into orchestration_v2_projection_runs values (?,?,?,?,1)",
                           (tid, "queued" if tid == "queued" else "completed", "old", '{"startedAt":"older"}'))
            db.execute("insert into orchestration_v2_projection_runtime_requests values ('request','pending')")
            db.execute("""insert into orchestration_v2_projection_provider_threads values
                       ('background','idle','{"pendingBackgroundTasks":[{}]}')""")
            db.execute("insert into orchestration_v2_projection_subagents values ('subagent','running')")
            db.execute("insert into orchestration_v2_projection_turn_items values ('secret','secret_request','waiting')")
        original = self.args.db.read_bytes()
        rows = {t["id"]: t for t in bridge["snapshot"](self.args.db)["threads"]}
        self.assertEqual({t for t, row in rows.items() if row["status"] == "running"},
                         {"queued", "request", "background", "subagent", "secret"})
        self.assertEqual(rows["pinned"]["pinnedAt"], "old")
        self.assertEqual(self.args.db.read_bytes(), original)
        with patch("sqlite3.connect", wraps=sqlite3.connect) as connect:
            bridge["snapshot"](self.args.db)
            self.assertTrue(connect.call_args.args[0].endswith("?mode=ro"))


if __name__ == "__main__":
    unittest.main()
