"""seat and a0-dispatch-hook read a seat's thread on its runsOn machine (mini) with ssh. Fake ssh; no network."""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
THREAD = "mcp:0a92d515-c413-4d89-8b94-e17b44fd15e3"
ROW = [{"title": "AGENT-BASE", "archived_at": None, "deleted_at": None, "updated_at": "2026-10-17T10:00:00",
        "payload_json": "{}"}]
FAKE_SSH = """#!/bin/sh
echo "$@" >> "$FAKE_SSH_LOG"
if [ -n "$FAKE_SSH_DOWN" ]; then echo "ssh: connect to host mini-fast port 22: Operation timed out" >&2; exit 255; fi
printf '%s' "$FAKE_SSH_ROW"
"""


class RemoteSeatTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="u011-seat-")
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name).resolve()
        (self.dir / "bin").mkdir()
        ssh = self.dir / "bin" / "ssh"
        ssh.write_text(FAKE_SSH)
        ssh.chmod(0o755)
        self.log = self.dir / "ssh.log"
        self.seats = self.dir / "t3-seats.json"
        self.seats.write_text(json.dumps({"AGENT-BASE": {"thread": THREAD, "runsOn": "mini"}}))
        self.db = self.dir / "statev2.sqlite"
        con = sqlite3.connect(self.db)
        con.execute("create table orchestration_v2_projection_threads (thread_id text, title text, archived_at text,"
                    " deleted_at text, updated_at text, payload_json text)")
        con.commit()
        con.close()

    def env(self, down=False):
        e = dict(os.environ, PATH=f"{self.dir / 'bin'}:{os.environ['PATH']}", A0_SEATS_FILE=str(self.seats),
                 A0_T3_DB=str(self.db), A0_DISPATCH_FILE=str(self.dir / "dispatch.jsonl"),
                 FAKE_SSH_LOG=str(self.log), FAKE_SSH_ROW=json.dumps(ROW))
        if down:
            e["FAKE_SSH_DOWN"] = "1"
        return e

    def run_seat(self, *args, down=False):
        return subprocess.run([sys.executable, str(ROOT / "bin/seat"), *args], env=self.env(down),
                              capture_output=True, text=True, timeout=60)

    def test_list_reads_mini_seat_over_ssh(self):
        r = self.run_seat()
        self.assertIn("ok         AGENT-BASE", r.stdout, r.stdout + r.stderr)
        argv = self.log.read_text()
        self.assertIn("mini-fast", argv)
        self.assertIn("RemoteCommand=none", argv)
        self.assertIn("RequestTTY=no", argv)
        self.assertIn("statev2.sqlite", argv)
        self.assertIn("-readonly", argv)  # sqlite3 is run read-only on the mini

    def test_ssh_failure_is_unreachable_not_missing(self):
        r = self.run_seat("list", down=True)
        self.assertIn("unreachable (mini)", r.stdout)
        self.assertNotIn("missing", r.stdout)
        w = self.run_seat("which", "AGENT-BASE", down=True)
        self.assertEqual(w.returncode, 1)
        self.assertIn("unreachable (mini)", w.stdout)

    def test_dispatch_hook_does_not_refuse_send_to_mini_seat(self):
        payload = {"hook_event_name": "PreToolUse", "tool_name": "mcp__t3__t3_thread_send",
                   "tool_input": {"threadId": THREAD, "message": "x"}}
        r = subprocess.run([sys.executable, str(ROOT / "bin/a0-dispatch-hook")], input=json.dumps(payload),
                           env=self.env(), capture_output=True, text=True, timeout=60)
        self.assertNotIn('"deny"', r.stdout, r.stdout + r.stderr)
        self.assertIn("runs on another machine", r.stdout)


if __name__ == "__main__":
    unittest.main()
