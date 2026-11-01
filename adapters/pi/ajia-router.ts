// Pi adapter: inject the routed skill and memory before a turn, and review the
// finished session in the background. Copy to ~/.pi/agent/extensions/ajia-router.ts
// and run /reload, or install with `ajia setup pi-plugin --install`.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HOST = "pi";
const REVIEW_COOLDOWN_MS = Number(process.env.AJIA_PLUGIN_COOLDOWN_MS || 60000);
const REVIEW_DELAY_MS = Number(process.env.AJIA_REVIEW_DELAY_MS || 2000);

function ajiaBin(): string {
  if (process.env.AJIA_BIN) return process.env.AJIA_BIN;
  try {
    const here = path.dirname(fs.realpathSync(fileURLToPath(import.meta.url)));
    const candidate = path.resolve(here, "../..", "bin", "ajia");
    if (fs.existsSync(candidate)) return candidate;
  } catch {
    // Fall through to PATH.
  }
  return "ajia";
}

function hookPath(): string {
  if (process.env.AJIA_HOOK) return process.env.AJIA_HOOK;
  const ajia = ajiaBin();
  return path.isAbsolute(ajia) ? path.join(path.dirname(ajia), "ajia-hook") : "ajia-hook";
}

function scheduleReview(last: { at: number; timer: ReturnType<typeof setTimeout> | undefined }, ctx: any): void {
  const sessionFile = ctx?.sessionManager?.getSessionFile?.();
  if (!sessionFile) return;
  if (last.timer) clearTimeout(last.timer);
  last.timer = setTimeout(() => {
    if (Date.now() - last.at < REVIEW_COOLDOWN_MS) return;
    last.at = Date.now();
    try {
      const child = spawn(process.env.AJIA_PYTHON || "python3", [hookPath(), "--review", "--host", HOST], {
        detached: true,
        stdio: ["pipe", "ignore", "ignore"],
        env: { ...process.env },
      });
      child.stdin?.end(
        JSON.stringify({
          transcript_path: sessionFile,
          cwd: ctx?.cwd,
          stop_hook_active: false,
        }),
      );
      child.unref();
    } catch {
      // Fail open; the turn is never blocked.
    }
  }, REVIEW_DELAY_MS);
}

export default function (pi: any) {
  const last = { at: 0, timer: undefined as ReturnType<typeof setTimeout> | undefined };
  let currentCtx: any;
  pi.on("session_start", (_event: any, ctx: any) => {
    currentCtx = ctx;
  });
  pi.on("agent_settled", (_event: any, ctx: any) => scheduleReview(last, ctx || currentCtx));
  pi.on("agent_end", (_event: any, ctx: any) => scheduleReview(last, ctx || currentCtx));

  pi.on("before_agent_start", async (event: any, ctx: any) => {
    if (event.messageType !== "user" || !event.prompt) return;
    let body = "";
    try {
      const result = await pi.exec(
        ajiaBin(),
        ["route", event.prompt, "--json", "--host", HOST],
        { timeout: 5000 },
      );
      const parsed = JSON.parse(result.stdout || "{}");
      if (parsed.decision === "inject" && parsed.body) body = parsed.body;
    } catch {
      // Fail open.
    }
    try {
      const result = await pi.exec(
        ajiaBin(),
        ["memory", "context", "--cwd", ctx?.cwd || process.cwd(), "--json"],
        { timeout: 3000 },
      );
      const memory = JSON.parse(result.stdout || "{}").text;
      if (memory) {
        body = (body ? `${body}\n\n` : "") + `## ajiaskill memory\n${memory}`;
      }
    } catch {
      // Memory is optional.
    }
    if (!body) return;
    return { systemPrompt: `${event.systemPrompt}\n\n${body}` };
  });
}
