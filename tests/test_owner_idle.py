"""Selection is conservative and reminders never repeat within one conversation."""
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import owner_idle as idle


class Selection(unittest.TestCase):
    def setUp(self):
        self.now = 10000
        self.row = dict(seat='OWNER', thread='old', zero=False, active=False,
                        queued=False, background=False, pending_input=False,
                        completed=8000, started=7900, tokens=150000,
                        said='Task completed.', checkpoint=False)
        self.limits = idle.thresholds({}, 'OWNER')

    def choose(self, **changes):
        return idle.select({**self.row, **changes}, self.limits, [], self.now)[0]

    def test_stale_checkpoint_gets_one_reminder(self):
        self.assertEqual(self.choose(), 'tell')
        events = [dict(source='owner-idle', thread='old', kind='checkpoint-request')]
        self.assertEqual(idle.select(self.row, self.limits, events, self.now)[0], 'skip')
        self.assertEqual(idle.select({**self.row, 'thread': 'new'}, self.limits, events, self.now)[0], 'tell')

    def test_fresh_checkpoint_can_finish_reminded_owner(self):
        events = [dict(source='owner-idle', thread='old', kind='checkpoint-request')]
        self.assertEqual(idle.select({**self.row, 'checkpoint': True}, self.limits, events, self.now)[0], 'fresh')

    def test_every_busy_unknown_or_question_signal_holds(self):
        for change in [dict(zero=True), dict(active=True), dict(queued=True),
                       dict(background=True), dict(background=None), dict(pending_input=True),
                       dict(pending_input=None), dict(completed=None), dict(said=''),
                       dict(said='QUESTION FOR SHAAN: choose a route'), dict(said='Which route?'),
                       dict(said='Waiting for Shaan'), dict(tokens=None), dict(error='unreachable'),
                       dict(completed=9990), dict(tokens=99999)]:
            with self.subTest(change=change):
                self.assertEqual(self.choose(**change), 'skip')

    def test_threshold_boundaries_and_overrides(self):
        self.assertEqual(self.choose(completed=8800, tokens=100000), 'tell')
        values = idle.thresholds({'default': {'idle_minutes': 10}, 'OWNER': {'context_tokens': 200000}}, 'OWNER')
        self.assertEqual(values, {'idle_minutes': 10, 'context_tokens': 200000})
        self.assertEqual(idle.select(self.row, values, [], self.now)[0], 'skip')
        for invalid in [0, -1, True, '100k', float('nan')]:
            with self.assertRaises(ValueError):
                idle.thresholds({'OWNER': {'context_tokens': invalid}}, 'OWNER')


class Snapshot(unittest.TestCase):
    def test_live_source_checkpoints_route_to_writable_seat_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'live'
            (root / '.git').parent.mkdir(parents=True)
            (root / '.git').write_text('gitdir: fixture')
            (root / '.siso').mkdir()
            handoff, memory = idle.checkpoint_paths('OWNER', root / 'agents/zero')
            self.assertEqual(handoff, root.parent / 'main/.agents/agents/OWNER/HANDOFF.md')
            self.assertEqual(memory, handoff.parent / 'memory/MEMORY.md')

    def test_readonly_db_and_checkpoint_written_during_last_turn(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            handoff, memory = idle.checkpoint_paths('OWNER', root)
            for path in (handoff, memory):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('Current checkpoint\n')
                os.utime(path, (8500, 8500))
            path = root / 'state.sqlite'
            writer = sqlite3.connect(path)
            writer.executescript('''
                create table orchestration_v2_projection_threads(thread_id text,payload_json text);
                create table orchestration_v2_projection_runs(thread_id text,status text,requested_at text,completed_at text,ordinal int);
                create table orchestration_v2_projection_provider_threads(thread_id text,updated_at text,payload_json text);
                create table orchestration_v2_projection_runtime_requests(thread_id text,payload_json text);
                create table orchestration_v2_projection_messages(thread_id text,role text,streaming int,created_at text,payload_json text);
            ''')
            writer.execute('insert into orchestration_v2_projection_threads values (?,?)', ('old', json.dumps(dict(title='Owner', activeProviderThreadId='p'))))
            writer.execute('insert into orchestration_v2_projection_runs values (?,?,?,?,?)', ('old', 'completed', '1970-01-01T02:11:40Z', '1970-01-01T02:30:00Z', 1))
            provider = dict(id='p', status='idle', pendingBackgroundTasks=[], contextUsage={'usedTokens': 150000})
            writer.execute('insert into orchestration_v2_projection_provider_threads values (?,?,?)', ('old', 'now', json.dumps(provider)))
            writer.execute('insert into orchestration_v2_projection_messages values (?,?,?,?,?)', ('old', 'assistant', 0, 'now', json.dumps({'text': 'Completed.'})))
            writer.commit()
            db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
            entry = dict(thread='old', cwd=str(root))
            row = idle.snapshot(db, 'OWNER', entry)
            self.assertTrue(row['checkpoint'])
            self.assertEqual(row['tokens'], 150000)
            with self.assertRaises(sqlite3.OperationalError):
                db.execute('delete from orchestration_v2_projection_runs')
            # Background work on an older provider still belongs to this owner.
            provider.update(id='older', pendingBackgroundTasks=[{'taskId': 'bg'}])
            writer.execute('insert into orchestration_v2_projection_provider_threads values (?,?,?)', ('old', 'earlier', json.dumps(provider)))
            writer.commit()
            self.assertTrue(idle.snapshot(db, 'OWNER', entry)['background'])
            memory.write_text('old memory')
            os.utime(memory, (100, 100))
            self.assertFalse(idle.snapshot(db, 'OWNER', entry)['checkpoint'])
            db.close()
            writer.close()


if __name__ == '__main__':
    unittest.main()
