"""Per-seat memory resolves independently of the project task-store location."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
from a0_data_home import resolve_agent_home


class AgentStateHome(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.env = patch.dict(os.environ)
        self.env.start()
        self.addCleanup(self.env.stop)
        os.environ.pop("SISO_AGENT_STATE_ROOT", None)

    def repo(self, name):
        root = self.root / name
        root.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        return root

    def test_subprojects_share_one_seat_and_other_seats_are_isolated(self):
        root = self.repo("repo")
        project = root / "agents/zero"
        project.mkdir(parents=True)
        expected = root / ".agents/agents/agent-zero"
        self.assertEqual(resolve_agent_home(project), expected)
        self.assertEqual(resolve_agent_home(root), expected)
        self.assertNotEqual(resolve_agent_home(project, "agents-hub"), expected)

    def test_live_requires_explicit_paired_writable_root(self):
        live = self.repo("siso/live")
        state = self.repo("siso/main")
        with self.assertRaisesRegex(ValueError, "requires"):
            resolve_agent_home(live)
        os.environ["SISO_AGENT_STATE_ROOT"] = str(state)
        self.assertEqual(resolve_agent_home(live), state / ".agents/agents/agent-zero")
        self.assertFalse((live / ".agents").exists())

    def test_invalid_name_or_relative_selection_cannot_escape(self):
        for name in ("../other", "", "a/b"):
            with self.assertRaises(ValueError):
                resolve_agent_home(self.root, name)
        os.environ["SISO_AGENT_STATE_ROOT"] = "../main"
        with self.assertRaisesRegex(ValueError, "absolute"):
            resolve_agent_home(self.root)

    def test_symlinked_state_is_refused(self):
        (self.root / ".agents").symlink_to(self.root / "outside", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            resolve_agent_home(self.root)
