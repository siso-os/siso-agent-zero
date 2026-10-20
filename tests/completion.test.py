"""Completion regressions; fixtures and host replies never reach a real agent.

Uses an owned temporary directory unless A0_COMPLETION_FIXTURE_ROOT is supplied.
"""
import datetime
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
_fixture_home = None if os.environ.get('A0_COMPLETION_FIXTURE_ROOT') else tempfile.TemporaryDirectory(prefix='a0-completion-')
FIXTURES = Path(os.environ.get('A0_COMPLETION_FIXTURE_ROOT') or _fixture_home.name).resolve()


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = FIXTURES / self._testMethodName
        self.fixture.mkdir()
        self.look = runpy.run_path(str(ROOT / "bin/look"))
        self.look["jobs"].__globals__["H"] = str(self.fixture)
        self.now = time.time()

    def run_record(self, name, started, suffix=""):
        runs = self.fixture / ".local/state/codex-run/runs"
        runs.mkdir(parents=True, exist_ok=True)
        (runs / f"{name}{suffix}.meta.json").write_text(json.dumps({
            "name": name, "started": started, "pid": os.getpid(),
        }))

    def closures(self, records):
        state = self.fixture / ".local/state/a0"
        state.mkdir(parents=True)
        (state / "closed.jsonl").write_text("\n".join(json.dumps(r) for r in records) + "\ninvalid json\n")

    def iso(self, seconds):
        return datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc).isoformat()

    def test_mixed_closures_keep_latest_and_show_new_run(self):
        self.run_record("closed", self.now - 100)
        self.run_record("resent", self.now - 200, "-old")
        self.run_record("resent", self.iso(self.now - 10), "-new")
        self.closures([
            {"name": "closed", "at": self.now - 20},
            {"name": "closed", "at": self.iso(self.now - 30)},
            {"name": "closed", "at": self.now - 150},
            {"name": "resent", "at": self.iso(self.now - 50).replace("+00:00", "Z")},
        ])
        rows = self.look["jobs"]()
        self.assertEqual(len(rows), 1)
        self.assertIn("resent · running", rows[0])

    def test_invalid_closures_do_not_hide_work_or_crash(self):
        invalid = [None, True, [], {}, "bad", "NaN", "Infinity", 10**100, "2026-99-99"]
        self.run_record("visible", self.now - 60)
        self.closures([{"name": "visible", "at": v} for v in invalid] + [[], None, {}, {"name": [], "at": self.now}])
        self.assertIn("visible · running", self.look["jobs"]()[0])

    def test_supported_timestamps_and_invalid_run_records(self):
        stamp = self.look["timestamp"]
        for value in [self.now, str(self.now), self.iso(self.now), self.iso(self.now).replace("+00:00", "Z")]:
            self.assertAlmostEqual(stamp(value), self.now, places=5)
        offset = datetime.datetime.fromtimestamp(self.now, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
        self.assertAlmostEqual(stamp(offset), self.now, places=5)
        for i, value in enumerate([None, True, "bad", [], "NaN", 10**100]):
            self.run_record(f"invalid-{i}", value)
        self.assertEqual(self.look["jobs"](), ["nothing out"])

    def test_equal_timestamp_still_shows_run(self):
        self.run_record("equal", self.now)
        self.closures([{"name": "equal", "at": self.now}])
        self.assertIn("equal · running", self.look["jobs"]()[0])

    def own(self, replies, expected):
        # Use the complete production controller and parser. Only substitute its
        # host executable, with a local fixture that returns deterministic replies.
        bindir = self.fixture / "bin"
        roles = self.fixture / "roles"
        bindir.mkdir()
        roles.mkdir()
        source = (ROOT / "bin/role").read_text()
        host_line = 'AB="$HOME/SISO_Workspace/SISO_Agency/apps/siso-internal-labs/siso-internal-labs-agent-base/services/host/bin/siso-host-service"'
        self.assertEqual(source.count(host_line), 1)
        controller = bindir / "role"
        controller.write_text(source.replace(host_line, 'AB="$Z/mock-host"'))
        controller.chmod(0o755)
        (roles / "health.md").write_text("Fixture role only\n")
        for i, reply in enumerate(replies, 1):
            (self.fixture / f"reply-{i}").write_text(reply)
        host = self.fixture / "mock-host"
        host.write_text('''#!/bin/sh
set -eu
fixture=$(dirname "$0")
count=0
[ ! -f "$fixture/count" ] || count=$(cat "$fixture/count")
count=$((count+1))
printf '%s\n' "$count" > "$fixture/count"
cat "$fixture/reply-$count"
''')
        host.chmod(0o755)
        (self.fixture / '.local/state/a0').mkdir(parents=True)
        env = dict(os.environ, HOME=str(self.fixture), A0_ROLE_STATE=str(roles))
        result = subprocess.run([str(controller), "own", "health", "4"], capture_output=True, text=True, timeout=20, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"health: {expected} runs")
        self.assertEqual(int((self.fixture / "count").read_text()), expected)
        ledger = [json.loads(line) for line in (roles / "health.jsonl").read_text().splitlines()]
        self.assertEqual(len(ledger), expected)
        return ledger

    def test_blocked_with_document_changes_stops_after_one(self):
        ledger = self.own(["STATUS: blocked — waiting for authority\nNUMBER: retries 4 -> 4\nCHANGED: PLAN.md, HANDOFF.md, measurements.json\n"], 1)
        self.assertTrue(ledger[-1]["status"].startswith("blocked"))
        self.assertIn("PLAN.md", ledger[-1]["changed"])

    def test_successful_changes_reach_limit_even_if_changed_mentions_blocked(self):
        self.own(["STATUS: done\nNUMBER: fixes 0 -> 1\nCHANGED: blocked-handling.py\n"] * 4, 4)

    def test_no_changes_stop_after_two(self):
        self.own(["STATUS: done\nNUMBER: fixes 0 -> 0\nCHANGED: nothing\n"] * 2, 2)

    def test_missing_changes_stop_after_two(self):
        self.own(["STATUS: done\nNUMBER: fixes 0 -> 0\n"] * 2, 2)

    def test_progress_resets_no_change_streak_then_blocked_stops(self):
        self.own([
            "STATUS: done\nCHANGED: nothing\n",
            "STATUS: done\nCHANGED: source.py\n",
            "STATUS: done\nCHANGED: no processes stopped\n",
            "STATUS: BLOCKED — external dependency\nCHANGED: PLAN.md\n",
        ], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
