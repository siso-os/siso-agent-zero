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

    def test_state_home_holds_legacy_only_on_the_host_with_the_existing_base_release(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("fixture_a0_home", BIN / "a0_data_home.py")
        homes = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(homes)
        with tempfile.TemporaryDirectory(prefix=".siso-ephemeral-a0-home.") as tmp:
            home = Path(tmp)
            with patch.dict(os.environ, clear=False), patch.object(homes.Path, "home", return_value=home):
                os.environ.pop("A0_DATA_HOME", None)
                self.assertEqual(homes.resolve_data_home(), home / "SISO_Workspace/_data/worktrees/siso/main/agents/zero")
                active = home / ".local/state/agent-base/live/active.json"
                active.parent.mkdir(parents=True)
                active.write_text('{}')
                self.assertEqual(homes.resolve_data_home(), home / "SISO_Workspace/SISO_Agents/agent-zero/siso-agent-zero")
                active.write_text(json.dumps({"a0DataHome": str(home / "SISO_Workspace/_data/worktrees/siso/main/agents/zero")}))
                self.assertEqual(homes.resolve_data_home(), home / "SISO_Workspace/_data/worktrees/siso/main/agents/zero")
                os.environ["A0_DATA_HOME"] = str(home / "verified-new-store")
                self.assertEqual(homes.resolve_data_home(), home / "verified-new-store")

    def test_private_context_stays_outside_tracked_task_state(self):
        with tempfile.TemporaryDirectory(prefix=".siso-ephemeral-private-state.") as tmp:
            data, private = Path(tmp) / "data", Path(tmp) / "private"
            raw = private / "transcript/raw/fixture.jsonl"
            raw.parent.mkdir(parents=True)
            raw.write_text('{"text":"synthetic fixture"}\n')
            with patch.dict(os.environ, {"A0_DATA_HOME": str(data), "A0_PRIVATE_HOME": str(private)}):
                az = runpy.run_path(str(BIN / "siso-az"), run_name="cutover_fixture")
                transcript = runpy.run_path(str(BIN / "a0-transcript"), run_name="cutover_fixture")
                recall = runpy.run_path(str(BIN / "recall"), run_name="cutover_fixture")
            self.assertEqual(az["TASKS"], str(data / ".agents/a0/tasks.json"))
            self.assertEqual(az["INBOX"], str(private / "inbox.log"))
            self.assertEqual(az["LOG"], str(private / "log.jsonl"))
            self.assertEqual(transcript["OUT"], private / "transcript")
            self.assertEqual(recall["files_for"](".agents/a0/transcript/raw/*.jsonl"), [str(raw)])

    def test_upgrade_targets_repository_not_live_tree(self):
        upgrade = runpy.run_path(str(BIN / "a0-upgrade"), run_name="cutover_fixture")
        repo = Path.home() / "SISO_Workspace/_data/worktrees/siso/main"
        self.assertEqual(upgrade["REPOS"]["agent-zero"], repo)
        self.assertEqual(upgrade["wt_path"]({"repo": "agent-zero", "id": "synthetic"}).parent.name, "siso")
        self.assertFalse(upgrade["LOG"].is_relative_to(repo))

    def test_upgrade_stages_changed_paths_across_monorepo(self):
        upgrade = runpy.run_path(str(BIN / "a0-upgrade"), run_name="cutover_fixture")
        with tempfile.TemporaryDirectory() as tmp:
            wt = Path(tmp)
            module = wt / "agents/zero"
            module.mkdir(parents=True)
            calls = []
            def shell(args, **kwargs):
                calls.append(args)
                return SimpleNamespace(returncode=1 if "--quiet" in args else 0, stdout=" M agents/skills/hub/haiku-team.js\0" if args[1] == "status" else "1")
            ship = upgrade["cmd_ship"]
            with patch.dict(ship.__globals__, {
                "get": lambda _: {"repo": "agent-zero", "id": "synthetic"},
                "wt_path": lambda _: wt, "sh": shell,
                "commit": lambda *_: None, "open_pr": lambda *_: None,
            }), patch("subprocess.run", return_value=SimpleNamespace(returncode=0)) as run:
                ship(["synthetic", "--check", "synthetic-check"])
            self.assertEqual(run.call_args.kwargs["cwd"], module)
            self.assertIn(["git", "--literal-pathspecs", "add", "-A", "--", "agents/skills/hub/haiku-team.js"], calls)
            self.assertNotIn(["git", "add", "-A"], calls)
