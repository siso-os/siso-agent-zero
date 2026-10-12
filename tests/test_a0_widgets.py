"""Disposable operational snapshots only; never reads a live inbox or widget directory."""
import fcntl
from unittest.mock import patch
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest

loader = importlib.machinery.SourceFileLoader('a0_widgets', str(Path(__file__).parents[1] / 'bin/a0-widgets'))
spec = importlib.util.spec_from_loader(loader.name, loader)
w = importlib.util.module_from_spec(spec)
loader.exec_module(w)


class ProducerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a0-widgets-synthetic-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.write('ann.jsonl', [{'id': 7, 'title': 'First', 'body': 'Ready', 'project': 'Fixture', 'at': '2026-10-06T00:00:00Z', 'needs': 'Review'}, {'id': 8, 'title': 'Second', 'body': 'Done', 'needs': 'nothing'}], True)
        self.write('inbox.jsonl', [], True)
        self.write('plan.json', {'owner': 'Fixture', 'project': 'Widget acceptance', 'items': [{'id': 'p1', 'title': 'Check parity', 'status': 'checked', 'to': {'agent': 'tester'}, 'his': 'Keep the fields', 'evidence': ['Fixture passed']}]})
        self.write('state.json', {'state': 'claimed', 'holder': {'model': 'fixture'}})
        self.write('manifest.json', {'announcements': 'ann.jsonl', 'inbox': 'inbox.jsonl', 'plans': ['plan.json'], 'tasks': [{'id': 'task-1', 'state': 'state.json'}]})
        self.args = types.SimpleNamespace(manifest=self.root/'manifest.json', output_root=self.root/'widgets', publish=False)
    def write(self, name, data, lines=False):
        (self.root/name).write_text(''.join(json.dumps(r)+'\n' for r in data) if lines else json.dumps(data))
    def docs(self):
        return {p.stem: json.loads(p.read_text()) for p in (self.root/'widgets/A0').glob('*.json')}
    def publish(self):
        self.args.publish=True
        return w.run(self.args)
    def test_dry_run_and_roundtrip_same_snapshot(self):
        self.assertEqual(w.run(self.args)['widgets'], 6)
        self.assertFalse(self.args.output_root.exists())
        self.assertEqual(w.run(self.args), w.run(self.args))
        self.publish(); docs=self.docs()
        self.assertEqual([r['id'] for r in docs['announcements']['data']['items']], ['8','7'])
        self.assertEqual(docs['needs']['data']['items'], [{'id':'7','title':'First','detail':'Fixture · Review'}])
        self.assertEqual(docs['plans']['data']['checked'],1)
        self.assertEqual(docs['plans']['data']['items'][0]['owner'],'tester')
        detail=next(v for k,v in docs.items() if k.startswith('plan-'))
        self.assertEqual(detail['data']['rows'][0]['quote'],'Keep the fields\nFixture passed')
        self.assertEqual(docs['team']['shape'],'list')
        self.assertIn('liveness unknown',docs['team']['data']['rows'][0]['meta'])
        self.write('inbox.jsonl',[{'text':'announcement 7: seen'},{'text':'announcement 8: Thanks'}],True)
        self.publish(); docs=self.docs()
        self.assertEqual(docs['needs']['data']['items'],[])
        self.assertTrue(docs['announcements']['data']['items'][1]['seen'])
        self.assertFalse(docs['announcements']['data']['items'][0]['seen'])
    def test_no_change_retains_bytes_and_mtime(self):
        self.publish(); before={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in (self.root/'widgets/A0').glob('*.json')}
        self.assertEqual(self.publish()['changed'],0)
        self.assertEqual(before,{p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in (self.root/'widgets/A0').glob('*.json')})
    def test_bad_source_retains_every_last_good_file(self):
        self.publish(); before=self.docs(); (self.root/'plan.json').write_text('{broken')
        with self.assertRaises(ValueError):self.publish()
        self.assertEqual(before,self.docs())
    def test_collision_retains_foreign_file(self):
        self.publish(); path=self.root/'widgets/A0/needs.json'; path.write_text('{"producer":"other"}')
        with self.assertRaisesRegex(ValueError,'collision'):self.publish()
        self.assertEqual(path.read_text(),'{"producer":"other"}')
    def test_invalid_identity_duplicate_and_overflow_fail_before_write(self):
        for rows in [[{'id':'a: injected','title':'x','body':'y'}], [{'id':1,'title':'x','body':'y'}]*2]:
            self.write('ann.jsonl',rows,True)
            with self.assertRaises(ValueError):self.publish()
            self.assertFalse(self.args.output_root.exists())
    def test_missing_source_fails_before_write(self):
        (self.root/'ann.jsonl').unlink()
        with self.assertRaises(ValueError):self.publish()
        self.assertFalse(self.args.output_root.exists())
    def test_stale_managed_widget_requires_explicit_archive(self):
        self.publish(); manifest=json.loads((self.root/'manifest.json').read_text());manifest['plans']=[];self.write('manifest.json',manifest)
        with self.assertRaisesRegex(ValueError,'archive explicitly'):self.publish()
    def test_read_only_rollout_has_no_action_controls(self):
        self.args.read_only_actions=True;self.publish()
        self.assertTrue(all(d['actions']==[] for d in self.docs().values()))
    def test_source_hash_guard_rejects_stale_snapshot(self):
        _,guard=w.build(self.args.manifest);self.write('guard.json',guard);self.args.source_guard=self.root/'guard.json'
        self.publish();before=self.docs()
        self.write('inbox.jsonl',[{'text':'announcement 7: seen'}],True)
        with self.assertRaisesRegex(ValueError,'Source guard changed'):self.publish()
        self.assertEqual(before,self.docs())
    def test_existing_widget_capacity_and_writer_lock(self):
        self.publish()
        folder=self.root/'widgets/A0'
        with (folder.parent/'.a0-widgets-A0.lock').open('r+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError,'Another widget producer'):self.publish()
        for i in range(123):(folder/f'foreign-{i}.json').write_text('{"producer":"other"}')
        with self.assertRaisesRegex(ValueError,'128 widgets'):self.publish()
    def test_failed_replace_preserves_last_good_and_cleans_own_temps(self):
        self.publish(); before=self.docs()
        self.write('inbox.jsonl',[{'text':'announcement 7: seen'}],True)
        with patch.object(w.os,'replace',side_effect=OSError('fixture replace failure')):
            with self.assertRaises(OSError):self.publish()
        self.assertEqual(before,self.docs())
        self.assertEqual(list((self.root/'widgets/A0').glob('.a0-widgets-*')),[])
    def test_large_sources_partition_losslessly_by_bytes_and_rows(self):
        self.write('ann.jsonl',[{'id':i,'title':'x'*200,'body':'y'*4000} for i in range(128)],True)
        rows=[{'id':f'p{i}','title':f'Row {i}','status':'checked' if i%2 else 'moving'} for i in range(302)]
        self.write('plan.json',{'owner':'Fixture','project':'Large plan','items':rows})
        self.publish(); docs=self.docs()
        ann=[d for d in docs.values() if d['shape']=='announcements']
        self.assertGreater(len(ann),1)
        self.assertEqual({r['id'] for d in ann for r in d['data']['items']},{str(i) for i in range(128)})
        plans=[d for d in docs.values() if d['shape']=='progress']
        self.assertEqual(len(plans),3)
        self.assertEqual(sum(len(d['data']['items']) for d in plans),302)
        self.assertTrue(all(d['data']['total']==302 and d['data']['checked']==151 and d['data']['counts']['moving']==151 for d in plans))
        self.assertTrue(all(len(w.encode(d))<=w.LIMIT for d in docs.values()))
        self.assertTrue(all(len(d['data']['items'])<=128 for d in ann+plans))


if __name__=='__main__':unittest.main()
