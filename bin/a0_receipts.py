"""Correlate existing dispatches and owner returns; no additional ledger."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'harness/bin'))
from a0_events import emit


def stamp(value):
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return dt.datetime.fromisoformat(str(value).replace('Z', '+00:00')).timestamp()
    except (ValueError, TypeError):
        return 0


def dispatch_path():
    return Path(os.environ.get('A0_DISPATCH_FILE', str(Path.home() / '.local/state/a0/dispatch.jsonl')))


def dispatches(path=None):
    path = Path(path) if path else dispatch_path()
    if not path.is_file():
        return []
    result = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                row = {'parse_error': True}
        except ValueError:
            row = {'parse_error': True}
        # Hash the existing record, including its position: repeated sends remain distinct.
        ident = hashlib.sha256((str(number) + ':' + line).encode()).hexdigest()[:20]
        tasks = sorted(set(re.findall(r'\bt-\d{4,}\b', str(row.get('task') or '') + ' ' + str(row.get('brief') or ''))))
        result.append({**{k: row.get(k) for k in ('at', 'kind', 'name', 'thread', 'parent', 'machine', 'model')},
                       'id': 'dispatch:' + ident, 'tasks': tasks, 'parse_error': bool(row.get('parse_error'))})
    return result


def owner_receipt(dispatch, row, status, reason=''):
    """Metadata-only receipt: raw seat messages and prompts never enter the ledger."""
    correlation = dispatch['id'] if dispatch else f"{row.get('thread')}:{row.get('run')}"
    event = {'id': f'owner-return:{correlation}:{status}',
             'at': dt.datetime.now(dt.timezone.utc).isoformat(), 'source': 'a0-await',
             'kind': status, 'status': status, 'dispatch': dispatch['id'] if dispatch else None,
             'who': row.get('seat') or (dispatch or {}).get('name'),
             'thread': row.get('thread'), 'owner_run': row.get('run'),
             'tasks': (dispatch or {}).get('tasks', []), 'reason': reason,
             'return': f'Owner {status}; thread={row.get("thread")} run={row.get("run")}; {reason}'}
    # The event writer mirrors attributed events into the canonical task sidecar.
    event['task'] = event['tasks'][0] if event['tasks'] else None
    emit(event)
    return event
