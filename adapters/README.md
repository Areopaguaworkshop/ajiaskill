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
`ctx.session.context`, asks the session model for a strict lesson via
`ctx.session.generate`, then runs `ajia review --host opencode`. Only a
proposed lesson pays for a second model call: the plugin asks for a skill plan
and runs `ajia learn --from-lesson <id> --host opencode`. Learn applies the
rubric, catalog dedup, patch cap, scan, and approval gates. The plugin calls
`ctx.skill.reload()` after a successful install. Memory files in
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
`ajia-hook --review --host pi`, which uses `pi -p` for both the lesson and the
authoring call. Review queues the lesson; learn writes the skill.

## OMP

Install with:

```bash
ajia setup omp-plugin --install
# reload extensions in OMP
```

`before_agent_start` injects the routed skill and memory. `agent_end` reviews
the finished session in the background through
`ajia-hook --review --host omp`, which uses `omp -p` for both the lesson and the
authoring call. Review queues the lesson; learn writes the skill.

## Codex

Install both hooks with:

```bash
ajia setup codex-hooks --install
```

Then run `/hooks` in Codex and trust the new definitions.

- `UserPromptSubmit` injects the routed skill and memory.
- `Stop` runs `ajia-hook --review --host codex` in the background. It reads
  `transcript_path`, asks `codex exec` for a strict lesson, calls `ajia review`
  to queue it, then asks `codex exec` for the skill plan and calls
  `ajia learn`.

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
  `transcript_path`, asks `claude -p --bare` for a strict lesson, calls
  `ajia review` to queue it, then asks `claude -p --bare` for the skill plan and
  calls `ajia learn`.

Claude has a 10,000-character cap. The hook truncates at 9,000 and points to
`ajia use <id> --json` for the full body. If Claude is not logged in, review
falls back to `AJIA_REVIEW_URL`; authoring falls back to `AJIA_LEARN_URL` and
then `AJIA_REVIEW_URL`. With neither, the hook fails open.

## Hermes

Hermes reads `~/.agents/skills` only as a git-root *project* root (and only
when that root is trusted), so add it as an external dir or MCP native-first
refusal will point at skills Hermes cannot see. Keep existing entries:

```yaml
skills:
  external_dirs:
    - /home/ajia/.local/share/omh/current/skills
    - ~/.agents/skills
```

Add a shell hook in `~/.hermes/config.yaml`:

```yaml
hooks:
  pre_llm_call:
    - command: "/home/ajia/Projects/ajiaskill/bin/ajia-hook --host hermes"
      timeout: 6
```

Hermes adds the returned context to the current user turn.
