// stack-doctor reads live state, so this checks its contract: valid JSON, every check family present, exit code = any red.
import { test } from "node:test";
import assert from "node:assert";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
const bin = fileURLToPath(new URL("../bin/stack-doctor", import.meta.url));

test("stack-doctor --json: rows with level/check/msg, all families, exit 1 iff a red", () => {
  const r = spawnSync(bin, ["--json", "--hours", "1"], { encoding: "utf8", timeout: 120000 });
  const rows = JSON.parse(r.stdout);
  assert.ok(rows.length >= 8);
  for (const x of rows) assert.ok(["red", "amber", "green"].includes(x.level) && x.check && x.msg, JSON.stringify(x));
  const names = new Set(rows.map((x) => x.check));
  for (const n of ["claude-agents", "claude-model", "codex-config", "codex-cap", "ab-queue", "laptop-disk", "backup"]) assert.ok(names.has(n), n);
  assert.strictEqual(r.status, rows.some((x) => x.level === "red") ? 1 : 0);
  assert.ok(!rows.some((x) => /check crashed/.test(x.msg)), "no check crashed");
});
