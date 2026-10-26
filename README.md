# ajiaskill

A local skill platform for coding agents. One catalog, one CLI, one MCP server, and a silent router. Find a source skill, use it without installing it, and promote it only after a safety gate.

Status: **Phase 3b: foundry, profiles, and Hermes-generated metadata.** Catalog, search/use, MCP, safety, promotion, rollback, native inventory, remote source add, cross-agent foundry, profiles, and generated-skill metadata exist. MCP is the default automatic trigger. Host hooks are reference-only and are not installed.

## What it does

- **Catalog:** indexes `SKILL.md` files from local and git sources.
- **Search:** finds a skill by name, description, and path.
- **Use:** copies the exact bytes to a read-only store and returns the full `SKILL.md` to the agent. Use it in place; copying it into a host skill directory is installation.
- **MCP (default):** the `ajiaskill` server exposes `ajia_search` and `ajia_use` as tools. The agent calls them when no native or core skill fits.
- **Router (optional):** `ajia route` maps a message to one skill with rules and metadata. `ajia-router` is the fallback skill. Host hooks are reference-only.
- **Remote search:** queries `skills.sh`.
- **Remote source path:** `ajia remote add` turns a skills.sh result into a pinned git source, syncs it, and finds the skill in the catalog.
- **Remote install:** wraps `npx skills add` when you explicitly want the upstream installer.
- **Scan:** NVIDIA SkillEvaluator and SkillSpector plus a built-in tripwire.
- **Promote:** manual, gated, backed up, and recorded in a lock file.
- **Sandbox:** prints a no-network, read-only Docker command for source scripts.
- **Foundry:** writes cross-agent candidates under `~/.ajia/foundry`, and indexes Hermes `/learn` skills as candidates.
- **Profiles:** sources, hosts, routing thresholds, and safety policy per profile.
- **Generated metadata:** Hermes `created_by` and curator state, plus foundry candidates, appear in the catalog.

## Quick start

```bash
python3 bin/ajia init
python3 bin/ajia source sync
python3 bin/ajia search "review ui accessibility"
python3 bin/ajia use <id>
python3 bin/ajia route "review this PR" --json --host opencode
```

`source sync` indexes the two enabled local sources: `ajia-core` (this repo) and `hermes` (`~/.hermes/skills`). The 24 remote sources are configured but off by default.

## npm

The npm package is `ajiaskill`. It ships the CLI, the MCP server, and the eight core skills. Python 3.10+ is required; the Node wrapper calls `python3` unless `AJIA_PYTHON` is set.

```bash
npm install -g ajiaskill
ajiaskill init
ajia search "review ui accessibility"
ajiaskill mcp --host codex
```

Without a global install:

```bash
npx -y ajiaskill init
npx -y ajiaskill mcp --host codex
npx -y ajiaskill-mcp --host codex
```

`ajiaskill` and `ajia` are the same CLI. `ajiaskill-mcp` starts the MCP server directly. The local `setup` command prints absolute Python commands for this checkout; npm users can substitute `npx -y ajiaskill mcp --host <host>`.

Enable a remote source when you need it:

```bash
python3 bin/ajia source enable pstack
python3 bin/ajia source sync pstack
```

## Router (optional)

The default automatic path is MCP. `ajia route` remains for manual routing, the `ajia-router` fallback skill, and a future deterministic mode.

```bash
ajia route "review this PR" --json --host opencode
ajia route "make this page prettier" --json --host opencode
ajia route "what is the weather" --explain
```

The router uses `routing.json` plus optional sidecar metadata:

| Field | Use |
|---|---|
| `capabilities` | Canonical verbs such as `review.code` or `design.ui`. |
| `triggers` | Phrases, keywords, and regex. |
| `examples` | Positive and negative sentences. |
| `negative_triggers` | Veto or downrank, with an `unless` context. |
| `file_globs` | Context evidence. |
| `host_fit` | Soft host preference. |
| `requires` | Hard tool and environment gate. |
| `priority` | Tie-break only. |

The score is:

```text
0.55 * lexical + 0.25 * rule + 0.10 * context + 0.10 * priority
```

The router injects at 0.60 or more with a 0.08 margin, or at a 0.90 rule hit. It suggests between 0.45 and 0.60. It does nothing below 0.45. It logs decisions to `~/.ajia/routing.jsonl`.

The router returns `native` when the host already has the skill, `inject` when it can use a source or core body, `suggest` when ambiguous, and `none` when no match is safe. The primary automatic path is still MCP. `ajia-router` is the manual fallback.

## Remote backends

```bash
ajia remote search "test driven development" --limit 5
ajia remote add obra/superpowers --skill test-driven-development
ajia use remote-obra-superpowers/skills/test-driven-development
ajia scan remote-obra-superpowers/skills/test-driven-development
ajia promote remote-obra-superpowers/skills/test-driven-development --dry-run
```

`remote search` uses the `skills.sh` API. `remote add` normalizes the source, queries the GitHub repository license, records it as the source license fallback, clones under `~/.ajia/sources`, rebuilds the catalog, and returns the catalog id. A per-skill license wins over the source license.

`remote install` prints the `npx skills add` command and only runs it with `--yes`. The upstream installer bypasses the ajia scan and promotion gate.

## Install

```bash
./install.sh --dry-run
./install.sh
```

The installer links each skill into `~/.agents/skills` and `~/.claude/skills`, and links the CLI into `~/.local/bin/ajia`. Use `--no-cli` to skip the CLI link, or `--project .` to copy skills into a project.

Uninstall:

```bash
./install.sh --uninstall
```

The uninstaller removes only symlinks that point into this repository.

## MCP (default)

MCP is the default trigger on all six hosts. Register it once:

```bash
python3 bin/ajia setup opencode
python3 bin/ajia setup pi
python3 bin/ajia setup hermes
python3 bin/ajia setup codex
python3 bin/ajia setup omp
python3 bin/ajia setup claude
```

Each command prints the exact registration command and the 2-line policy. The MCP server is registered as `ajiaskill`; its tools are read-only. They are live on OpenCode, Pi, Hermes, Codex, OMP, and Claude. Each registration passes `--host` so search results can mark native skills and `ajia_use` can refuse a duplicate fallback.

Start a new host session to load `ajia_search` and `ajia_use` if they are not visible yet.

## Host adapters (reference only)

Hooks are **not installed**. MCP is the default.

`bin/ajia-hook` and `adapters/` remain as reference code for a future deterministic mode. If you enable them later, they fail open on timeout or error. See `adapters/README.md` for the per-host caveats.

## Safety stack

| Layer | Tool | Gate |
|---|---|---|
| Tier 1 | NVIDIA SkillEvaluator | PII, unicode, script lint, license, then SkillSpector. |
| Static scan | NVIDIA SkillSpector | 71 patterns; JSON and SARIF. **Primary gate.** |
| Host gate | Hermes built-in scanner | Quarantine, trust tier, content hash. |
| Second opinion | Snyk `mcp-scan` | Prompt injection and tool poisoning. Optional. |
| Runtime | Docker, OpenShell, CUA | No host files, no secrets, no network by default. |
| Pin | git SHA, tree hash, lock | Exact bytes; re-scan every change. |

Scanners are triage, not certificates. Pin the exact bytes and re-scan.

## Scan and promote

```bash
ajia scan <id> --json
ajia promote <id> --dry-run
ajia promote <id> --yes
ajia uninstall <id>
```

Promotion rules:

- `block` verdict: refuse.
- `warn` verdict: require `--force` after review.
- Unknown license: require `--allow-unknown-license`.
- Existing non-owned target: refuse.
- Promoted copies are named `ajia-<skill>` and carry `.ajia-promoted.json`.
- Replaced copies are backed up under `~/.ajia/backups/`.
- The lock file is `~/.ajia/ajia.lock.json`.

## Commands

| Command | Purpose |
|---|---|
| `ajia init` | Create `~/.ajia` and the default `sources.yaml`. |
| `ajia source list` | Show sources and their on/off state. |
| `ajia source add <id> <path-or-url>` | Add a local or git source. |
| `ajia source enable/disable <id>` | Toggle a source. |
| `ajia source sync [id...]` | Fetch sources and rebuild the catalog. |
| `ajia catalog build` | Rebuild the catalog from enabled sources. |
| `ajia catalog stats` | Show skill counts and catalog digest. |
| `ajia search "<query>" --json` | Search the local catalog. |
| `ajia use <id> --json` | Use a skill without installing it. |
| `ajia route "<task>" --json` | Route a message to one skill, with native-first decisions. |
| `ajia generated [--json]` | List generated and foundry candidates. |
| `ajia profile list/show/use` | Inspect or switch local profiles. |
| `ajia foundry init/sync/list` | Manage the cross-agent foundry. |
| `ajia native [--host]` | List native and ajia-owned skills per host. |
| `ajia rollback <id>` | Restore a promoted skill from its backup. |
| `ajia remote search "<query>"` | Search skills.sh. |
| `ajia remote add <source> --skill <skill>` | Add a skills.sh source, sync it, and find the skill. |
| `ajia remote install ...` | Print or run the npx skills installer. |
| `ajia mcp` | Run the stdio MCP server. |
| `ajia setup <host>` | Print the MCP registration command with the host id. |
| `ajia scan <id> --json` | Run SkillEvaluator security, PII, and lint, plus SkillSpector and the tripwire. |
| `ajia promote <id> --dry-run` | Show the promotion plan. |
| `ajia promote <id> --yes` | Apply the promotion. |
| `ajia uninstall <id>` | Remove an owned promoted copy. |
| `ajia sandbox <id> --run '<cmd>'` | Print or run a Docker sandbox command. |
| `ajia learn '<source>'` | Print the Hermes `/learn` path and the foundry path. |
| `ajia policy` | Print the 2-line trigger policy. |
| `ajia status` | Show sources, skills, and trials. |
| `ajia doctor` | Check the local setup. |

## Foundry and profiles

The cross-agent foundry is the reliable path:

```bash
mkdir -p ~/.ajia/foundry/my-skill
$EDITOR ~/.ajia/foundry/my-skill/SKILL.md
ajia foundry sync
ajia generated
ajia use foundry/my-skill
```

Any agent can write a foundry candidate. The source is enabled by default and
indexed with `generated_by: foundry`. Nothing is installed until promotion.

Hermes `/learn` is interactive. `hermes -z` and `hermes chat -q` prune
`skill_manage`, so they cannot author skills. Use `ajia learn --execute` as a
best-effort PTY driver, or run `/learn` in `hermes chat` and then
`ajia source sync hermes`. Hermes skills with `created_by` `learn` or `agent`
carry `generated_by` and `curator_state` in the catalog.

Profiles live in `profiles.json` (or `~/.ajia/profiles.json`):

```bash
ajia profile list
ajia profile show
ajia profile use work
```

A profile selects sources, hosts, router thresholds, and safety policy. The
default `personal` profile allows every enabled source. The `work` profile is a
smaller example.

## Native-first

`hosts.json` holds the user and project skill roots for all six hosts. `ajia native` scans them, marks ajia-owned symlinks and promoted copies, and reports what is truly native. `ajia search --host` and `ajia route --host` use that inventory. A native skill wins, and the source fallback is refused.

## Core skills

- `grill-me` — turn a vague idea into shared understanding.
- `write-plan` — turn that understanding into an executable plan.
- `ajia-find` — fallback catalog search/use.
- `ajia-router` — fallback router for manual use.
- `ajia-scan` — the safety stack and report reading, including PII and lint.
- `ajia-promote` — the gated promotion flow.
- `ajia-sandbox` — no-network script execution.
- `ajia-learn` — Hermes `/learn` foundry.

## Layout

```text
bin/ajia                 # CLI, router, and MCP server
bin/ajia-hook            # generic Codex/Claude/Hermes hook
hosts.json               # native and project skill roots per host
profiles.json            # sources, hosts, routing, safety
routing.json             # routing metadata for core and common skills
adapters/                # reference OpenCode, Pi, and OMP adapters
skills/                  # core skills
scripts/validate-skills.py
scripts/test_mcp_hosts.py
tests/test_ajia.py
install.sh
```

## Validate

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate-skills.py
scripts/test_mcp_hosts.py
./install.sh --check
```

## License

MIT for the original content. Adapted skills keep their upstream notices in `THIRD_PARTY_NOTICES.md`.
