---
name: ajia-promote
description: Use when the user asks to install or promote a source skill into core; runs the scan, license check, dry-run plan, and requires explicit approval before applying.
license: MIT
---

# ajia-promote

## Core principle

Use is not install. Promotion is a separate, user-approved step.

## Flow

1. Run `ajia scan <id> --json`, or let `promote` run it.
2. Run `ajia promote <id> --dry-run`.
3. Show the scan verdict, license, name, and targets.
4. Ask the user.
5. Only after approval, run `ajia promote <id> --yes`.

## Gate

- `block`: refuse.
- `warn`: require `--force` and a review of the report.
- Unknown license: require `--allow-unknown-license`.
- Existing non-owned target: refuse.
- Never overwrite a native or foreign skill directory.

## Result

Promotion copies the skill to `~/.agents/skills/ajia-<name>` and
`~/.claude/skills/ajia-<name>`, writes a marker, and records a lock entry.

## Undo

`ajia uninstall <id>` removes only owned targets. Backups live under
`~/.ajia/backups/`.
