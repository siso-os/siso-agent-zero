import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'bin/a0-upgrade'
loader = importlib.machinery.SourceFileLoader('upgrade_intake', str(SOURCE))
spec = importlib.util.spec_from_loader(loader.name, loader)
upgrade = importlib.util.module_from_spec(spec)
loader.exec_module(upgrade)


class UpgradeIntake(unittest.TestCase):
    def test_lessons_arrays_final_lines_and_idempotency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lessons = root / 'IMPROVE.jsonl'
            lessons.write_text(json.dumps(dict(lessons=['Reuse the existing token ledger before building a second.']))+'\n')
            final = root / 'ret-builder.txt'
            final.write_text('RETURN\nSTATUS: done\nLEARNED: Count cached input only once in a Codex run.\n')
            with patch.object(upgrade, 'STATE', root / 'upgrades.jsonl'):
                upgrade.cmd_ingest(['--limit','10',str(lessons),str(final)])
                self.assertEqual(len(upgrade.current()), 2)
                upgrade.cmd_ingest(['--limit','10',str(lessons),str(final)])
                self.assertEqual(len(upgrade.current()), 2)
                self.assertTrue(all(r['needs_scope_review'] for r in upgrade.current().values()))
                self.assertTrue(all(r['status']=='queued' for r in upgrade.current().values()))

    def test_dry_run_does_not_file_and_ignores_reasoning(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); final=root/'ret.txt'
            final.write_text('thinking: PRIVATE_REASONING_MARKER\nSTATUS: done\nLEARNED: Read existing corpus before external research.\n')
            with patch.object(upgrade, 'STATE', root/'upgrades.jsonl'):
                upgrade.cmd_ingest(['--dry-run',str(final)])
                self.assertFalse(upgrade.STATE.exists())
                candidates=list(upgrade.lesson_candidates([final]))
                self.assertEqual(len(candidates),1)
                self.assertNotIn('PRIVATE_REASONING_MARKER',json.dumps(candidates))


class ConcreteLessons(unittest.TestCase):
    def test_ledger_words_target_and_normalized_active_dedupe(self):
        for status in ('queued', 'working', 'merged'):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                ledger = root / 'LEDGER.md'
                lesson = 'Fix `agents/zero/bin/look` to count merged upgrades.'
                ledger.write_text('- 2026-10-21: ' + lesson + '\n')
                with patch.object(upgrade, 'STATE', root / 'upgrades.jsonl'):
                    upgrade.cmd_ingest([str(ledger)])
                    row = next(iter(upgrade.current().values()))
                    self.assertIn(lesson, row['idea'])
                    self.assertIn('target: agents/zero/bin/look', row['why'])
                    upgrade.put(dict(id=row['id'], status=status, idea=lesson.upper(), lesson=''))
                    upgrade.cmd_ingest([str(ledger)])
                    self.assertEqual(len(upgrade.current()), 1)

    def test_dropped_idea_can_be_filed_again(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); ledger = root / 'LEDGER.md'
            ledger.write_text('- 2026-10-21: Fix bin/look to count merged upgrades.\n')
            with patch.object(upgrade, 'STATE', root / 'upgrades.jsonl'):
                upgrade.cmd_ingest([str(ledger)])
                upgrade.put(dict(id='u001', status='dropped'))
                upgrade.cmd_ingest([str(ledger)])
                self.assertEqual(len(upgrade.current()), 2)

if __name__ == '__main__': unittest.main()
