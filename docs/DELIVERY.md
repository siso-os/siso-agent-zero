# Delivery facts on the existing ledger

`a0-task set <id> done_check='...' delivery.<field>=<value>` attaches facts to
the existing task JSON. An empty value clears a fact to `null`. No database or
second task store is involved. Existing task fields and stages retain their meaning.

A goal is an open task with a target time: `a0-task set <id> due=2026-10-23T20:05+07:00
done_check='...'` (ISO time with a zone; `due=` clears it). SISO Code's Tasks tab lists
open goals soonest first, with the definition of done, on Agent Zero's thread and its owner's.

`a0-task resolve <id>` prints the delivery record and its explicit `missing`
fields. `delivery.module_id` resolves through the monorepo catalog, including
Git metadata outside a sparse checkout. For an external source, pass
`--module /path/to/its/module.json`; that file is read only and stays in its repo.
Module identity must agree. Both SISO's `id` and HALO's `name` are supported.

Fields: `module_id`, `source_authority`, `task_authority`, `task_id`, `run_id`,
`tested_commit`, `landed_commit`, `running_commit`, `target`,
`writable_state_home`, `evidence_link`, `observed_at`, `observed_result`.
Only authority, target and writable-home defaults come from module metadata.
`$A0_DATA_HOME` resolves through the existing writable-home selector.

HALO's canonical task ID is its full GitHub issue URL, even when an existing
A0 task already references the work. Keep GitHub Issues as its task authority;
do not import HALO source or create another HALO backlog. A0's local ID remains
`record_id` in the generated resolution. Existing task projections are retained.

Record tested, landed and running commits separately. Health or a closed issue
does not establish feature behavior or commit ancestry. Absent observations stay
null; record time and evidence with each actual observation. `resolve` never
changes state, starts a run, installs a release or infers success from prose.
`a0-task index` exposes `delivery` and `done_check` in the existing A0 plan view
for dispatcher readers. Step 2 owns executing checks and assigning work.

Contract check: `python3 -B agents/zero/tests/a0-task.test.py`.
