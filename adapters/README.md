# Host adapters

The `ajia-router` files are **reference-only** pre-turn adapters. They are
**not installed**. MCP is the default trigger. The OpenCode autolearn plugin is
the first installable adapter; the rest remain references.

| Host | Status | Note |
|---|---|---|
| Pi | not installed | Reference extension only. |
| Hermes | not installed | Reference shell hook only. |
| Codex | not installed | Reference hook; trust via `/hooks` if enabled. |
| OMP | not installed | Reference extension only. |
| Claude | not installed | Reference hook; 10K context cap if enabled. |
| OpenCode | **V2 autolearn plugin available** | Install with `ajia setup opencode-plugin --install`. |

All adapters call:

```bash
ajia route "<user message>" --json --host <host>
```

They fail open: a timeout, error, low confidence, or empty body injects
nothing.

Re-running an `--install` command updates its own hook entry or symlink in
place when the install path or version changes, so an upgrade does not leave a
duplicate hook running every turn.

## OpenCode

The V1 `opencode/ajia-router.mjs` reference remains blocked by the OpenCode 2.x
plugin migration. Do not enable it.

The V2 autolearn plugin lives in `opencode/ajia-learn/`. Install it explicitly:

```bash
ajia setup opencode-plugin --install
# restart OpenCode
```

It listens for `session.execution.succeeded`, reads the transcript with
`ctx.session.context`, asks the session model for a strict review plan via
`ctx.session.generate`, then runs `ajia review --host opencode`. Learned skills
are scanned, quarantined or installed by the engine, and the plugin calls
`ctx.skill.reload()` so OpenCode sees them. Memory files in
`~/.ajia/memory/USER.md` and `~/.ajia/memory/projects/` are injected through the
`context` hook.

Disable with `ajia learning pause`; remove the symlink and restart OpenCode to
uninstall the plugin.

## Pi

Install with:

```bash
ajia setup pi-plugin --install
# reload extensions in Pi
```

`before_agent_start` injects the routed skill and memory. `agent_settled`
reviews the finished session in the background through
`ajia-hook --review --host pi`, which uses `pi -p` as the review model.

## OMP

Install with:

```bash
ajia setup omp-plugin --install
# reload extensions in OMP
```

`before_agent_start` injects the routed skill and memory. `agent_end` reviews
the finished session in the background through
`ajia-hook --review --host omp`, which uses `omp -p` as the review model.

## Codex

Install both hooks with:

```bash
ajia setup codex-hooks --install
```

Then run `/hooks` in Codex and trust the new definitions.

- `UserPromptSubmit` injects the routed skill and memory.
- `Stop` runs `ajia-hook --review --host codex` in the background. It reads
  `transcript_path`, asks `codex exec` for a strict review plan, then calls
  `ajia review`.

Set `additionalContextLimit: 0` if you want the full skill body rather than
Codex's preview.

## Claude Code

Install both hooks with:

```bash
ajia setup claude-hooks --install
# restart Claude Code
```

- `UserPromptSubmit` injects the routed skill and memory.
- `Stop` runs `ajia-hook --review --host claude` in the background. It reads
  `transcript_path`, asks `claude -p --bare` for a strict review plan, then
  calls `ajia review`.

Claude has a 10,000-character cap. The hook truncates at 9,000 and points to
`ajia use <id> --json` for the full body. If Claude is not logged in, the
review falls back to `AJIA_REVIEW_URL`; with neither, it fails open.

## Hermes

Add a shell hook in `~/.hermes/config.yaml`:

```yaml
hooks:
  pre_llm_call:
    - command: "/home/ajiap/project/ajiaskill/bin/ajia-hook --host hermes"
      timeout: 6
```

Hermes adds the returned context to the current user turn.
