# Third-party notices

`ajiaskill` adapts ideas and, where noted, text from these MIT-licensed projects.

## Matt Pocock — `mattpocock/skills`

- Source: https://github.com/mattpocock/skills
- Files: `skills/productivity/grilling/SKILL.md`, `skills/productivity/grill-me/SKILL.md`
- Used by: `skills/grill-me/SKILL.md`
- License: MIT
- Copyright: Matt Pocock

## Jesse Vincent — `obra/superpowers`

- Source: https://github.com/obra/superpowers
- Files: `skills/writing-plans/SKILL.md`
- Used by: `skills/write-plan/SKILL.md`
- License: MIT
- Copyright: Jesse Vincent

## Planned adaptations

The remaining skills will adapt these MIT sources. Add their notices when the files land.

- `cursor/plugins/pstack` — Lauren Tan — proof ladder, `prove-it-works`, verification-skill pattern.
- `addyosmani/agent-skills` — Addy Osmani — Definition of Done, test sizing.
- `cloudflare/security-audit-skill` — Cloudflare — independent verifier and evidence verdicts.

## Format reference

- `agentskills/agentskills` — Agent Skills specification (Apache-2.0).
- `anthropics/skills` — format examples (mixed licenses; no proprietary document skills are copied).

## External tools (not vendored)

These tools are installed separately and invoked by `ajia`. They are not copied
into this repository.

- **NVIDIA SkillSpector** — Apache-2.0 — https://github.com/NVIDIA/SkillSpector
- **NVIDIA SkillEvaluator** — Apache-2.0 — https://github.com/NVIDIA/SkillEvaluator
- **Hermes Agent** — host runtime — https://github.com/NousResearch/hermes-agent
- **Snyk `mcp-scan`** — optional second opinion — https://github.com/invariantlabs-ai/mcp-scan

## Safety tools in the scan gate

`ajia scan` uses NVIDIA SkillSpector when it is on `PATH`. The built-in
tripwire remains available when it is not. The promotion gate treats scanner
output as triage, not a certificate.

## Routing references (ideas, not vendored)

- **EverMind-AI/SkillCorpus** — Apache-2.0 — per-turn injection, weighted RRF, and a valid "none" gate.
- **zhengyanzhao1997/SkillRouter** — MIT — body-aware retrieval and rerank findings.
- **aurelio-labs/semantic-router** — MIT — semantic routing concepts.
- **zhaoxuya520/reverse-skill** — MIT — rule priority and regression-case patterns.
- **kerpopule/hermes-jev-skills** — MIT — suggestion UX and fatigue controls.
