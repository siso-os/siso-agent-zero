"""Upgrade loop receipts: real Git staging, private path refusal, and rendered Look."""
import contextlib
import datetime
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

BIN = Path(__file__).resolve().parents[1] / 'bin'
sys.path.insert(0, str(BIN))

def load(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(BIN / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

upgrade = load('upgrade_loop', 'a0-upgrade')
look = load('look_loop', 'look')

class UpgradeLoop(unittest.TestCase):
    def test_ship_stages_outside_module_and_rename(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, check=True, capture_output=True, text=True).stdout
            git('init', '-q'); git('config', 'user.email', 'fixture@example.com'); git('config', 'user.name', 'Fixture')
            (root / 'old name').write_text('original\n'); git('add', '.'); git('commit', '-qm', 'base')
            git('update-ref', 'refs/remotes/origin/main', 'HEAD')
            git('mv', 'old name', 'new name')
            (root / 'agents/zero').mkdir(parents=True)
            target = root / 'agents/skills/hub/haiku-team.js'
            target.parent.mkdir(parents=True); target.write_text('// correction\n')
            real_sh = upgrade.sh
            def local_sh(args, **kwargs):
                if args[:2] == ['git', 'push']:
                    return None
                return real_sh(args, **kwargs)
            with patch.object(upgrade, 'get', return_value=dict(id='u001', repo='agent-zero')), patch.object(upgrade, 'wt_path', return_value=root), patch.object(upgrade, 'sh', side_effect=local_sh), patch.object(upgrade, 'commit') as commit, patch.object(upgrade, 'open_pr'):
                upgrade.cmd_ship(['u001', '--check', 'true'])
                commit.assert_called_once()
            staged = git('diff', '--cached', '--name-only')
            self.assertIn('agents/skills/hub/haiku-team.js', staged)
            self.assertIn('new name', staged)
            print('SHIP: staged agents/skills/hub/haiku-team.js outside agents/zero')

    def test_private_paths_refused_before_staging(self):
        for path in ('secrets/key', 'x/.credentials/key', 'personal/a', '.env', 'x/.env.local', 'x/token.env'):
            with self.subTest(path=path), patch.object(upgrade, 'sh') as sh:
                sh.return_value.stdout = '?? ' + path + '\0'
                with self.assertRaisesRegex(SystemExit, 'REFUSED'):
                    upgrade.stage_changes(Path('/unused'))
                self.assertEqual(sh.call_count, 1)

    def test_look_renders_recent_merged_reasons_max_five_lines(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / 'upgrades.jsonl'
            now = datetime.datetime.now()
            rows = []
            for i in range(7):
                rows += [dict(id=f'u{i:03}', idea='fix', why='Stop repeating the staging mistake. ' * 4), dict(id=f'u{i:03}', status='merged', at=now.isoformat())]
            rows += [dict(id='old', status='merged', at=(now-datetime.timedelta(days=8)).isoformat()), dict(id='queued', status='queued', at=now.isoformat())]
            state.write_text('\n'.join(map(json.dumps, rows)))
            with patch.dict(os.environ, A0_UPGRADES_FILE=str(state)):
                lines = look.upgrades()
                self.assertEqual(len(lines), 5)
                self.assertEqual(lines[0], '7 merged in the last 7 days')
                self.assertTrue(all(len(line.split(': ', 1)[1]) <= 80 for line in lines[1:]))
                with contextlib.ExitStack() as stack:
                    for name in ('doctor', 'shipping', 'jobs', 'tasks', 'pipeline', 'roles', 'his_words', 'self_warnings'):
                        stack.enter_context(patch.object(look, name, return_value=[]))
                    stack.enter_context(patch('owner_idle.summary', return_value='fixture'))
                    stack.enter_context(patch.object(sys, 'argv', ['look']))
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output): look.main()
                self.assertIn('== Upgrades\n  7 merged', output.getvalue())
                print('LOOK: == Upgrades / ' + lines[0])

    def test_any_seat_files_with_seat_and_area_and_week_counts_it(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / 'upgrades.jsonl'
            with patch.object(upgrade, 'STATE', state), patch.object(sys, 'argv', ['a0-upgrade', 'add']), \
                    contextlib.redirect_stdout(io.StringIO()):
                upgrade.cmd_add(['fix the HALO deploy skill wording', '--why', 'seat hit it twice', '--seat', 'HALO', '--area', 'agents/skills/hub'])
                r = upgrade.current()['u001']
            self.assertEqual((r['seat'], r['area']), ('HALO', 'agents/skills/hub'))
            with self.assertRaises(SystemExit), patch.object(upgrade, 'STATE', state):
                upgrade.cmd_add(['x', '--why', 'y', '--area', '../etc'])
        recs = [dict(id='u001', seat='HALO', at='2026-10-23T10:00:00'), dict(id='u001', status='merged', at='2026-10-23T11:00:00'),
                dict(id='u002', at='2026-10-22T10:00:00')]
        commits = [('2026-10-23', 'a0-upgrade u001: fix'), ('2026-10-23', 'skills: research-first'), ('2026-10-23', 'no prefix here')]
        t = upgrade.week_table(recs, commits, 4)['2026-W43']
        self.assertEqual(t['HALO'], [1, 1, 0])
        self.assertEqual(t['agent-zero'], [1, 0, 0])  # legacy rows without a seat
        self.assertEqual((t['skills'], t['other']), ([0, 0, 1], [0, 0, 1]))

    def test_merged_is_recorded_when_authoring_sync_fails(self):
        # u324, 23 Oct: siso sync exit 3 (dirty main) stops pull_live before publishing live, by design; it used to stop
        # before "merged" was written too, so 19 merged upgrades stayed "working". The merge is recorded first now.
        def fake_sh(args, **kw):
            if args[:3] == ['gh', 'pr', 'view']: return SimpleNamespace(returncode=0, stdout='MERGED\n', stderr='')
            return SimpleNamespace(returncode=3 if args[-1] == 'sync' else 0, stdout='', stderr='')
        puts = []
        with patch.object(upgrade, 'sh', side_effect=fake_sh), patch.object(upgrade, 'put', side_effect=puts.append), \
                patch.object(upgrade, 'get', return_value=dict(id='u009', repo='agent-zero')), self.assertRaises(SystemExit):
            upgrade.merge(dict(id='u009', repo='agent-zero'), 'https://github.com/o/r/pull/9', Path('/unused'))
        self.assertEqual(puts, [dict(id='u009', status='merged', pr='https://github.com/o/r/pull/9')])

    def test_merge_refreshes_installed_skill_copies(self):
        # BRAVE index, 23 Oct: upgrades landed in agents/zero/.claude/skills but ~/.agents/skills kept the old copy.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); src = root / 'wt'; home = root / 'skills'
            (src / 'agents/zero/.claude/skills/foo').mkdir(parents=True)
            (src / 'agents/zero/.claude/skills/foo/SKILL.md').write_text('name: foo\nNEW\n')
            (home / 'foo').mkdir(parents=True); (home / 'foo/SKILL.md').write_text('name: foo\nOLD\n')
            (home / 'bar').mkdir(); (home / 'bar/SKILL.md').write_text('name: bar\n')
            calls = []
            def fake_sh(args, **kw):
                calls.append(args); return SimpleNamespace(returncode=0, stdout='', stderr='')
            with patch.object(upgrade, 'SKILLS_HOME', home), patch.object(upgrade, 'ARCHIVE', root / 'archive'), patch.object(upgrade, 'sh', side_effect=fake_sh):
                got = upgrade.refresh_installed(['agents/zero/.claude/skills/foo/SKILL.md', 'agents/skills/hub/registry/skills/global/bar/SKILL.md',
                                                 'agents/skills/hub/registry/skills/global/absent/SKILL.md', 'agents/zero/bin/look'], src, 'u009')
            self.assertEqual(got, ['foo', 'bar'])
            self.assertIn('NEW', (home / 'foo/SKILL.md').read_text())
            self.assertIn('OLD', next((root / 'archive').glob('*/foo-u009/SKILL.md')).read_text())
            self.assertEqual(calls[0][2:6], ['install', 'bar', '--target', str(home)])

    def test_firstmate_alias_uses_monorepo_worktree(self):
        self.assertEqual(upgrade.REPOS['firstmate'], upgrade.REPOS['agent-zero'])
        self.assertEqual(upgrade.wt_path(dict(id='u001', repo='firstmate')), upgrade.wt_path(dict(id='u001', repo='agent-zero')))
