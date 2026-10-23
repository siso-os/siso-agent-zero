"""Verify scheduled upgrades invoke one Haiku upgrader and cannot overlap."""
import fcntl
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

REVIEW = Path(__file__).resolve().parents[1] / 'bin/a0-review'


class HaikuSelfUpgrade(unittest.TestCase):
    def test_one_upgrader_and_shared_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            command = home / '.local/bin/haiku'
            command.parent.mkdir(parents=True)
            command.write_text('#!/usr/bin/env python3\nimport json,os,sys\nfrom pathlib import Path\nPath(os.environ["HOME"],"call.json").write_text(json.dumps(sys.argv[1:]))\nprint("UPGRADER_FIXTURE_OK")\n')
            command.chmod(0o755)
            env = {**os.environ, 'HOME': str(home)}
            result = subprocess.run([str(REVIEW)], env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('UPGRADER_FIXTURE_OK', result.stdout)
            import json
            args = json.loads((home / 'call.json').read_text())
            self.assertEqual(args[1:3], ['--agent', 'upgrader'])
            self.assertIn('at most ONE filed upgrade', args[0])
            self.assertIn('a0-upgrade ingest --limit 3', args[0])
            self.assertIn('check current code and existing fixes', args[0])
            with (home / '.local/state/a0/haiku-selfupgrade.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                result = subprocess.run([str(REVIEW)], env=env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0)
                self.assertIn('SKIPPED: Haiku self-upgrade already running', result.stdout)


if __name__ == '__main__':
    unittest.main()
