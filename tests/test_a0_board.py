import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
BIN = ROOT / 'agents/zero/bin/a0'
sys.path.insert(0, str(ROOT / 'agents/harness/bin'))
import a0_events as events


def module(path, name):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(mod)
    return mod


class BoardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {'A0_DATA_HOME': str(self.root / 'data'), 'A0_EVENTS': str(self.root / 'events.jsonl'),
                    'CODEX_RUN_STATE': str(self.root / 'runs'), 'A0_TEAMS': str(self.root / 'teams'),
                    'A0_BOARD_STATE': str(self.root / 'board'), 'A0_FLEET_JSON': str(self.root / 'fleet.json'),
                    'A0_DISPATCH_FILE': str(self.root / 'dispatch.jsonl'), 'A0_T3_DB': str(self.root / 'state.sqlite'),
                    'A0_AWAIT_REPORTED': str(self.root / 'await-reported.jsonl')}
        self.patch = patch.dict(os.environ, self.env)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for key in ('A0_DATA_HOME', 'A0_TEAMS', 'CODEX_RUN_STATE'):
            Path(self.env[key]).mkdir()
        (events.data_home() / 'tasks').mkdir()
        (self.root / 'fleet.json').write_text(json.dumps([
            {'seat': 'MINI', 'status': 'completed', 'machine': 'mini'},
            {'seat': 'A0', 'status': 'running', 'age': '2m'}]))

    def run_meta(self, name, pid=None):
        path = self.root / 'runs/runs' / name
        path.parent.mkdir(exist_ok=True)
        Path(str(path) + '.meta.json').write_text(json.dumps({'pid': pid or os.getpid(),
            'started': time.time() - 90, 'worker': name, 'task': 't-0001', 'dir': str(self.root)}))
        return path

    def task(self, ident='t-0001', owner='A0'):
        (events.data_home() / 'tasks' / (ident + '.json')).write_text(json.dumps({
            'id': ident, 'title': 'stub', 'owner': owner, 'stage': 'building', 'priority': 'P1'}))

    def board(self, *args):
        proc = subprocess.run([sys.executable, str(BIN), 'board', *args], text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_terminal_events_task_sidecar_return_and_idempotence(self):
        path = self.run_meta('builder')
        self.task()
        Path(str(path) + '.last.md').write_text('RETURN\nSTATUS: done — stub\nVERIFY: passed')
        first = events.finish(path, 0)
        events.finish(path, 0)
        self.assertEqual(first['status'], 'done')
        self.assertIn('VERIFY: passed', first['return'])
        self.assertEqual(first['task'], 't-0001')
        self.assertGreater(first['duration'], 89)
        self.assertEqual(len(Path(os.environ['A0_EVENTS']).read_text().splitlines()), 1)
        self.assertEqual(len((events.data_home() / 'tasks/events.jsonl').read_text().splitlines()), 1)

    def test_failure_overrides_done_and_needs_shaan(self):
        self.assertEqual(events.result_status('STATUS: done', 9), 'blocked')
        self.assertEqual(events.result_status('STATUS: needs-shaan', 0), 'needs-shaan')
        self.assertEqual(events.result_status('', 0), 'blocked')

    def test_running_pid_and_unattended_tasks(self):
        self.task()
        self.task('t-0002', None)
        self.run_meta('active')
        board = self.board('--json', '--since', '2h')
        self.assertTrue(next(r for r in board['running'] if r['who'] == 'active')['pid_alive'])
        self.assertEqual([r['id'] for r in board['unattended_tasks']], ['t-0002'])
        self.assertEqual(board['idle'][0]['machine'], 'mini')
        self.assertFalse((self.root / 'board').exists())

    def test_dead_pid_is_blocked_and_malformed_event_is_ignored(self):
        path = self.run_meta('dead', 99999999)
        Path(os.environ['A0_EVENTS']).write_text('{incomplete\n')
        board = self.board('--json')
        dead = next(r for r in board['blocked'] if r.get('run') == str(path))
        self.assertFalse(dead['pid_alive'])

    def test_remote_run_uses_local_mirror_without_claiming_remote_pid(self):
        path = self.run_meta('remote', 99999999)
        meta = json.loads(Path(str(path) + '.meta.json').read_text())
        meta.update(remote_run='/mini/run', machine='mini')
        Path(str(path) + '.meta.json').write_text(json.dumps(meta))
        Path(str(path) + '.mirror.json').write_text(json.dumps({'pid': os.getpid()}))
        board = self.board('--json')
        row = next(r for r in board['running'] if r.get('run') == str(path))
        self.assertIsNone(row['pid_alive'])
        self.assertTrue(row['observer_pid_alive'])

    def test_team_start_end_and_since(self):
        value = {'board': str(self.root / 'teams/stub.jsonl'), 'who': 'team', 'kind': 'team-start',
                 'status': 'running', 'at': time.time() - 20, 'task': 't-0001'}
        for kind, status in [('team-start', 'running'), ('team-end', 'blocked')]:
            value.update(kind=kind, status=status)
            proc = subprocess.run([sys.executable, str(BIN), 'team-event', json.dumps(value)], capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        board = self.board('--json', '--since', '10s')
        self.assertEqual(board['teams'][0]['status'], 'blocked')
        self.assertEqual(board['counts']['events_since'], 0)

    def test_backfill_exact_directory_and_repeat_safe(self):
        path = self.run_meta('historical', 99999999)
        Path(str(path) + '.last.md').write_text('RETURN\nSTATUS: done')
        Path(str(path) + '.usage.json').write_text(json.dumps({'exit': 0, 'secs': 20}))
        pids = self.root / 'pids.txt'
        pids.write_text('historical 99999999\nunknown 99999998\n')
        for _ in range(2):
            proc = subprocess.run([sys.executable, str(BIN), 'backfill', str(pids)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)['unmatched'], 1)
        self.assertEqual(len(Path(os.environ['A0_EVENTS']).read_text().splitlines()), 2)

    def test_notification_uses_mcp_send_once(self):
        path = self.run_meta('notify')
        Path(str(path) + '.last.md').write_text('RETURN\nSTATUS: done')
        with patch.object(events, 'notify') as send:
            events.finish(path, 0, 'A0')
            events.finish(path, 0, 'A0')
            self.assertEqual(send.call_count, 1)
            self.assertEqual(send.call_args.args[0], 'A0')

    def test_notify_payload_uses_authenticated_thread_send(self):
        fake = self.root / 'seat-fresh-t3'
        fake.write_text("class Mcp:\n def __init__(self, args): pass\n def call(self, name, value):\n  import json\n  from pathlib import Path\n  Path(__file__).with_name('sent.json').write_text(json.dumps([name, value]))\n")
        with patch.object(events, '__file__', str(self.root / 'a0_events.py')):
            events.notify('mcp:fixture', {'id': 'stub-id', 'who': 'builder', 'status': 'done',
                           'task': 't-0001', 'duration': 2, 'log': '/fixture/run.jsonl'})
        method, payload = json.loads((self.root / 'sent.json').read_text())
        self.assertEqual(method, 't3_thread_send')
        self.assertEqual(payload['threadId'], 'mcp:fixture')
        self.assertEqual(payload['mode'], 'auto')
        self.assertNotIn('\n', payload['message'])

    def test_asks_old_runs_and_missing_team_boards_never_disappear(self):
        self.task()
        self.task('t-0002')
        task_path = events.data_home() / 'tasks/t-0002.json'
        task = json.loads(task_path.read_text())
        task['stage'] = 'happy'
        task_path.write_text(json.dumps(task))
        (events.data_home() / 'tasks/t-broken.json').write_text('{broken')
        Path(self.env['A0_DISPATCH_FILE']).write_text('{broken dispatch\n')
        path = self.run_meta('old', 99999999)
        meta = json.loads(Path(str(path) + '.meta.json').read_text())
        meta['started'] = time.time() - 72 * 3600
        Path(str(path) + '.meta.json').write_text(json.dumps(meta))
        Path(str(path) + '.last.md').write_text('RETURN\nSTATUS: done')
        Path(str(path) + '.usage.json').write_text(json.dumps({'exit': 0, 'secs': 10}))
        events.finish(path, 0)
        events.emit({'id': 'archived-team', 'source': 'haiku-team', 'board': str(self.root / 'teams/gone.jsonl'),
                     'status': 'blocked', 'kind': 'team-end', 'at': time.time() - 9999, 'task': 't-0002'})
        board = self.board('--json', '--since', '1s')
        self.assertEqual({t['id'] for t in board['asks']}, {'t-0001', 't-0002', 't-broken'})
        self.assertFalse(next(t for t in board['asks'] if t['id'] == 't-0002')['outstanding'])
        self.assertEqual(len(board['coverage']['unreadable_tasks']), 1)
        self.assertTrue(board['dispatches'][0]['parse_error'])
        self.assertEqual(len(board['coverage']['missing_returns']), 1)
        self.assertIn(str(path), [r.get('run') for r in board['child_runs']])
        self.assertEqual(board['teams'][0]['receipt'], 'archived-team')
        self.assertEqual(len(board['receipts']), 2)

    def test_waiter_persists_correlated_done_and_blocked_without_prompt_text(self):
        import sqlite3
        from datetime import datetime, timezone
        iso = lambda t: datetime.fromtimestamp(t, timezone.utc).isoformat()
        self.task()
        self.task('t-0002')
        now = time.time()
        dispatch = {'at': now - 10, 'kind': 't3_thread_send', 'name': 'A0', 'thread': 'owner-thread',
                    'parent': 'session:fixture', 'brief': 't-0001 work-only fixture DO_NOT_COPY_PROMPT'}
        log = Path(self.env['A0_DISPATCH_FILE'])
        log.write_text(json.dumps(dispatch) + '\n')
        db = sqlite3.connect(self.env['A0_T3_DB'])
        db.execute('create table orchestration_v2_projection_runs (run_id text, thread_id text, ordinal int, status text, requested_at text, completed_at text)')
        db.execute('create table orchestration_v2_projection_threads (thread_id text, payload_json text)')
        db.execute('insert into orchestration_v2_projection_runs values (?, ?, ?, ?, ?, ?)',
                   ('run-owner', 'owner-thread', 1, 'completed', iso(now), iso(now)))
        db.execute('insert into orchestration_v2_projection_runs values (?, ?, ?, ?, ?, ?)',
                   ('run-child', 'child-thread', 1, 'completed', iso(now), iso(now)))
        db.execute('insert into orchestration_v2_projection_threads values (?, ?)',
                   ('child-thread', json.dumps({'lineage': {'rootThreadId': 'owner-thread', 'parentThreadId': 'owner-thread'}})))
        db.commit()
        waiter = module(BIN.with_name('a0-await'), 'waiter_fixture')
        waiter.DB = self.env['A0_T3_DB']
        row = {'seat': 'A0', 'thread': 'owner-thread', 'run': 1, 'status': 'completed',
               'activity': '0m', 'said_full': 'RETURN\nSTATUS: done\nVERIFY: fixture secret text not retained'}
        def wait():
            with patch.object(waiter, 'fleet', return_value={'A0': row}), \
                 patch.object(waiter, 'pending_questions', return_value=[]), \
                 patch.object(waiter, 'pending_children', return_value=0), \
                 patch.object(waiter, 'queued_runs', return_value=0), \
                 patch.object(waiter.time, 'sleep', side_effect=[None, AssertionError('waiter did not return')]), patch.object(sys, 'argv', ['a0-await', 'A0']):
                self.assertEqual(waiter.main(), 0)
        wait()
        # u316: the same message is never reported twice; a re-armed waiter keeps waiting for new words.
        with self.assertRaisesRegex(AssertionError, 'waiter did not return'):
            wait()
        board = self.board('--json', '--since', '1s')
        self.assertEqual(len(board['receipts']), 1)
        self.assertEqual(board['dispatches'][0]['outcome'], 'done')
        self.assertEqual(next(a for a in board['asks'] if a['id'] == 't-0001')['receipts'], [board['receipts'][0]['id']])
        self.assertIn('run-child', [r.get('run') for r in board['child_runs']])
        self.assertNotIn('DO_NOT_COPY_PROMPT', json.dumps(board))
        self.assertNotIn('secret text', Path(self.env['A0_EVENTS']).read_text())
        # A second ask stays outstanding; the old return cannot discharge it.
        newer = {**dispatch, 'at': now + 10, 'brief': 't-0002'}
        with log.open('a') as out:
            out.write(json.dumps(newer) + '\n')
        self.assertFalse(waiter.matches_dispatch(row, {**newer, 'id': 'new'}))
        board = self.board('--json')
        self.assertEqual(board['dispatches'][1]['outcome'], 'missing-return')
        self.assertTrue(next(a for a in board['asks'] if a['id'] == 't-0002')['missing_receipt'])
        db.execute('update orchestration_v2_projection_runs set completed_at=? where thread_id=?', (iso(now + 20), 'owner-thread'))
        db.commit()
        db.close()
        # A steer can finish on a run that started before the dispatch.
        row['said_full'] = 'RETURN\nSTATUS: blocked — missing fixture access'
        wait()
        board = self.board('--json')
        self.assertEqual(board['dispatches'][1]['outcome'], 'blocked')
        self.assertEqual(len(board['receipts']), 2)
        self.assertEqual(board['coverage']['missing_returns'], [])

    def test_board_deadline_on_slow_fleet_uses_snapshot(self):
        board = module(BIN, 'board_fixture')
        os.environ.pop('A0_FLEET_JSON')
        (self.root / 'board').mkdir()
        (self.root / 'board/board-fleet.json').write_text(json.dumps({'at': time.time() - 40,
                         'rows': [{'seat': 'MINI', 'status': 'completed', 'machine': 'mini'}]}))
        with patch.object(board.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fleet-check', 1.15)), patch.object(board.subprocess, 'Popen'):
            snap = board.snapshot(time.time() - 3600)
        self.assertEqual(snap['fleet']['source'], 'cached')
        self.assertEqual(snap['idle'][0]['seat'], 'MINI')


if __name__ == '__main__':
    unittest.main()
