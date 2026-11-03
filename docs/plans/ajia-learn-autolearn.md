# ajia-learn autolearn — plan

Status: M0–M4 implemented; rollout and ongoing hardening remain.

Current implementation (2026-11-03): `ajia review` is capture-only. It queues
an evidence-backed lesson under `~/.ajia/learning/lessons/`. `ajia learn` is the
only author. Learn applies the 8/10 rubric, whole-catalog dedup, patch caps,
scan, approval, and install gates. The old direct-write path is removed.

Visual plan: [ajia-learn-autolearn.html](ajia-learn-autolearn.html)

## Goal

Make `ajia-learn` behave like Hermes' automatic learning loop, for OpenCode,
Pi, OMP, Codex, and Claude Code (not Hermes):

- after a turn/session, review the transcript;
- detect corrections, preferences, techniques, and repeated intents;
- create or patch a class-level skill;
- write it to the foundry, index it, install it into the host skill root, and
  reload the host;
- maintain a small memory store and inject it into the host prompt;
- keep core, third-party, user-owned, and adopted skills immutable;
- keep a ledger, backups, and rollback.

User decisions:

- write policy: **active + auto-install**;
- install target: **`~/.agents/skills` only** (all five hosts read it);
- hosts: **OpenCode, Pi, OMP, Codex, Claude Code**; Hermes excluded;
- auto-update: **patch only review-owned candidates**;
- scope: **skills + memory**;
- memory: **global `USER.md` + per-project files**;
- model: **host-native where clean, endpoint fallback**;
- default: **enabled by default**; installing the host plugin/hook is the
  per-host consent gate. `ajia learning pause` is the kill switch.

## What Hermes does (research summary)

Hermes' automatic behavior is a host runtime, not a skill:

- post-turn background review, gated by nudge intervals (skills every 15
  tool iterations, memory every 10 turns);
- forks the agent with a transcript snapshot; same model (warm cache) or an
  auxiliary model with a digest;
- strict prompt: update a loaded skill, update an umbrella, add a reference,
  or create a class-level umbrella;
- tool whitelist: `memory`, `skills`, `read_file`, `search_files`; no terminal;
- read-before-write; provenance `created_by: agent`; protects bundled, hub,
  pinned, user-owned, and external skills;
- curator (separate, every 7 days): stale/archive/consolidate, ledger,
  snapshots, rollback; archive-never-delete;
- `/learn` is an explicit, different path.

## What ajiaskill has

- MCP server: `ajia_search`/`ajia_use` only; no transcript, no turn.
- `bin/ajia-hook`: pre-prompt only; no post-turn.
- OpenCode adapter: dead V1 reference plugin; V2 is not implemented.
- Foundry: already an indexed, searchable, usable candidate store. Reuse it,
  do not add a second "learned" source.
- `ajia use` does not increment use counts; ranking/staleness are blind
  outside Hermes.
- No memory store, curator, or outcome logging.

## Host APIs (verified / to verify)

| Host | Trigger | Transcript | Host model | Notes |
|---|---|---|---|---|
| OpenCode 2.2.0 | V2 plugin; `ctx.event.subscribe` (`session.idle` / assistant completion) | `ctx.session.context({sessionID})` | `ctx.session.generate({sessionID, prompt})` — transient, no tools/history | Also `ctx.skill.transform`/`reload`, `ctx.session.hook("context")`, `ctx.storage` |
| Claude Code 2.x | `Stop` hook with `transcript_path` | transcript file | `claude -p` headless | Verify hook timeout/async and child recursion |
| Codex 0.165 | `notify`/post-turn hook (verify) | session log (verify) | `codex exec` headless | Verify hook payload and transcript path |
| Pi 1.4 | extension event (verify) | extension API (verify) | headless command (verify) | Reference adapter is pre-turn only |
| OMP 18.13 | extension event (verify) | extension API (verify) | headless command (verify) | Reference adapter is pre-turn only |
| Hermes | excluded | — | — | Do not duplicate; index Hermes skills via source sync |

## Architecture

### 1. Review engine: `ajia review`

Input: a normalized transcript (JSONL/Markdown) + host.

Pipeline:

1. Normalize messages, tool calls, outcomes.
2. Detect one of four signals: explicit correction, failed attempt with a
   verified fix, repeated intent in two sessions, or a loaded skill that caused
   a wrong step.
3. Generate a strict lesson with the host model or configured endpoint:
   `action | signal | scope | name | description | evidence | confidence`.
   The review schema has no body.
4. Validate the lesson: evidence count, signal, scope, name, description,
   confidence, and no body. A body is a hard error.
5. Append the lesson to `~/.ajia/learning/lessons/` with `status: proposed` or
   `noop`.
6. Record the review budget. Do not write foundry, scan, or install.

### 1b. Authoring engine: `ajia learn`

Input: one proposed lesson plus a skill plan from the host model or
`AJIA_LEARN_URL`.

Pipeline:

1. Load the proposed lesson. Refuse a missing, rejected, or already authored
   lesson.
2. Generate or load the skill plan: action, name, description, body, license,
   confidence, and rubric.
3. Validate the rubric: five dimensions scored 0–2, total at least 8, no zero
   on trigger or verification.
4. Validate the body: no frontmatter, under 120 lines, one verification step.
5. Deduplicate against the whole catalog: patch a learn-owned skill; reject a
   duplicate of a core or user skill.
6. Enforce the patch cap: three patches per skill per week; `--approve` overrides
   the fourth.
7. Write `~/.ajia/foundry/<slug>/SKILL.md` + `.ajia-learn.json` with
   `origin: learn`, `review_id`, `lesson_id`, rubric, and quality score.
8. Rebuild the catalog, scan, quarantine, stage approval, or install.
9. Append a ledger entry and mark the lesson `authored` or `noop`.

### 2. Store and state

- Reuse `~/.ajia/foundry`; no new source.
- Sidecar `.ajia-learn.json` per managed skill:
  `origin: review`, `state: active|candidate`, `created_at`, `updated_at`,
  `content_hash`, `pinned`, `adopted`.
- `build_catalog` reads the sidecar; defaults remain `generated_by: foundry`,
  `curator_state: candidate`.
- `~/.ajia/usage.json` keyed by skill id; `ajia use` increments; catalog reads.
- `~/.ajia/learning/ledger.jsonl`, `~/.ajia/learning/state.json`,
  `~/.ajia/learning/intents.jsonl`.
- Memory: `~/.ajia/memory/USER.md`, `~/.ajia/memory/projects/<project>.md`,
  `MEMORY.md` index.

### 3. Auto-install

- Single common target: `~/.agents/skills/ajia-<slug>` (all five hosts list
  `~/.agents/skills` in `hosts.json`).
- Write `.ajia-promoted.json` so `is_owned_skill` marks it owned and
  native-first does not refuse the MCP fallback.
- Backup the previous copy under `~/.ajia/backups/`.
- Scan first; block/warn policy applies.
- OpenCode: call `ctx.skill.reload()` after install; other hosts load at next
  session.
- Core, third-party, user-owned, adopted, and pinned skills are immutable.
- `ajia uninstall`/rollback removes only review-owned copies.

### 4. Host triggers

Each host gets a thin adapter; the engine owns validation and writes.

- **OpenCode:** V2 plugin. Subscribe to session idle/assistant completion;
  fetch transcript; call `ctx.session.generate` with a strict review prompt;
  pass the JSON plan to `ajia review --plan`. Use `ctx.storage` for cooldown
  and last-reviewed message; `ctx.skill.transform` for immediate surfacing;
  `ctx.session.hook("context")` for memory.
- **Claude Code:** `Stop` hook. Pass `transcript_path` to
  `ajia review --transcript`; use `claude -p` as the model provider; inject
  memory via a session-start hook.
- **Codex:** `notify`/post-turn hook if available; otherwise `codex exec`
  provider + a wrapper. Verify the installed 0.165 contract first.
- **Pi/OMP:** extension event + headless model command; verify APIs first.
- **Hermes:** disabled in `learning.hosts`; index Hermes-created skills via
  `ajia source sync hermes` only.

### 5. Model providers

Provider interface:

- `host`: adapter supplies a JSON plan using the host model.
  - OpenCode: `ctx.session.generate` (transient; no tools/history).
  - Claude: `claude -p`.
  - Codex: `codex exec`.
  - Pi/OMP: verify headless.
- `endpoint`: `AJIA_REVIEW_URL` OpenAI-compatible; `AJIA_REVIEW_MODEL`,
  `AJIA_REVIEW_API_KEY`, timeout, token cap. This is the common fallback.

Host-native is preferred where it is clean; endpoint is the fallback and the
only option when a host has no safe headless review path. A child-review env
flag (`AJIA_REVIEW_CHILD=1`) prevents recursion in hooks.

### 6. Trigger policy

- OpenCode: after a turn/session idle; cooldown and per-session single-flight.
- Claude/Codex: after turn; same cooldown.
- Minimum signals: correction/preference/technique or repeated intent >= 2.
- Trivial turns: noop.
- Optional `learning.review_every_n_turns` and token caps.
- One review in flight per host/session; file lock around write+sync.

### 7. Safety gates (Hermes parity)

Hermes has the same class of gates; ajiaskill needs explicit equivalents
because auto-install is enabled.

| Gate | Hermes evidence | ajiaskill implementation |
|---|---|---|
| Automatic scan | `skills.guard_agent_created` security scan with rollback (`tools/skill_manager_tool.py:49-63,333-351`); memory injection scan | Mandatory for every review-created/patched skill. Reuse `scan_skill`: SkillEvaluator, SkillSpector, built-in tripwire, PII, unicode, license, injection patterns. Write `scan.json`. |
| Quarantine | Staged writes under `~/.hermes/pending/skills` with `/skills pending|approve|reject` (`tools/write_approval.py:170-185`); archive is separate | `~/.ajia/learning/quarantine/<slug>/` holds `SKILL.md`, `scan.json`, `reason`. Not indexed, not searchable, not installed. Release only with a passing rescan and `ajia learning quarantine release <slug> --yes`. |
| Backup | Curator snapshot before every real run (`agent/curator.py:891-900`); promotion backups | Before every patch or install: snapshot the foundry tree and the installed `~/.agents/skills/ajia-<slug>` copy under `~/.ajia/backups/<stamp>/<slug>/`. Retention policy, never overwrite a backup. |
| Rollback | Curator ledger with content-addressed blobs + `hermes curator rollback` (`tools/skill_ledger.py`) | `~/.ajia/learning/ledger.jsonl`: before/after path, sha256, actor, action, scan verdict. Blobs under `~/.ajia/learning/blobs/`. `ajia learning rollback <id|entry>` restores foundry and installed copy; fail closed if a blob is missing. Auto-rollback on install failure. |
| Immutable core/user | `skill_manager_guards.py`: bundled, hub, pinned, user-owned, external, unreadable provenance refused; `created_by` is a policy flag | Review may write only `.ajia-learn.json` with `origin: review` and `state != adopted`. Core `skills/`, third-party, `.ajia-promoted.json`, adopted, pinned, and unreadable provenance are immutable. Fail closed. |
| Read-before-write / CAS | Exact target read mark required for patch/write (`skill_manager_guards.py:220-238`) | Hash the current target; patch only if the base hash matches. Refuse a patch that shrinks the body by more than 50% without explicit approval. |
| Archive, never delete | Curator archives; no auto-delete | `ajia learning archive`; no auto-delete. Archive excludes from the catalog and host root; restore is explicit. |
| Kill switch | `auxiliary.background_review.enabled: false` | `ajia learning pause`; `learning.enabled: false`. Pauses review and auto-install, leaves installed skills intact. |

Pipeline order (no shortcuts):

1. Review plan is validated and written to foundry.
2. Automatic scan runs before any install.
3. Block or warn → quarantine; no host write.
4. Pass → backup foundry and installed copy.
5. Atomic install to `~/.agents/skills/ajia-<slug>`.
6. Append ledger entry with before/after hashes.
7. Reload the host registry.
8. Any failure after step 4 → restore backup and record a failed ledger entry.

Additional safety:

- Transcript is untrusted: strict JSON, no raw transcript in skill bodies,
  no shell from the model, injection scan on the generated body.
- Path allowlist in code: `~/.ajia`, `~/.agents/skills/ajia-*`.
- Redact secrets before remote model calls; local model preferred.
- One review in flight per host/session; a file lock covers write + index +
  install.
- Per-host consent is installing the adapter; enabled by default once the
  adapter exists.

## Commands

```text
ajia review --transcript <file> --host <host> [--plan <json>]
ajia learning status|pause|resume
ajia learning quarantine list|show <slug>|release <slug> --yes
ajia learning backup list
ajia learning rollback <id|entry>
ajia learning ledger
ajia learning archive <slug>|restore <slug>
ajia learning adopt <slug>|pin <slug>
ajia memory show|add
```

## Controls

Auto-approve means the automatic install path. It is enabled by default per
your decision, and every part can be disabled.

| Control | Default | Effect |
|---|---|---|
| `learning.enabled` | `true` | Master switch for review and install. |
| `learning.auto_install` | `true` | Install learned skills automatically. Set `false` to keep review + candidates only. |
| `learning.require_approval` | `false` | Stage every create, patch, and install for explicit approval. |
| `learning.auto_patch` | `true` | Patch review-owned skills automatically. Set `false` to queue patches. |
| `learning.hosts` | all five | Per-host allowlist; remove a host to disable its trigger. |
| `ajia learning pause` | — | Runtime kill switch; leaves installed skills intact. |

With `auto_install: false`, the review still writes a searchable foundry
candidate; run `ajia learning approve <id>` or `ajia promote <id> --yes` to
install it. With `require_approval: true`, nothing is written or installed
until approved.

## Phases

| Phase | Deliverable | Acceptance |
|---|---|---|
| M0 | `ajia use` usage ledger; `ajia review --transcript`; foundry candidate; validation/scan; quarantine; backup; ledger; immutable guards; tests — **implemented** | Real correction creates a skill; search/use finds it; noop on trivial; injection does not write; blocked skill is quarantined; install failure restores backup; core/user skill patch is refused |
| M1 | OpenCode V2 plugin: completion trigger, host `generate`, auto-install to `~/.agents/skills`, `ctx.skill.reload`, memory injection — **implemented** | One automatic review; skill installed and visible next turn; scan/quarantine/backup/rollback exercised; no core/user writes |
| M2 | Claude Code `Stop` + `claude -p`; Codex `Stop` + `codex exec`; memory injection — **implemented** | Same acceptance on each host; per-host disable |
| M3 | Pi/OMP adapters; repetition signal; dedupe/merge; curator (pin/adopt/archive/restore/prune/rollback); outcome metrics — **implemented** | No duplicates; stale/archive works; rollback works |
| M4 | Privacy/redaction, injection eval, cost caps, docs, rollout — **implemented** | Security fixtures pass; per-day budget respected |

## Confirmed defaults

- Single install target `~/.agents/skills`; one copy, no per-host duplicates.
- Memory: global `USER.md` + per-project files, injected into prompts.
- Model: host-native where clean; `AJIA_REVIEW_URL` fallback.
- Enabled by default; host adapter installation is consent. `ajia learning
  pause` disables review and auto-install without uninstalling skills.
- Auto-install still requires the automatic scan, backup, and rollback path.

## Remaining implementation checks

- OpenCode V2 exact idle/assistant-completion event name and `ctx.session.generate`
  behavior on the installed 2.2.0.
- Claude `Stop` hook timeout/async semantics and `claude -p` recursion guard.
- Codex 0.165 `notify`/post-turn payload and `codex exec` provider invocation.
- Pi/OMP post-turn/transcript APIs; if absent, endpoint + pre-turn adapter only.
- Scan thresholds, 50% patch-shrink guard, and secret/PII redaction rules.
- Cost budget: max review runs/day and max input tokens per run.

## Non-goals (first pass)

- Replacing Hermes' native review.
- Auto-installing into every host-specific root when `~/.agents/skills` works.
- LLM consolidation/merge in M0–M2.
- Cross-machine memory sync.
