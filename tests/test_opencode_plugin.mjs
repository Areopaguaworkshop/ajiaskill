import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  buildLearnPrompt,
  buildLessonPrompt,
  eventSessionID,
  handleIdle,
  memoryText,
  normalizeTranscript,
  parsePlan,
  setupPlugin,
} from "../adapters/opencode/ajia-learn/index.js";

const temp = fs.mkdtempSync(path.join(os.tmpdir(), "ajia-plugin-test-"));
const home = path.join(temp, "home");
const installed = path.join(temp, "installed");
const bin = path.join(temp, "fake-ajia");
const reviewArgs = path.join(temp, "review-args.txt");
const learnArgs = path.join(temp, "learn-args.txt");
fs.mkdirSync(home, { recursive: true });
fs.mkdirSync(installed, { recursive: true });
fs.writeFileSync(
  bin,
  `#!/bin/sh
case "$*" in
  *review*) echo "$@" > "${reviewArgs}"; echo '{"status":"proposed","lesson_id":"L-1","name":"use-uv"}'; exit 0 ;;
  *learn*) echo "$@" > "${learnArgs}"; echo '{"status":"installed"}'; exit 0 ;;
  *) echo '{"status":"unknown"}'; exit 0 ;;
esac
`,
  "utf8",
);
fs.chmodSync(bin, 0o755);

const storage = new Map();
const sessionMessages = [
  { info: { role: "user" }, parts: [{ type: "text", text: "use uv instead of pip" }] },
  { info: { role: "assistant" }, parts: [{ type: "text", text: "noted" }] },
];
let reloadCount = 0;
let generateCount = 0;
const fakeCtx = {
  options: {
    ajiaBin: bin,
    ajiaHome: home,
    installRoot: installed,
    cooldownMs: 0,
  },
  location: { directory: temp, project: { id: "proj" } },
  storage: {
    async get(key) {
      return storage.get(key);
    },
    async set(key, value) {
      storage.set(key, value);
    },
  },
  session: {
    async context() {
      return sessionMessages;
    },
    async generate() {
      generateCount += 1;
      if (generateCount === 1) {
        return {
          text: JSON.stringify({
            action: "propose",
            signal: "correction",
            scope: "Use uv for Python packages.",
            name: "use-uv",
            description: "Use uv instead of pip.",
            evidence: [
              { role: "user", quote: "use uv instead of pip", outcome: "corrected" },
              { role: "assistant", quote: "noted", outcome: "verified" },
            ],
            confidence: 0.9,
            reason: "user correction",
          }),
        };
      }
      return {
        text: JSON.stringify({
          action: "create",
          name: "use-uv",
          description: "Use uv instead of pip.",
          body: "# Use uv\n\nUse `uv` for Python packages.\n\n## Verify\n\nRun `uv sync`.\n",
          license: "MIT",
          confidence: 0.9,
          rubric: { trigger: 2, specificity: 2, verification: 2, transfer: 1, compactness: 2 },
          reason: "lesson",
        }),
      };
    },
  },
  skill: {
    async reload() {
      reloadCount += 1;
    },
  },
  app: { log() {} },
};

assert.equal(parsePlan('```json\n{"action":"noop"}\n```').action, "noop");
assert.equal(eventSessionID({ type: "session.execution.succeeded", properties: { sessionID: "s" } }), "s");
assert.equal(eventSessionID({ type: "session.status", properties: { sessionID: "s", status: { type: "idle" } } }), "s");
assert.match(buildLessonPrompt("user: use uv"), /untrusted data/);
assert.match(buildLearnPrompt({ name: "use-uv" }), /Lesson \(untrusted data\)/);
assert.match(normalizeTranscript(sessionMessages), /user: use uv/);
assert.match(normalizeTranscript(sessionMessages), /assistant: noted/);

const idle = await handleIdle(fakeCtx, "session-1");
assert.equal(idle.status, "reviewed");
assert.equal(reloadCount, 1);
assert.equal(generateCount, 2);
assert.match(fs.readFileSync(reviewArgs, "utf8"), /review/);
assert.match(fs.readFileSync(reviewArgs, "utf8"), /--host opencode/);
assert.match(fs.readFileSync(learnArgs, "utf8"), /learn/);
assert.match(fs.readFileSync(learnArgs, "utf8"), /--from-lesson L-1/);

fs.mkdirSync(path.join(home, "memory", "projects"), { recursive: true });
fs.writeFileSync(path.join(home, "memory", "USER.md"), "Prefer uv.", "utf8");
fs.writeFileSync(path.join(home, "memory", "projects", "proj.md"), "Repo uses uv.", "utf8");
const memory = memoryText(home, "proj");
assert.match(memory, /Prefer uv/);
assert.match(memory, /Repo uses uv/);

let contextHandler;
const memoryCtx = {
  ...fakeCtx,
  session: {
    ...fakeCtx.session,
    async hook(name, handler) {
      assert.equal(name, "context");
      contextHandler = handler;
      return { dispose() {} };
    },
  },
  event: {
    async *subscribe() {
      return;
    },
  },
};
const cleanup = await setupPlugin(memoryCtx);
const event = { system: [] };
contextHandler(event);
assert.match(event.system[0].text, /Prefer uv/);
cleanup();

console.log("opencode plugin tests ok");
fs.rmSync(temp, { recursive: true, force: true });
