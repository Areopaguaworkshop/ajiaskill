---
name: ajia-find
description: Use when no installed or native skill clearly matches the task; searches the local ajia catalog and uses a source skill without installing it. Fallback when the ajia MCP tools are unavailable.
license: MIT
---

# ajia-find

This is the fallback path. Prefer the `ajia_search` and `ajia_use` MCP tools when they are available.

## Search

Run:

```bash
ajia search "<task>" --json
```

Pick the best result by `match_reason`. If no result fits, stop and do the task normally.

## Use

Run:

```bash
ajia use <id> --json
```

Read the `body` field and follow it as instructions. Resolve relative files from `base_dir`. The skill is read-only; `ajia` does not execute scripts.

## Guard

- One search per task.
- Do not search for ordinary edits or when a native or core skill fits.
- Do not install or promote. The user decides that with `ajia promote`.
- If a source skill needs a script, ask before running it and use the host sandbox and permissions.
