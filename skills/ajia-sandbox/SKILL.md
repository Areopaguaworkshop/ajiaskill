---
name: ajia-sandbox
description: Use when a source skill needs to run a script; runs it in a no-network, read-only Docker sandbox or prints the OpenShell or CUA alternative.
license: MIT
---

# ajia-sandbox

## Core principle

Scripts run outside the host. No home, no secrets, no network by default.

## Run

```bash
ajia sandbox <id> --run '<command>'
```

This prints the Docker command. Add `--execute` only after the user approves.

## Policy

- No host files. The skill is mounted read-only at `/skill`.
- No network. The container uses `--network none`.
- No privileges. The container uses `--cap-drop ALL` and `no-new-privileges`.
- Read-only root. `/tmp` is a small tmpfs.
- No credentials, Docker socket, or SSH agent.

## Alternatives

- OpenShell for policy-enforced egress allowlists.
- CUA for desktop and browser skills.
