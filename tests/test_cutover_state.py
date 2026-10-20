import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

BIN = Path(__file__).resolve().parents[1] / "bin"


class CutoverStateTest(unittest.TestCase):
    def test_task_and_ask_share_external_state(self):
        with tempfile.TemporaryDirectory() as state:
            env = dict(os.environ, A0_DATA_HOME=state)
            result = subprocess.run([sys.executable, str(BIN / "a0-task"), "add",
                                     "Synthetic cutover task", "--his", "synthetic fixture"],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            tasks = list((Path(state) / "tasks").glob("t-*.json"))
            self.assertEqual(len(tasks), 1)
            with patch.dict(os.environ, {"A0_DATA_HOME": state}):
                ask = runpy.run_path(str(BIN / "ask"), run_name="cutover_fixture")
            self.assertEqual(ask["TASKS"], Path(state) / "tasks")
            self.assertEqual(ask["A0TASK"], BIN / "a0-task")
            generated = subprocess.run([sys.executable, str(BIN / "a0-task"), "index"],
                                       env=env, capture_output=True, text=True)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            self.assertTrue((Path(state) / ".agents/A0-plan.json").is_file())

    def test_upgrade_targets_repository_not_live_tree(self):
        upgrade = runpy.run_path(str(BIN / "a0-upgrade"), run_name="cutover_fixture")
        repo = Path.home() / "SISO_Workspace/_data/worktrees/siso/main"
        self.assertEqual(upgrade["REPOS"]["agent-zero"], repo)
        self.assertEqual(upgrade["wt_path"]({"repo": "agent-zero", "id": "synthetic"}).parent.name, "siso")
        self.assertFalse(upgrade["LOG"].is_relative_to(repo))

    def test_upgrade_stages_only_its_module(self):
        upgrade = runpy.run_path(str(BIN / "a0-upgrade"), run_name="cutover_fixture")
        with tempfile.TemporaryDirectory() as tmp:
            wt = Path(tmp)
            module = wt / "agents/zero"
            module.mkdir(parents=True)
            calls = []
            def shell(args, **kwargs):
                calls.append(args)
                return SimpleNamespace(returncode=1 if "--quiet" in args else 0, stdout="1")
            ship = upgrade["cmd_ship"]
            with patch.dict(ship.__globals__, {
                "get": lambda _: {"repo": "agent-zero", "id": "synthetic"},
                "wt_path": lambda _: wt, "sh": shell,
                "commit": lambda *_: None, "open_pr": lambda *_: None,
            }), patch("subprocess.run", return_value=SimpleNamespace(returncode=0)) as run:
                ship(["synthetic", "--check", "synthetic-check"])
            self.assertEqual(run.call_args.kwargs["cwd"], module)
            self.assertIn(["git", "add", "-A", "--", "agents/zero"], calls)
            self.assertNotIn(["git", "add", "-A"], calls)
