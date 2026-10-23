"""Fleet dispatch keeps work queued below headroom and uses local admission."""
import contextlib
import importlib.machinery
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('fleet_admission', str(Path(__file__).resolve().parents[1] / 'bin/fleet'))
spec = importlib.util.spec_from_loader(loader.name, loader)
fleet = importlib.util.module_from_spec(spec)
loader.exec_module(fleet)


class StopTick(Exception):
    pass


class DispatchAdmission(unittest.TestCase):
    def tick(self, free):
        job = {'id': 'one', 'brief': 'fixture', 'status': 'queued'}
        manifest = {'name': 'fixture', 'jobs': [job], 'max': 6, 'machine': 'mini',
                    'model': 'fixture-model', 'why': 'fixture', 'effort': 'medium'}
        with contextlib.ExitStack() as stack:
            for name, value in {'locked': contextlib.nullcontext(), 'manifests': [manifest],
                                'ps': {}, 'sample': 0, 'enforce': None, 'pressure': ('normal', free),
                                'budget': 9 * fleet.GIB, 'admission_rss': 0, 'reserve': 0,
                                'workdir': '/tmp', 'dispatch': None, 'save': None, 'tree': set()}.items():
                stack.enter_context(patch.object(fleet, name, return_value=value))
            stack.enter_context(patch.object(fleet.shutil, 'disk_usage', return_value=SimpleNamespace(free=free)))
            stack.enter_context(patch.object(fleet.time, 'sleep', side_effect=StopTick))
            spawn = stack.enter_context(patch.object(fleet, 'spawn', return_value=(SimpleNamespace(), {'pid': 999})))
            with self.assertRaises(StopTick):
                fleet.runner('fixture')
            return job, manifest, spawn

    def test_below_headroom_stays_queued(self):
        job, manifest, spawn = self.tick(16 * fleet.GIB)
        self.assertEqual(job['status'], 'queued')
        self.assertIn('18', manifest['note'])
        spawn.assert_not_called()

    def test_admitted_dispatch_uses_receiving_host_gate(self):
        job, _, spawn = self.tick(40 * fleet.GIB)
        self.assertEqual(job['status'], 'running')
        self.assertEqual(spawn.call_args.args[0][:3], [fleet.CODEX_RUN, '--on', 'laptop'])
        self.assertNotIn('CODEX_RUN_ADMITTED', fleet.ENV)


if __name__ == '__main__':
    unittest.main()
