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

## User-requested creation

Use this when the user asks to create a skill, not when review found one.

1. Ask five questions, or run `ajia learn --new "<idea>" --json` for the
   structured brief:
   - What does it do? One sentence, third person.
   - When should the agent use it? Give three phrases users would say.
   - What are the exact steps, commands, or source of truth?
   - How does the agent verify success?
   - When should the skill not be used?
2. Write the body to a file and run:
   `ajia learn --new "<idea>" --name <slug> --description "<what + when>" --body draft.md`
3. Read the scan and warnings. Then `ajia use foundry/<slug>` and
   `ajia promote foundry/<slug> --dry-run`. Never auto-promote.

The interactive path runs the same questions when stdin is a TTY. Without a
TTY, `--new` prints the brief and writes nothing.

Authoring rules:

- Description: third person, what it does and when to use it, real trigger
  phrases, under 1024 characters.
- Body: under 500 lines. Move conditional detail to `references/` one level
  deep; link each reference from `SKILL.md`.
- Match specificity to risk: exact commands for fragile steps, judgment for
  open-ended work. Give a default, not a menu.
- Include a verification step and a gotchas or failure-modes section.
- Test the skill on three real tasks before promoting it.

## Edit an existing skill

User-owned foundry skill:

```bash
ajia learn --edit <slug> --body revised.md
ajia learn --edit <slug> --body revised.md --yes
```

The first command shows a diff and writes nothing. `--yes` backs up the old
copy, applies the edit, re-indexes, and re-scans. A blocking scan restores the
backup. If the skill is installed, re-promote it after the edit.

A learn-owned skill must be taken out of the automatic lane first:

```bash
ajia learning adopt <slug>   # or: ajia learning pin <slug>
ajia learn --edit <slug> --body revised.md --yes
```

`ajia learning adopt` and `pin` make the skill user-owned, so future review
patches will not overwrite it. `ajia learning rollback <slug>` or the backup
path restores the previous version.

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
