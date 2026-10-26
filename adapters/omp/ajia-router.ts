// Reference adapter for OMP extensions.
// Copy to ~/.omp/agent/extensions/ajia-router.ts and run /reload-plugins.
export default function (pi: any) {
  pi.on("before_agent_start", async (event: any) => {
    if (event.reason === "revive" || !event.prompt) return;
    try {
      const result = await pi.exec(
        process.env.AJIA_BIN || "ajia",
        ["route", event.prompt, "--json", "--host", "omp"],
        { timeout: 2000 },
      );
      const parsed = JSON.parse(result.stdout || "{}");
      if (parsed.decision !== "inject" || !parsed.body) return;
      return { systemPrompt: [...event.systemPrompt, parsed.body] };
    } catch {
      // Fail open.
      return;
    }
  });
}
