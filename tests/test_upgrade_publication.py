"""Dirty authoring state cannot block guarded adoption of an already landed upgrade."""
import importlib.machinery
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
loader=importlib.machinery.SourceFileLoader("upgrade_publication",str(Path(__file__).resolve().parents[1]/"bin/a0-upgrade"))
spec=importlib.util.spec_from_loader(loader.name,loader);upgrade=importlib.util.module_from_spec(spec);loader.exec_module(upgrade)
class UpgradePublication(unittest.TestCase):
 def test_dirty_sync_retains_state_and_still_uses_the_guarded_live_command(self):
  with patch.object(upgrade,"sh",side_effect=[SimpleNamespace(returncode=4),SimpleNamespace(returncode=0)]) as sh:
   result=upgrade.pull_live(upgrade.REPOS["agent-zero"],[])
  self.assertIn("authoring sync held",result)
  self.assertEqual([c.args[0][-1] for c in sh.call_args_list],["sync","live"])
  self.assertNotIn("check",sh.call_args_list[1].kwargs)
 def test_other_sync_refusals_never_publish(self):
  for code in (1,2,3,128):
   with self.subTest(code=code),patch.object(upgrade,"sh",return_value=SimpleNamespace(returncode=code)) as sh:
    with self.assertRaises(SystemExit):upgrade.pull_live(upgrade.REPOS["agent-zero"],[])
    self.assertEqual(sh.call_count,1)
 def test_live_refusal_remains_a_failure(self):
  with patch.object(upgrade,"sh",side_effect=[SimpleNamespace(returncode=4),SystemExit("live edits retained")]):
   with self.assertRaises(SystemExit):upgrade.pull_live(upgrade.REPOS["agent-zero"],[])
 def test_clean_sync_preserves_the_existing_receipt(self):
  with patch.object(upgrade,"sh",return_value=SimpleNamespace(returncode=0)):
   self.assertEqual(upgrade.pull_live(upgrade.REPOS["agent-zero"],[]),"synced monorepo and live")
