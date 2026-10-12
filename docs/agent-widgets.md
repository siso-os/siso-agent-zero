# Agent Base widget producer

`bin/a0-widgets` turns an explicit operational snapshot into data-only widget files.
No discovery, task launch, inbox send, scheduler, or new task store is involved.
It defaults to a read-only validation receipt containing counts and hashes.

```sh
bin/a0-widgets --manifest /absolute/consumer/sources.json --output-root /absolute/consumer/widgets
bin/a0-widgets --manifest /absolute/consumer/sources.json --output-root /absolute/consumer/widgets --publish
```

The root is required; the producer appends `A0`. First exercise it under a
canonical disposable path. For an older live consumer without item-safe actions, use `--read-only-actions`
until the integrating owner deploys the reviewed item action handler. Rebuild
without that flag only after verifying the deployed contract.
A live root or inbox must be explicitly within the
current task's authorized scope. Never commit runtime snapshots or inbox data.

```json
{
  "announcements": "announcements.jsonl",
  "inbox": "receipts.jsonl",
  "plans": ["owner-plan.json"],
  "tasks": [{"id":"task-1","state":"STATE.json","log":"LOG.md"}],
  "issues": "issues.jsonl"
}
```

Paths are relative to the manifest or absolute. Announcements and inbox use the
existing board JSONL contracts. Plans use the existing owner `items` array, its
status, `to`, `his` and evidence fields. Tasks are explicit STATE/LOG pairs;
`log` and `issues` are optional. Empty plans/tasks are allowed. Missing declared
sources fail rather than looking empty. Only owned regular files through paths
without symlinks are accepted. Input files are bounded to 2 MiB.

Outputs include announcements, unseen needs, overall plan progress, a detail list
per plan, historical team task records, optional health, and machines. Historical
task state is labelled with liveness unknown. Machines reuse the server API.
Announcement project, time, needs and seen state survive. The legacy inbox
projection consumes exactly `announcement <id>: seen`; replies carry that same
item prefix without changing seen state. Replying with the literal word `seen`
therefore retains the legacy interpretation.

All source/schema checks and destination collisions are checked before writes.
Each widget is at most 256 KiB and 128 rows. Larger groups are partitioned into stable numbered widget files by row count and
byte size, with explicit page, page-count and total-row metadata. Progress pages
repeat the same full-source counts and total while each shows its own bounded
items. Original statuses are preserved, including statuses the legacy board
did not render. No rows are silently dropped. Input arrays are bounded to 10000
records and the existing agent protocol still limits the combined directory to
128 widget files.

File replacement is atomic, using private temporary files, fsync and rename.
Unchanged content preserves bytes and mtime. Initial timestamps derive from the
newest declared source mtime. For reviewed publication, pass `--source-guard` with
a JSON map of absolute source paths to SHA256 values, including the manifest.
A changed guard refuses publication. Sources are rehashed after staging and
before replacing any widget, so a concurrent source edit retains last-good output. Invalid sources retain all prior publications.
Filesystem failure during replacement can leave a mixed generation; it never
writes partial JSON. A per-agent nonblocking writer lock rejects concurrent publications. Another producer's file causes a
collision. A managed widget removed from the manifest must be explicitly archived
before publication; this command never removes its prior widget files.

## Notes adoption

Notes use Agent Base's existing `services/node/bin/ab-note.mjs` and private
`AB_A0_NOTES_ROOT`, independently of widgets. Do not append to its JSONL store.
Pass a JSON request through stdin to `ab-note.mjs apply`; read with `ab-note.mjs
list`. Create requires action, requestId, by, source and text (optional why).
Update/retire/restore require id and expectedRevision. Retry an unchanged payload
with the identical requestId; after a conflict, read again and use a new requestId.
A test can point AB_A0_NOTES_ROOT at a disposable canonical directory. Keep note
text out of shell arguments, command logs and result receipts.

## Migration acceptance and retirement

1. Run `heavy -- python3 -m unittest discover -s tests -p test_a0_widgets.py -v`.
2. In Agent Base, run `services/node/test/widgets-producer.mjs` through `heavy --
   node --experimental-strip-types` with A0_WIDGETS_CLI pointing here and
   A0_BOARD_FALLBACK pointing at the reviewed old board executable. The test copies
   the old generator and rebinds only runtime roots to its disposable snapshot;
   it never uses --post. It compares old/new IDs, counts, fields and action
   reclassification through a fake inbox. Run widget route and browser checks too.
3. Review and install only the Skills Hub `agent-widgets` capability into the
   intended consumer after an explicit installer dry-run. Verify the installed
   copy against canonical source; do not assume an active session reloaded it.
4. Bind an authorized operational snapshot to the manifest, dry-run, then publish
   to the selected widget root. Verify the actual Agent Base panel, two-second
   refresh, Seen/reply round-trip and current-source parity. Synthetic evidence
   does not prove live acceptance.
5. Identify the exact current posting owner and stop only that invocation after
   parity passes. The historical entry point is `bin-az/a0-board --post`, which
   refreshes `a0-tasks-card` and invokes console-post for `A0` / `a0-board`.
   Local launchd plist arguments and crontab on 2026-10-06 had no a0-board entry.
   That observation does not prove there is no remote or owner-loop posting.
   No fallback has been retired; retain its source and page for recovery.
