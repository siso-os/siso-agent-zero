"""Idle-owner backstop; called by a0-review, never a separate scheduled job.

20 minutes leaves room for immediate follow-ups. At 100k tokens a future read costs
at least 2.5 fresh boots (20-40k). Overrides live beside compact-at.json:
idle-compact.json = {"default": {"idle_minutes": 20, "context_tokens": 100000},
                     "SEAT": {"idle_minutes": 40, "context_tokens": 150000}}.
Missing evidence holds a seat. Only metadata and final assistant text are read.
"""
import argparse
import datetime as dt
import fcntl
import importlib.machinery
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parents[1] / 'harness/bin'
sys.path.insert(0, str(HARNESS))
from a0_events import alive, emit, events_path, load

DB = Path.home() / '.local/state/siso-code/userdata/statev2.sqlite'
SEATS = Path.home() / '.local/state/agent-base/t3-seats.json'
POLICY = Path.home() / '.local/state/a0/idle-compact.json'
LIVE = ('queued', 'preparing', 'starting', 'running', 'waiting')
ZERO_NAMES = {'a0', 'agent zero', 'agent-zero', 'orchestrator', 'laptop orchestrator'}
REMOTE_HOSTS = {'mini': 'mini-fast'}
LOCAL_HOST = os.environ.get('A0_OWNER_HOST', 'laptop')
QUESTION = re.compile(r'\?|QUESTION FOR SHAAN:|\b(?:waiting (?:on|for) (?:you|shaan)|need your (?:input|decision|approval)|please (?:choose|confirm|decide))\b', re.I)


def fresh_module():
    loader = importlib.machinery.SourceFileLoader('owner_seat_fresh', str(HARNESS / 'seat-fresh-t3'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def stamp(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value / 1000 if value > 1e11 else value
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp() if value else 0


def checkpoint_paths(seat, cwd):
    home = Path(cwd).expanduser()
    # Existing owners keep their handoff; new monorepo checkpoints use seat state.
    root = next((p for p in (home, *home.parents) if (p / '.git').exists()), home)
    canonical = root / '.agents/agents' / re.sub(r'[^A-Za-z0-9_-]', '_', seat)
    if (root / '.siso').is_dir() and root.name == 'live':
        # Live source is read-only. Seat checkpoints belong to paired main state.
        canonical = root.parent / 'main/.agents/agents' / re.sub(r'[^A-Za-z0-9_-]', '_', seat)
        return canonical / 'HANDOFF.md', canonical / 'memory/MEMORY.md'
    if (canonical / 'HANDOFF.md').exists() or ((root / '.siso').is_dir() and not (home / '.agents/HANDOFF.md').exists()):
        return canonical / 'HANDOFF.md', canonical / 'memory/MEMORY.md'
    return home / '.agents/HANDOFF.md', home / '.agents/memory/MEMORY.md'


def history():
    try:
        with events_path().open() as src:
            return [json.loads(line) for line in src if line.strip()]
    except FileNotFoundError:
        return []


def thresholds(policy, seat):
    values = {'idle_minutes': 20, 'context_tokens': 100000}
    values.update(policy.get('default', {}))
    values.update(policy.get(seat, {}))
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 < v < float('inf') for v in values.values()):
        raise ValueError('invalid idle policy')
    return values


def select(row, limits, events, now):
    """Pure selection rule: unknown safety signals never authorize a rotation."""
    if row.get('zero'):
        return 'skip', 'Agent Zero is manually compacted'
    if row.get('error'):
        return 'skip', row['error']
    if row.get('active') or row.get('queued'):
        return 'skip', 'running or queued'
    if row.get('background') is not False:
        return 'skip', 'background job present or unobserved'
    if row.get('pending_input') is not False or QUESTION.search(row.get('said', '')):
        return 'skip', 'open question or pending input'
    if not row.get('completed') or not row.get('said'):
        return 'skip', 'no completed final turn'
    if now - row['completed'] < limits['idle_minutes'] * 60:
        return 'skip', 'recently active'
    if row.get('tokens') is None:
        return 'skip', 'context unobserved'
    if row['tokens'] < limits['context_tokens']:
        return 'skip', 'context below threshold'
    if row.get('checkpoint'):
        return 'fresh', 'idle, large context, fresh HANDOFF and memory'
    if any(e.get('source') == 'owner-idle' and e.get('thread') == row['thread'] and e.get('kind') == 'checkpoint-request' for e in events):
        return 'skip', 'checkpoint already requested for this conversation'
    return 'tell', 'idle, large context, checkpoint needed'


def own_background(native_ids):
    """Detached codex-run jobs retain their parent's native session in existing metadata."""
    if not native_ids:
        return False
    for path in (Path.home() / '.local/state/codex-run/runs').glob('*.meta.json'):
        try:
            job = json.loads(path.read_text())
            pid = int(job.get('pid') or 0)
            if job.get('parent_session') in native_ids and pid > 0:
                os.kill(pid, 0)
                return True
        except (OSError, ValueError, TypeError):
            continue
    return False


def snapshot(db, seat, entry):
    tid = entry.get('thread')
    row = {'seat': seat, 'thread': tid, 'zero': seat.casefold() in ZERO_NAMES or
           str((entry.get('env') or {}).get('SISO_A0', entry.get('SISO_A0', ''))) == '1'}
    if row['zero']:
        return row
    if entry.get('runsOn', 'laptop') != LOCAL_HOST:
        return {**row, 'error': 'remote host; run backstop on its host'}
    if not tid:
        return {**row, 'error': 'no mapped thread'}
    found = db.execute('select payload_json from orchestration_v2_projection_threads where thread_id=?', (tid,)).fetchone()
    if not found:
        return {**row, 'error': 'thread unobserved'}
    thread = json.loads(found[0])
    row['zero'] = thread.get('title', '').casefold() in ZERO_NAMES
    if thread.get('archivedAt') or thread.get('deletedAt'):
        return {**row, 'error': 'thread archived or deleted'}
    runs = db.execute('select status,requested_at,completed_at from orchestration_v2_projection_runs where thread_id=? order by ordinal desc', (tid,)).fetchall()
    row.update(active=any(r[0] in LIVE and r[0] != 'queued' for r in runs), queued=any(r[0] == 'queued' for r in runs))
    if not runs or runs[0][0] != 'completed':
        return {**row, 'error': 'last turn not completed'}
    row['completed'], row['started'] = stamp(runs[0][2]), stamp(runs[0][1])
    providers = [json.loads(r[0]) for r in db.execute('select payload_json from orchestration_v2_projection_provider_threads where thread_id=? order by updated_at desc', (tid,))]
    current = next((p for p in providers if p['id'] == thread.get('activeProviderThreadId')), None)
    row['background'] = any(p.get('pendingBackgroundTasks') for p in providers) if providers and all('pendingBackgroundTasks' in p for p in providers) else None
    native_ids = {(p.get('nativeThreadRef') or {}).get('nativeId') for p in providers} - {None}
    if own_background(native_ids):
        row['background'] = True
    row['active'] |= any(p.get('status') == 'active' for p in providers)
    row['tokens'] = (current.get('contextUsage') or {}).get('usedTokens') if current else None
    requests = db.execute('select payload_json from orchestration_v2_projection_runtime_requests where thread_id=?', (tid,)).fetchall()
    row['pending_input'] = any(json.loads(r[0]).get('status') in ('pending', 'open') for r in requests)
    msg = db.execute("select payload_json from orchestration_v2_projection_messages where thread_id=? and role='assistant' and streaming=0 order by created_at desc limit 1", (tid,)).fetchone()
    row['said'] = json.loads(msg[0]).get('text', '') if msg else ''
    project = db.execute('select workspace_root from projection_projects where project_id=?', (thread.get('projectId'),)).fetchone() if thread.get('projectId') else None
    cwd = thread.get('worktreePath') or (project[0] if project else None) or entry.get('cwd') or ''
    handoff, memory = checkpoint_paths(seat, cwd)
    row.update(handoff=str(handoff), memory=str(memory), checkpoint=False)
    # A checkpoint written DURING the last completed turn is newer than its input.
    # Both files must be nonempty and updated; a repo's old shared memory is insufficient.
    row['checkpoint'] = all(p.is_file() and p.stat().st_size and p.stat().st_mtime >= row['started'] for p in (handoff, memory))
    return row


def remote_snapshot(seat, entry):
    """Same bounded read-only query on the owner's host; no transcript content crosses SSH."""
    alias = REMOTE_HOSTS.get(entry.get('runsOn'))
    if not alias:
        return {'seat': seat, 'thread': entry.get('thread'), 'error': 'unknown remote host'}
    script = ('import json,sqlite3,re,os\nfrom pathlib import Path\nimport datetime as dt\n' +
              f'LIVE={LIVE!r}\nZERO_NAMES={ZERO_NAMES!r}\nLOCAL_HOST="laptop"\n' +
              '\n'.join(inspect.getsource(f) for f in (stamp, checkpoint_paths, own_background, snapshot)) +
              '\np=Path.home()/".local/state/siso-code/userdata/statev2.sqlite"\n' +
              'with sqlite3.connect(p.as_uri()+"?mode=ro",uri=True,timeout=5) as db:\n' +
              f' row=snapshot(db,{seat!r},{dict(entry, runsOn="laptop")!r})\n' +
              f' row["pending_input"]=row.get("pending_input",True) or bool(re.search({QUESTION.pattern!r}, row.get("said",""),re.I))\n' +
              ' row["said"]="Final message present" if row.get("said") else ""\n print(json.dumps(row))\n')
    try:
        result = subprocess.run(['ssh', '-o', 'RemoteCommand=none', '-o', 'RequestTTY=no', '-o', 'ConnectTimeout=5', alias,
                                 'python3 -'], input=script, capture_output=True, text=True, timeout=20, check=True)
        row = json.loads(result.stdout)
        row['remote'] = alias
        return row
    except (subprocess.SubprocessError, ValueError, OSError):
        return {'seat': seat, 'thread': entry.get('thread'), 'error': 'remote metadata unobserved'}


def rows(args):
    entries = json.loads(args.seats.read_text()) if args.seats.exists() else {}
    zero_threads = {e.get('thread') for name, e in entries.items() if name.casefold() in ZERO_NAMES or
                    str((e.get('env') or {}).get('SISO_A0', e.get('SISO_A0', ''))) == '1'}
    out = []
    with sqlite3.connect(args.db.resolve().as_uri() + '?mode=ro', uri=True, timeout=5) as db:
        for seat, entry in entries.items():
            if args.seat and seat != args.seat:
                continue
            try:
                row = remote_snapshot(seat, entry) if entry.get('runsOn', 'laptop') != LOCAL_HOST else snapshot(db, seat, entry)
                row['zero'] = row.get('zero') or bool(entry.get('thread') and entry['thread'] in zero_threads)
                out.append(row)
            except (OSError, ValueError, KeyError, sqlite3.Error):
                out.append({'seat': seat, 'thread': entry.get('thread'), 'error': 'metadata unobserved'})
    # Remaining hosted owners must have observable queue/background state too.
    for path in (Path.home() / '.local/state/agent-base/hosts').glob('w*_p*.json'):
        host = load(path)
        seat = host.get('name')
        if not seat or seat in entries or (args.seat and seat != args.seat) or not host.get('pid') or not alive(host['pid']):
            continue
        out.append({'seat': seat, 'thread': host.get('session'), 'zero': seat.casefold() in ZERO_NAMES or
                    str((host.get('env') or {}).get('SISO_A0', '')) == '1',
                    'error': 'host queue/background state unobserved; retained'})
    return out


def public(row, action, reason, now):
    return {k: v for k, v in dict(seat=row['seat'], thread=row.get('thread'), action=action, reason=reason,
            context_tokens=row.get('tokens'), idle_minutes=round((now-row['completed'])/60) if row.get('completed') else None).items()}


def summary():
    args = argparse.Namespace(db=DB, seats=SEATS, seat=None)
    now, events = time.time(), history()
    policy = json.loads(POLICY.read_text()) if POLICY.exists() else {}
    candidates = sum(select(r, thresholds(policy, r['seat']), events, now)[0] in ('tell', 'fresh') or
                     select(r, thresholds(policy, r['seat']), events, now)[1] == 'checkpoint already requested for this conversation' for r in rows(args))
    today = dt.datetime.now().astimezone().date()
    compacted = {e['who'] for e in events if e.get('source') == 'owner-idle' and e.get('kind') == 'fresh' and e.get('status') == 'done' and dt.datetime.fromtimestamp(stamp(e.get('at'))).date() == today}
    return f'Owners: {len(compacted)} compacted today · {candidates} idle and fat'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Act; default is a read-only dry run')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--seat')
    parser.add_argument('--db', type=Path, default=DB)
    parser.add_argument('--seats', type=Path, default=SEATS)
    parser.add_argument('--policy', type=Path, default=POLICY)
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error('choose --apply or --dry-run')
    policy = json.loads(args.policy.read_text()) if args.policy.exists() else {}
    events, now, failed = history(), time.time(), False
    for row in rows(args):
        action, reason = select(row, thresholds(policy, row['seat']), events, now)
        result = public(row, action, reason, now)
        if args.apply and action != 'skip' and row.get('remote'):
            # The host's existing live checkout must contain the landed backstop;
            # never install source or mutate a remote database from the laptop.
            command = 'env A0_OWNER_HOST=mini python3 ~/SISO_Workspace/_data/worktrees/siso/live/agents/zero/bin/owner-idle --apply --seat ' + __import__('shlex').quote(row['seat'])
            try:
                remote = subprocess.run(['ssh', '-o', 'RemoteCommand=none', '-o', 'RequestTTY=no', '-o', 'ConnectTimeout=5',
                                         row['remote'], command], capture_output=True, text=True, timeout=200, check=True)
                for line in remote.stdout.splitlines():
                    receipt = json.loads(line)
                    if receipt.get('action') in ('fresh', 'tell'):
                        emit(dict(id=f"owner-idle:{row['thread']}:{receipt['action']}", at=dt.datetime.now(dt.timezone.utc).isoformat(),
                                  source='owner-idle', kind='fresh' if receipt['action'] == 'fresh' else 'checkpoint-request',
                                  status='done', who=row['seat'], thread=row['thread'], context_before=row.get('tokens')))
                    print(line, flush=True)
                continue
            except (subprocess.SubprocessError, OSError):
                result.update(action='failed', reason='remote backstop unavailable; owner retained')
                failed = True
                emit(dict(id=f"owner-idle:{row['thread']}:remote-failed:{int(now)}", at=dt.datetime.now(dt.timezone.utc).isoformat(),
                          source='owner-idle', kind='remote-failed', status='blocked', who=row['seat'], thread=row['thread']))
                print(json.dumps(result), flush=True)
                continue
        if args.apply and action != 'skip':
            # Serialize checks/actions with other backstop runs using the existing seat-map lock.
            with open(str(args.seats) + '.idle.lock', 'a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                current = next((r for r in rows(args) if r['seat'] == row['seat']), {})
                if current.get('thread') != row['thread'] or select(current, thresholds(policy, row['seat']), history(), time.time())[0] != action:
                    result.update(action='skip', reason='state changed before action')
                else:
                    event = dict(id=f"owner-idle:{row['thread']}:{action}", at=dt.datetime.now(dt.timezone.utc).isoformat(),
                                 source='owner-idle', kind='checkpoint-request' if action == 'tell' else 'fresh',
                                 status='running', who=row['seat'], thread=row['thread'], context_before=row['tokens'])
                    if action == 'tell':
                        # Persist before sending: lost replies must never cause a second expensive wake.
                        emit(event)
                        message = (f"A0 idle checkpoint: task done and nothing waiting. Write/update {row['handoff']} and {row['memory']} "
                                   f"with done, next, open threads and paths. If any job or question remains, preserve it and stop. "
                                   f"Otherwise your LAST action is to arm a detached `seat-fresh {row['seat']!r}` after this turn. "
                                   "The backstop can finish the refresh from those files if needed. Do not restart services.")
                        rc = subprocess.run([sys.executable, str(HERE / 'a0-tell'), '--sync', '--expected-thread', row['thread'],
                                             '--request-id', event['id'], row['seat'], message], capture_output=True, timeout=90).returncode
                        result.update(action='tell' if rc == 0 else 'failed', reason='checkpoint requested once' if rc == 0 else f'a0-tell exit {rc}; request retained')
                    else:
                        command = [sys.executable, str(HARNESS / 'seat-fresh-t3'), row['seat'], '--db', str(args.db), '--seats', str(args.seats),
                                   '--idle-owner', '--policy', str(args.policy),
                                   '--handoff', row['handoff'], '--memory', row['memory'],
                                   '--note', f"Read {row['handoff']} and {row['memory']}. Work is checkpointed; remain idle when no next task is waiting."]
                        rc = subprocess.run(command, capture_output=True, timeout=180).returncode
                        if rc == 0:
                            event['status'] = 'done'
                            emit(event)
                        else:
                            emit({**event, 'id': event['id'] + f':failed:{int(now)}', 'kind': 'fresh-failed', 'status': 'blocked'})
                        result.update(action='fresh' if rc == 0 else 'failed', reason='seat-fresh completed' if rc == 0 else f'seat-fresh exit {rc}; old history retained')
        failed |= result['action'] == 'failed'
        print(json.dumps(result), flush=True)
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
