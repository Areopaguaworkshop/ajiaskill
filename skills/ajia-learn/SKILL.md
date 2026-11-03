---
name: ajia-learn
description: Use when a workflow or source should become a reusable skill; author a review lesson with a rubric and catalog dedup, write a cross-agent foundry candidate, or capture a Hermes /learn skill.
license: MIT
---

# ajia-learn

## Review lessons (default)

`ajia review` is the detector. It queues an evidence-backed lesson and never
writes a `SKILL.md`. `ajia learn` is the only author.

1. List proposed lessons with `ajia learn --queue`.
2. Author one with `ajia learn --from-lesson <id> --plan <skill.json>`, or let
   `ajia learn --from-lesson <id>` call `AJIA_LEARN_URL`.
3. Check the result with `ajia learn --audit` and `ajia learning status`.
4. Quarantined or pending skills need `ajia learning quarantine release`,
   `ajia learning approve`, or `ajia learning reject`.

Rules:

- Review plans carry evidence, signal, scope, and confidence. They cannot carry
  a body.
- Learn requires an 8/10 rubric, a verification step, and a body under 120
  lines.
- Learn deduplicates against the whole catalog. Patch a learn-owned skill;
  never duplicate a core or user skill.
- Three patches per skill per week; a fourth needs `--approve`.
- Scan before install. Approval or `auto_install` still gates the host copy.

## Cross-agent foundry

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
