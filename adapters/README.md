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

Copy `pi/ajia-router.ts` to `~/.pi/agent/extensions/`, then run `/reload`.
The adapter appends the selected body to the system prompt.

## OMP

Copy `omp/ajia-router.ts` to `~/.omp/agent/extensions/`, then run
`/reload-plugins`. The adapter appends the selected body to the system prompt.

## Codex

Add a `UserPromptSubmit` hook in `~/.codex/hooks.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/ajiap/project/ajiaskill/bin/ajia-hook --host codex",
            "timeout": 6,
            "additionalContextLimit": 0
          }
        ]
      }
    ]
  }
}
```

`additionalContextLimit: 0` is required for a full skill body.

## Claude Code

Add a `UserPromptSubmit` hook in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/ajiap/project/ajiaskill/bin/ajia-hook --host claude",
            "timeout": 3
          }
        ]
      }
    ]
  }
}
```

Claude has a 10,000-character cap. The hook truncates at 9,000 and points to
`ajia use <id> --json` for the full body.

## Hermes

Add a shell hook in `~/.hermes/config.yaml`:

```yaml
hooks:
  pre_llm_call:
    - command: "/home/ajiap/project/ajiaskill/bin/ajia-hook --host hermes"
      timeout: 6
```

Hermes adds the returned context to the current user turn.
