---
name: ajia-router
description: Use when the host has no router hook, the user asks which skill fits, or a manual route is needed; runs ajia route and follows the selected skill only when confidence is high.
license: MIT
---

# ajia-router

This is the fallback. The primary router is a host hook.

## Run

```bash
ajia route "<task>" --json --host <host>
```

## Follow the decision

- `native`: use the host's native skill at `path`. Do not load the source body.
- `inject`: follow `body`. Resolve relative files from `base_dir`.
- `suggest`: show 2–3 candidates and ask. Do not inject.
- `none`: do the task normally.

## Rules

- One route per task.
- Use the selected skill in place. Do not copy it into a host skill directory.
- Do not promote.
- Do not execute a source script outside the sandbox.
- If the host hook is active, do not use this skill.
