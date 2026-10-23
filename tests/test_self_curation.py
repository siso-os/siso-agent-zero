"""Staleness is advisory; checkpoints preserve history and never read reasoning."""
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import a0_self as s


class SelfCuration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        agent_home = patch.object(s, "resolve_agent_home", return_value=self.root / ".agents/agents/agent-zero")
        agent_home.start()
        self.addCleanup(agent_home.stop)
        (self.root / ".agents/agents/agent-zero/memory").mkdir(parents=True)
        self.now = dt.datetime(2026, 10, 21, 12, tzinfo=dt.timezone.utc)
        self.handoff = self.root / ".agents/agents/agent-zero/HANDOFF.md"
        self.handoff.write_text("# A0 checkpoint 2026-10-21T11:00:00+00:00\n\nprevious entry\n")
        (self.root / "AGENTS.md").write_text("## Now (21 Oct 2026)\n")
        self.summary = dict(decisions=["Kept the release hold pending proof."], spawns=["Builder x is blocked."], lessons=["Check the selected state home."])

    def test_stale_top_uses_timestamp_not_file_mtime(self):
        self.handoff.write_text("# A0 checkpoint 2026-10-19T11:00:00+00:00\n")
        self.assertTrue(any("24 h" in x for x in s.warnings(self.root, self.root, self.now)))

    def test_line_limit_and_missing_now_are_warnings(self):
        (self.root / "AGENTS.md").write_text("old\n" * 151)
        out = s.warnings(self.root, self.root, self.now)
        self.assertTrue(any("150" in x for x in out))
        self.assertTrue(any("Now" in x for x in out))

    def test_checkpoint_preserves_history_and_deduplicates(self):
        old = self.handoff.read_text()
        self.assertTrue(s.append_checkpoint(self.root, self.summary, "a0-self:fixture", self.now))
        self.assertTrue(self.handoff.read_text().endswith(old))
        self.assertFalse(s.append_checkpoint(self.root, self.summary, "a0-self:fixture", self.now))
        self.assertIn("Check the selected", (self.root / ".agents/agents/agent-zero/memory/2026-10-21.md").read_text())
        self.assertIn("2026-10-21.md", (self.root / ".agents/agents/agent-zero/memory/MEMORY.md").read_text())

    def test_interrupted_publication_keeps_the_previous_handoff(self):
        old = self.handoff.read_text()
        with patch.object(s.os, "replace", side_effect=OSError("fixture interruption")):
            with self.assertRaises(OSError):
                s.append_checkpoint(self.root, self.summary, "interrupted", self.now)
        self.assertEqual(old, self.handoff.read_text())

    def test_invalid_summary_never_changes_handoff(self):
        old = self.handoff.read_text()
        for summary in (None, {**self.summary, "lessons": ["bad\nheading"]}, {**self.summary, "spawns": ["x"] * 4}):
            with self.assertRaises(ValueError):
                s.append_checkpoint(self.root, summary, "bad", self.now)
        self.assertEqual(old, self.handoff.read_text())

    def test_stop_uses_final_response_and_pinned_tools_free_haiku(self):
        event = dict(hook_event_name="Stop", session_id="fixture", cwd=str(self.root),
                     transcript_path="/must-not-read-reasoning", last_assistant_message="Final result: builder x blocked.")
        result = SimpleNamespace(returncode=0, stdout=json.dumps(dict(modelUsage={"claude-haiku-5-5": {}}, structured_output=self.summary)))
        with patch.object(s, "resolve_data_home", return_value=self.root), patch.object(s.Path, "home", return_value=self.root), \
                patch.object(s, "LIVE", self.root), patch.object(s.subprocess, "run", side_effect=[result, SimpleNamespace(returncode=0)]) as run:
            self.assertEqual(0, s.checkpoint(event))
        argv = run.call_args_list[0].args[0]
        self.assertEqual("claude-haiku-5-5", argv[argv.index("--model") + 1])
        self.assertEqual("", argv[argv.index("--tools") + 1])
        self.assertNotIn("must-not-read", run.call_args_list[0].kwargs["input"])
        self.assertIn("previous entry", self.handoff.read_text())

    def test_stop_driver_detaches_and_never_forwards_transcript_path(self):
        event = dict(hook_event_name="Stop", session_id="fixture", cwd=str(self.root),
                     transcript_path="/never-forward", last_assistant_message="Completed report")
        child = Mock()
        with patch.object(s.subprocess, "Popen", return_value=child) as start:
            self.assertEqual(0, s.launch_checkpoint(event))
        self.assertTrue(start.call_args.kwargs["start_new_session"])
        self.assertEqual(start.call_args.kwargs["stdout"], s.subprocess.DEVNULL)
        self.assertNotIn("never-forward", child.stdin.write.call_args.args[0])
        child.stdin.close.assert_called_once()

    def test_subagent_or_recursion_does_not_call_model(self):
        with patch.object(s.subprocess, "run") as run:
            self.assertEqual(0, s.checkpoint(dict(hook_event_name="SubagentStop")))
            with patch.dict(s.os.environ, A0_SELF_CHECKPOINT="1"):
                self.assertEqual(0, s.checkpoint(dict(hook_event_name="Stop")))
        run.assert_not_called()

    def test_checkpoint_never_changes_shared_or_legacy_memory(self):
        legacy = self.root / ".agents/HANDOFF.md"
        shared = self.root / ".agents/memory/MEMORY.md"
        shared.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text("preserved old handoff")
        shared.write_text("reviewed shared fact")
        s.append_checkpoint(self.root, self.summary, "isolated", self.now)
        self.assertEqual(legacy.read_text(), "preserved old handoff")
        self.assertEqual(shared.read_text(), "reviewed shared fact")

    def test_standalone_checkpoint_creates_ignored_seat_state(self):
        s.subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        s.append_checkpoint(self.root, self.summary, "first-writer", self.now)
        result = s.subprocess.run(["git", "-C", str(self.root), "check-ignore", str(self.handoff)], capture_output=True)
        self.assertEqual(result.returncode, 0)
        for name in ("memory", "notes", "lessons", "session-context"):
            self.assertTrue((self.handoff.parent / name).is_dir())
