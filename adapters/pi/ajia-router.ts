// Reference adapter for Pi extensions.
// Copy to ~/.pi/agent/extensions/ajia-router.ts and run /reload.
export default function (pi: any) {
  pi.on("before_agent_start", async (event: any) => {
    if (event.messageType !== "user" || !event.prompt) return;
    try {
      const result = await pi.exec(
        process.env.AJIA_BIN || "ajia",
        ["route", event.prompt, "--json", "--host", "pi"],
        { timeout: 2000 },
      );
      const parsed = JSON.parse(result.stdout || "{}");
      if (parsed.decision !== "inject" || !parsed.body) return;
      return { systemPrompt: `${event.systemPrompt}\n\n${parsed.body}` };
    } catch {
      // Fail open.
      return;
    }
  });
}
