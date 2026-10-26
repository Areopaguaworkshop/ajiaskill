# Host adapters

These are **reference-only** hook adapters. They are **not installed**. MCP is
the default trigger. Keep this directory for a future deterministic mode.

| Host | Status | Note |
|---|---|---|
| Pi | not installed | Reference extension only. |
| Hermes | not installed | Reference shell hook only. |
| Codex | not installed | Reference hook; trust via `/hooks` if enabled. |
| OMP | not installed | Reference extension only. |
| Claude | not installed | Reference hook; 10K context cap if enabled. |
| OpenCode | not installed | Blocked by local plugin/schema migration; MCP only. |

All adapters call:

```bash
ajia route "<user message>" --json --host <host>
```

They fail open: a timeout, error, low confidence, or empty body injects
nothing.

## OpenCode

MCP only on this machine. OpenCode 2.1.4 reported plugin and schema migration
failures when the hook was tested. Do not enable the adapter until that is
fixed. The reference V1 adapter is in `opencode/ajia-router.mjs`; a V2 adapter
using `ctx.session.hook("context", ...)` is the future attempt.

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
            "timeout": 3,
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
      timeout: 3
```

Hermes adds the returned context to the current user turn.
