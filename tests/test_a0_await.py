"""a0-await: a seat that ends on a promise is still working, not done."""
import json
import runpy
import tempfile
import unittest
from pathlib import Path

AWAIT = Path(__file__).resolve().parents[1] / "bin" / "a0-await"


class AwaitWaitingTests(unittest.TestCase):
    def test_promise_to_fix_and_ship_is_waiting(self):
        ns = runpy.run_path(str(AWAIT), run_name="a0_await")
        self.assertIsNotNone(ns["WAITING"].search("I'll fix them worst first and ship each one."))


class AwaitParkedTests(unittest.TestCase):
    def test_promise_with_no_background_job_is_parked_not_done(self):
        ns = runpy.run_path(str(AWAIT), run_name="a0_await")
        ns["pending_children"] = lambda thread: 0
        ns["queued_runs"] = lambda thread: 0
        row = lambda said: {"status": "completed", "thread": "t", "said": said}
        self.assertTrue(ns["parked"](row("Parse failed. I'll fix it and run again.")))
        self.assertFalse(ns["parked"](row("I'll wait for the build running in background.")))
        self.assertFalse(ns["parked"](row("STATUS: done\nI'll fix nothing; merged.")))


class AwaitReportTests(unittest.TestCase):
    def setUp(self):
        self.ns = runpy.run_path(str(AWAIT), run_name="a0_await")

    def test_setup_links_and_passwords_are_redacted(self):
        out = self.ns["redact"]("Live at https://x.test/setup/abc123 and password: hunter2xyz")
        self.assertEqual(out, "Live at https://x.test/setup/<redacted> and password: <redacted>")

    def test_a_report_is_over_600_characters_or_a_link(self):
        self.assertFalse(self.ns["real_report"]("Merged."))
        self.assertTrue(self.ns["real_report"]("Merged. " + "x" * 600))
        self.assertTrue(self.ns["real_report"]("Live: https://example.com"))

    def test_short_turn_waits_out_quiet_minutes_and_queued_or_unknown_is_not_done(self):
        g = self.ns["done"].__globals__
        g["pending_children"] = g["queued_runs"] = lambda thread: 0
        short = {"status": "completed", "thread": "t", "said_full": "Merged.", "activity": "0m"}
        self.assertFalse(self.ns["done"](short, 12))
        self.assertTrue(self.ns["done"]({**short, "activity": "13m"}, 12))
        self.assertTrue(self.ns["done"]({**short, "said_full": "x" * 700}, 12))
        self.assertFalse(self.ns["done"]({**short, "said_full": "x" * 700, "status": "running"}, 12))
        g["queued_runs"] = lambda thread: 1
        self.assertFalse(self.ns["done"]({**short, "said_full": "x" * 700}, 12))
        g["pending_children"] = lambda thread: None
        self.assertFalse(self.ns["done"]({**short, "said_full": "x" * 700}, 12))

    def test_out_seat_is_sent_and_not_closed(self):
        g = self.ns["out_seats"].__globals__
        with tempfile.TemporaryDirectory() as d:
            log, closed = Path(d, "dispatch.jsonl"), Path(d, "closed.jsonl")
            log.write_text(json.dumps({"at": "2026-10-19T20:00:00", "name": "ESTATE"}) + "\n"
                           + json.dumps({"at": "2026-10-19T21:00:00", "name": "OPERATOR"}) + "\n")
            closed.write_text(json.dumps({"name": "OPERATOR", "at": "2026-10-19T21:30+07:00", "why": "done"}) + "\n")
            g["LOG"], g["CLOSED"] = str(log), str(closed)
            self.assertEqual(self.ns["out_seats"](["ESTATE", "OPERATOR", "HALO"]), ["ESTATE"])


class AwaitStuckTests(unittest.TestCase):
    def setUp(self):
        self.ns = runpy.run_path(str(AWAIT), run_name="a0_await")

    def test_live_run_fleet_check_flags_stuck_is_stuck_unless_a_child_is_live(self):
        g = self.ns["stuck"].__globals__
        hung = {"status": "running", "thread": "t", "activity": "2h45",
                "problems": ["STUCK run 4 running 3h ago, nothing for 165 min"]}
        g["pending_children"] = lambda thread: 0
        self.assertTrue(self.ns["stuck"](hung))
        self.assertEqual(self.ns["quiet_min"](hung["activity"]), 165)
        self.assertFalse(self.ns["stuck"]({**hung, "problems": []}))
        self.assertFalse(self.ns["stuck"]({**hung, "problems": ["QUEUED 1 message(s)"]}))
        g["pending_children"] = lambda thread: 1
        self.assertFalse(self.ns["stuck"](hung))


if __name__ == "__main__":
    unittest.main()
