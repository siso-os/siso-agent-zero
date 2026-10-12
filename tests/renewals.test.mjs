// renewals: a Codex plan read from a fake login; warn puts one line on his dashboard at 4 days left, never twice, and sends no notice for the same day-count.
import { test } from "node:test";
import assert from "node:assert";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, chmodSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const bin = fileURLToPath(new URL("../bin/renewals", import.meta.url));

function home(daysAhead) {
  const h = mkdtempSync(path.join(tmpdir(), "renewals-"));
  mkdirSync(path.join(h, ".codex"));
  mkdirSync(path.join(h, "bin"));
  const until = new Date(Date.now() + daysAhead * 86400e3);
  until.setHours(12, 0, 0, 0); // midday local, so the local calendar day count is exactly daysAhead
  const claims = { "https://api.openai.com/auth": { chatgpt_plan_type: "pro", chatgpt_subscription_active_until: until.toISOString().replace("Z", "+00:00") } };
  const jwt = ["x", Buffer.from(JSON.stringify(claims)).toString("base64url"), "y"].join(".");
  writeFileSync(path.join(h, ".codex/auth.json"), JSON.stringify({ tokens: { id_token: jwt } }));
  writeFileSync(path.join(h, "conf.json"), JSON.stringify({ plans: [{ name: "codex", kind: "codex", what: "ChatGPT Pro" }] }));
  for (const tool of ["siso-az", "notice"]) {
    writeFileSync(path.join(h, "bin", tool), `#!/bin/sh\necho "${tool} $*" >> "${h}/calls.log"\n`);
    chmodSync(path.join(h, "bin", tool), 0o755);
  }
  const env = { ...process.env, HOME: h, PATH: `${h}/bin:${process.env.PATH}`, RENEWALS_CONF: path.join(h, "conf.json"), RENEWALS_STATE: path.join(h, "state") };
  return { h, env };
}

test("4 days out: one dashboard line, no notice, not repeated on a second run", () => {
  const { h, env } = home(4);
  const a = spawnSync(bin, ["warn"], { env, encoding: "utf8" });
  assert.match(a.stdout, /codex\s+active\s+renews .*\(4 days\)/);
  assert.match(a.stdout, /warned: codex \(ChatGPT Pro\) renews in 4 days/);
  spawnSync(bin, ["warn"], { env, encoding: "utf8" });
  const calls = readFileSync(path.join(h, "calls.log"), "utf8").trim().split("\n");
  assert.strictEqual(calls.filter((c) => c.startsWith("siso-az need")).length, 1);
  assert.strictEqual(calls.filter((c) => c.startsWith("notice")).length, 0, "no notices: the dashboard line is the state");
});

test("10 days out: no warning; JSON carries days_left", () => {
  const { env } = home(10);
  assert.match(spawnSync(bin, ["warn"], { env, encoding: "utf8" }).stdout, /nothing to warn about/);
  const rows = JSON.parse(spawnSync(bin, ["--json"], { env, encoding: "utf8" }).stdout);
  assert.strictEqual(rows[0].days_left, 10);
});
