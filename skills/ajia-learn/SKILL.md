---
name: ajia-learn
description: Use when a workflow or source should become a reusable skill; writes a cross-agent foundry candidate or captures a Hermes /learn skill, then indexes it for all hosts.
license: MIT
---

# ajia-learn

## Cross-agent foundry (default)

1. Inspect the source: a repo, a document, a URL, or the workflow just completed.
2. Write a candidate to `~/.ajia/foundry/<slug>/SKILL.md`:
   - `name` and `description` in frontmatter.
   - `license` when known.
   - Short instructions, verification, and references.
3. Run `ajia foundry sync`.
4. Run `ajia generated` to see the candidate.
5. Run `ajia use <id>`, `ajia scan <id>`, and `ajia promote <id> --dry-run`.

The candidate is visible to OpenCode, Pi, Codex, and every MCP host. It is not
installed until the user promotes it.

## Hermes `/learn`

`/learn` is an interactive command. `hermes -z` and `hermes chat -q` prune
`skill_manage`, so they cannot author skills.

- Run `ajia learn --execute` to drive an interactive Hermes session through a
  PTY. It is best-effort and may need an approval.
- Or run `hermes chat`, then `/learn <source>`, then `/exit`, then
  `ajia source sync hermes`.
- Hermes skills created by `learn` or `agent` are indexed with `generated_by`
  and `curator_state` from `~/.hermes/skills/.usage.json`.

## Rules

- Generated skills are candidates. Never auto-promote.
- Never copy a source skill into `.agents/skills`, `.claude/skills`, or a host
  root. That is installation. Use it in place, or promote it explicitly.
- Scan before promote; the normal gate applies.
- Redact secrets from the source before writing or learning.
- A trial or a foundry candidate is not an installation.
