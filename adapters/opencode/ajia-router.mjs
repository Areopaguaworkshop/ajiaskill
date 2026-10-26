// Reference adapter for OpenCode V1 plugins.
// Copy to ~/.config/opencode/plugins/ajia-router.mjs and restart.
// V2 uses ctx.session.hook("context", ...) instead of chat.message + system.transform.
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const LOG = path.join(os.homedir(), ".ajia", "opencode-plugin.log");
function log(message) {
  try {
    fs.appendFileSync(LOG, `${new Date().toISOString()} ${message}\n`);
  } catch {
    // Ignore logging errors.
  }
}

const execFileAsync = promisify(execFile);
const pending = new Map();

async function route(message) {
  const { stdout } = await execFileAsync(
    process.env.AJIA_BIN || "ajia",
    ["route", message, "--json", "--host", "opencode"],
    { timeout: 2000, maxBuffer: 1024 * 1024 },
  );
  return JSON.parse(stdout);
}

export const AjiaRouter = async () => ({
  "chat.message": async (input, output) => {
    log(`chat.message session=${input.sessionID || "default"} parts=${(output.parts || []).length}`);
    const text = (output.parts || [])
      .filter((part) => part.type === "text")
      .map((part) => part.text)
      .join("\n");
    if (!text.trim()) return;
    try {
      const result = await route(text);
      log(`route decision=${result.decision} selected=${(result.selected || {}).id || "none"} body=${(result.body || "").length}`);
      if (result.decision === "inject" && result.body) {
        pending.set(input.sessionID || "default", result.body);
      }
    } catch {
      // Fail open.
    }
  },
  "experimental.chat.system.transform": async (input, output) => {
    const body = pending.get(input.sessionID || "default");
    log(`system.transform session=${input.sessionID || "default"} pending=${body ? body.length : 0}`);
    if (!body) return;
    pending.delete(input.sessionID || "default");
    output.system.push(body);
  },
});
