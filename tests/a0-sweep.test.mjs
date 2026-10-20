// a0-sweep: from a saved shell snapshot it picks only finished, quiet, unpinned subagent threads; seats, forks, busy and
// recent helpers stay.
import { test } from "node:test";
import assert from "node:assert";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const bin = fileURLToPath(new URL("../bin/a0-sweep", import.meta.url));

const old = new Date(Date.now() - 3 * 3600e3).toISOString();
const fresh = new Date(Date.now() - 5 * 60e3).toISOString();
const sub = { relationshipToParent: "subagent", parentThreadId: "seat" };
const t = (id, o = {}) => ({ id, projectId: o.projectId ?? "p1", title: id, status: "idle", updatedAt: old, lineage: sub, ...o });
const snapshot = { snapshot: { projects: [{ id: "p1", title: "HALO" }, { id: "p2", title: "UI-HUB" }], threads: [
  t("done-old"), t("completed-old", { status: "completed" }), t("other-project", { projectId: "p2" }),
  t("seat", { lineage: null }), t("fork", { lineage: { relationshipToParent: "fork" } }),
  t("running", { status: "running" }), t("recent", { updatedAt: fresh }), t("pinned", { pinnedAt: old }),
  t("waiting", { pendingRuntimeRequest: { kind: "approval" } }), t("bg", { pendingBackgroundTasks: [{ taskId: "x" }] }),
  t("archived", { archivedAt: old }),
] } };

function runSnapshot(input, ...args) {
  const home = mkdtempSync(path.join(tmpdir(), "a0-sweep-home-"));
  mkdirSync(path.join(home, ".local/state/agent-base"), { recursive: true });
  writeFileSync(path.join(home, ".local/state/agent-base/t3-seats.json"), JSON.stringify({
    primary: { thread: "seat" }, nested: { seats: [{ threadId: "seat-id" }] },
  }));
  const f = path.join(mkdtempSync(path.join(tmpdir(), "a0-sweep-")), "shell.json");
  writeFileSync(f, JSON.stringify(input));
  const r = spawnSync("node", [bin, "--plan-from", f, ...args], { encoding: "utf8", env: { ...process.env, HOME: home } });
  assert.strictEqual(r.status, 0, r.stderr);
  return r.stdout.trim().split("\n");
}

const run = (...args) => runSnapshot(snapshot, ...args);

test("picks finished quiet helpers only", () => {
  const out = run();
  const ids = out.slice(0, -1).map(l => l.split("\t")[2]).sort();
  assert.deepStrictEqual(ids, ["completed-old", "done-old", "other-project"]);
  assert.match(out.at(-1), /^would archive 3 of 8 helper threads: HALO 2, UI-HUB 1$/);
});

test("--project and --age narrow it", () => {
  assert.match(run("--project", "ui-hub").at(-1), /would archive 1 of 8.*UI-HUB 1/);
  assert.match(run("--age", "1").at(-1), /would archive 4 of 8/);
});


test("--top-hours includes quiet top-level threads and preserves all automatic guards", () => {
  const input = { ...snapshot.snapshot, threads: [
    t("quiet-top", { lineage: null }), t("seat", { lineage: null }), t("seat-id", { lineage: null }),
    t("pinned-top", { lineage: null, pinnedAt: old }), t("fork", { lineage: { relationshipToParent: "fork" } }),
    t("other-lineage", { lineage: { parentThreadId: "x" } }),
    t("busy-top", { lineage: null, activityRunStatus: "queued" }),
    t("waiting-top", { lineage: null, pendingRuntimeRequest: {} }),
    t("background-top", { lineage: null, pendingBackgroundTasks: [{}] }),
    t("recent-top", { lineage: null, updatedAt: fresh }),
  ] };
  const out = runSnapshot(input, "--top-hours", "2");
  assert.deepStrictEqual(out.slice(0, -1).map(l => l.split("\t")[2]), ["quiet-top"]);
  assert.match(runSnapshot(input, "--top-hours", "4").at(-1), /would archive 0/);
  assert.match(runSnapshot(input, "--top-hours", "2", "--project", "UI-HUB").at(-1), /would archive 0/);
});

test("--ids selects exactly the named open ids without adding default helpers", () => {
  const out = run("--ids", "pinned,recent,pinned,archived,missing");
  assert.deepStrictEqual(out.slice(0, -1).map(l => l.split("\t")[2]).sort(), ["pinned", "recent"]);
  assert.match(run("--ids", "").at(-1), /would archive 0/);
});

test("--save writes the unwrapped snapshot in offline mode", () => {
  const file = path.join(mkdtempSync(path.join(tmpdir(), "a0-sweep-save-")), "snapshot.json");
  run("--save", file);
  assert.deepStrictEqual(JSON.parse(readFileSync(file, "utf8")), snapshot.snapshot);
});

test("--pinned-helpers-hours includes only quiet pinned subagents with automatic guards", () => {
  const input = { ...snapshot.snapshot, threads: [
    t("pinned", { pinnedAt: old }), t("recent-pinned", { pinnedAt: old, updatedAt: fresh }),
    t("busy-pinned", { pinnedAt: old, status: "running" }),
    t("waiting-pinned", { pinnedAt: old, pendingRuntimeRequest: {} }),
    t("background-pinned", { pinnedAt: old, pendingBackgroundTasks: [{}] }),
    t("seat-id", { pinnedAt: old }), t("top-pinned", { pinnedAt: old, lineage: null }),
    t("fork-pinned", { pinnedAt: old, lineage: { relationshipToParent: "fork" } }),
    t("deleted-pinned", { pinnedAt: old, deletedAt: old }),
  ] };
  const out = runSnapshot(input, "--pinned-helpers-hours", "2");
  assert.deepStrictEqual(out.slice(0, -1).map(l => l.split("\t")[2]), ["pinned"]);
  assert.match(runSnapshot(input, "--pinned-helpers-hours", "4").at(-1), /would archive 0/);
  assert.match(runSnapshot(input, "--pinned-helpers-hours", "2", "--project", "UI-HUB").at(-1), /would archive 0/);
});

test("--help prints the entire header including every new flag and final log line", () => {
  const r = spawnSync("node", [bin, "--help"], { encoding: "utf8" });
  assert.strictEqual(r.status, 0, r.stderr);
  for (const flag of ["--top-hours", "--ids", "--save", "--pinned-helpers-hours"]) assert.ok(r.stdout.includes(flag));
  assert.match(r.stdout, /a0-sweep\.jsonl/);
  assert.ok(!r.stdout.includes("import "));
});
