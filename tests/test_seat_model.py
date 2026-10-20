"""seat list flags Opus on a seat the Opus chart does not list; the flag changes no state or exit code. Fixture; no network."""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
THREADS = [("mcp:e1", "ECOSYSTEM", "claude-opus-5-5"), ("mcp:o1", "OPERATOR", "claude-opus-5-5"),
           ("mcp:s1", "ESTATE", "claude-sonnet-5-5")]


class OpusChartTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="u085-seat-")
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name).resolve()
        self.seats = self.dir / "t3-seats.json"
        self.seats.write_text(json.dumps({name: {"thread": tid} for tid, name, _ in THREADS}))
        self.db = self.dir / "statev2.sqlite"
        con = sqlite3.connect(self.db)
        con.execute("create table orchestration_v2_projection_threads (thread_id text, title text, archived_at text,"
                    " deleted_at text, updated_at text, payload_json text)")
        for tid, title, model in THREADS:
            con.execute("insert into orchestration_v2_projection_threads values (?, ?, null, null, '2026-10-19', ?)",
                        (tid, title, json.dumps({"modelSelection": {"model": model}})))
        con.commit()
        con.close()

    def test_list_flags_only_opus_outside_the_chart(self):
        env = dict(os.environ, A0_SEATS_FILE=str(self.seats), A0_T3_DB=str(self.db),
                   A0_DISPATCH_FILE=str(self.dir / "dispatch.jsonl"))
        r = subprocess.run([sys.executable, str(ROOT / "bin/seat")], env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.count("! claude-opus-5-5: not on the Opus chart"), 1, r.stdout)  # ECOSYSTEM only
        self.assertIn("ECOSYSTEM", r.stdout)
        self.assertIn("3 seats, 0 not ok, 1 off the Opus chart", r.stdout)


if __name__ == "__main__":
    unittest.main()
