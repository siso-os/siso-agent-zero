"""Delivery contract: authority, explicit unknowns and lossless existing records."""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "bin/a0-task"


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.env = dict(os.environ, A0_DATA_HOME=str(self.home), PYTHONDONTWRITEBYTECODE="1")
        self.task_id = self.cli("add", "fixture", "--his", "fixture").stdout.strip()
        self.task = self.home / "tasks" / (self.task_id + ".json")

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(CLI), *args], env=self.env,
                                text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def module(self, value):
        path = self.home / "module.json"
        path.write_text(json.dumps(value))
        return str(path)

    def test_legacy_live_is_not_release_proof(self):
        t = json.loads(self.task.read_text())
        t.pop("delivery")
        t["stage"] = "live"
        t["evidence"] = ["merged abcdef1; health 200"]
        self.task.write_text(json.dumps(t))
        before = self.task.read_bytes()
        result = json.loads(self.cli("resolve", self.task_id).stdout)
        self.assertEqual(result["delivery"]["task_id"], self.task_id)
        for field in ("run_id", "tested_commit", "landed_commit", "running_commit", "observed_result"):
            self.assertIsNone(result["delivery"][field])
            self.assertIn(field, result["missing"])
        self.assertEqual(self.task.read_bytes(), before)

    def test_module_defaults_and_task_override(self):
        module = self.module({"id": "siso.agents.zero", "delivery": {
            "source_authority": "sisodias/siso", "target": "laptop",
            "writable_state_home": "$A0_DATA_HOME", "running_commit": "badcafe"}})
        self.cli("set", self.task_id, "delivery.target=mini", "delivery.landed_commit=abcdef1")
        result = json.loads(self.cli("resolve", self.task_id, "--module", module).stdout)["delivery"]
        self.assertEqual(result["target"], "mini")
        self.assertEqual(result["writable_state_home"], str(self.home))
        self.assertEqual(result["landed_commit"], "abcdef1")
        self.assertIsNone(result["running_commit"])
        self.cli("set", self.task_id, "delivery.target=")
        cleared = json.loads(self.cli("resolve", self.task_id, "--module", module).stdout)
        self.assertIsNone(cleared["delivery"]["target"])
        self.assertIn("target", cleared["missing"])

    def test_external_issue_authority_and_named_module(self):
        module = self.module({"name": "apps/streaming"})
        issue = "https://github.com/HALO-AGENCY/halo/issues/867"
        self.cli("set", self.task_id, "delivery.task_authority=GitHub Issues",
                 "delivery.task_id=" + issue, "delivery.source_authority=HALO-AGENCY/halo",
                 "delivery.module_id=apps/streaming")
        facts = json.loads(self.cli("resolve", self.task_id, "--module", module).stdout)["delivery"]
        self.assertEqual(facts["task_id"], issue)
        self.assertEqual(facts["source_authority"], "HALO-AGENCY/halo")
        self.assertIsNone(facts["tested_commit"])

    def test_invalid_update_does_not_write_partial_facts(self):
        before = self.task.read_bytes()
        result = self.cli("set", self.task_id, "delivery.target=mini",
                          "delivery.running_commit=HTTP200", ok=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.task.read_bytes(), before)
        self.assertEqual(self.cli("set", self.task_id, "delivery.typo=x", ok=False).returncode, 2)

    def test_wrong_module_refuses(self):
        self.cli("set", self.task_id, "delivery.module_id=siso.agents.zero")
        module = self.module({"id": "another.product"})
        self.assertEqual(self.cli("resolve", self.task_id, "--module", module, ok=False).returncode, 2)

    def test_generated_plan_preserves_check_and_delivery(self):
        self.cli("set", self.task_id, "done_check=python3 verify.py",
                 "delivery.run_id=builder-1", "delivery.evidence_link=https://example.test/proof")
        self.cli("index")
        item = json.loads((self.home / ".agents/A0-plan.json").read_text())["items"][0]
        self.assertEqual(item["done_check"], "python3 verify.py")
        self.assertEqual(item["delivery"]["run_id"], "builder-1")
        self.assertIsNone(item["delivery"]["running_commit"])

    def test_due_marks_a_goal_in_the_index(self):
        self.cli("set", self.task_id, "due=2026-10-23T20:05+07:00", "done_check=prod flipped")
        row = json.loads((self.home / "tasks/INDEX.json").read_text())["tasks"][0]
        self.assertEqual(row["due"], "2026-10-23T20:05+07:00")
        for bad in ("due=20:05", "due=2026-10-23T20:05"):  # no date; no zone
            self.assertNotEqual(self.cli("set", self.task_id, bad, ok=False).returncode, 0)
        self.cli("set", self.task_id, "due=")
        row = json.loads((self.home / "tasks/INDEX.json").read_text())["tasks"][0]
        self.assertIsNone(row["due"])


class StageAliasTests(unittest.TestCase):
    """A hand-written 'done' stage is an alias of live; it must not crash index or plan."""
    def setUp(self):
        sys.dont_write_bytecode = True
        loader = SourceFileLoader("a0_task", str(CLI))
        self.a0 = module_from_spec(spec_from_loader("a0_task", loader))
        loader.exec_module(self.a0)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        home = Path(tmp.name)
        self.a0.TASKS = home / "tasks"
        self.a0.TASKS.mkdir()
        self.a0.INDEX = self.a0.TASKS / "INDEX.json"
        self.a0.PLAN = home / "A0-plan.json"

    def test_hand_written_done_is_live(self):
        self.a0.save_task(self.a0.fresh_task("t-0001", "fixture", "fixture", stage="done"))
        index = self.a0.rebuild()
        self.assertEqual(index["counts"]["by_stage"], {"live": 1})
        self.assertEqual(self.a0.plan_view(index)["items"][0]["status"], "checked")


if __name__ == "__main__":
    unittest.main()
