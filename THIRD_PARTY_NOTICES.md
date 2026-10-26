# Third-party notices

`ajiaskill` adapts ideas and, where noted, text and code from these MIT- and
Apache-2.0-licensed projects. Each bundled skill keeps its upstream license
files next to its `SKILL.md`.

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

## Julius Brussee — `JuliusBrussee/caveman`

- Source: https://github.com/JuliusBrussee/caveman
- Files: `skills/caveman/SKILL.md`
- Used by: `skills/caveman/`
- License: Apache-2.0; pre-3.0 parts under MIT (`LICENSE-MIT`)
- Copyright: 2026 Julius Brussee

## multica-ai — `andrej-karpathy-skills`

- Source: https://github.com/multica-ai/andrej-karpathy-skills
- Files: `skills/karpathy-guidelines/SKILL.md`
- Used by: `skills/karpathy-guidelines/`
- License: MIT, declared in `.claude-plugin/plugin.json`; the upstream tree has no LICENSE file
- Copyright: multica-ai contributors

## Dietrich Gebert — `DietrichGebert/ponytail`

- Source: https://github.com/DietrichGebert/ponytail
- Files: `skills/ponytail/SKILL.md`
- Used by: `skills/ponytail/`
- License: MIT
- Copyright: 2026 DietrichGebert

## tt-a1i — `tt-a1i/archify`

- Source: https://github.com/tt-a1i/archify
- Files: `archify/SKILL.md`, `archify/bin/`, `archify/references/`, `archify/renderers/`, `archify/schemas/`, `archify/explainer/`, `archify/assets/`
- Used by: `skills/archify/` (upstream `examples/` excluded)
- License: Apache-2.0; pre-transition parts under MIT (`LICENSE-MIT`)
- Copyright: 2026 tt-a1i (Archify); 2025 Cocoon AI
- Notice: `skills/archify/NOTICE`, `skills/archify/THIRD_PARTY_NOTICES.md`

## Lauren Tan — `backnotprop/pstack`

- Source: https://github.com/backnotprop/pstack
- Files: `skills/create-verification-skill/SKILL.md`, `skills/create-verification-skill/references/`
- Used by: `skills/create-verification-skill/`
- License: MIT
- Copyright: 2026 Lauren Tan

## Answer me with HTML — `QingYunA/answer-me-with-html`

- Source: https://github.com/QingYunA/answer-me-with-html
- Files: `skills/answer-me-with-html/SKILL.md`, `scripts/am.mjs`, `references/`, `licenses/`
- Used by: `skills/answer-me-with-html/`
- License: MIT
- Copyright: 2026 Answer me with HTML contributors

## Impeccable — `pbakaus/impeccable`

- Source: https://github.com/pbakaus/impeccable
- Files: `plugin/skills/impeccable/SKILL.md`, `reference/`, `scripts/`
- Used by: `skills/impeccable/`
- License: Apache-2.0
- Copyright: pbakaus and contributors
- Notice: `skills/impeccable/NOTICE`
- Local addition: `reference/pdf-export.md`, `scripts/pdf-export.sh`, and the PDF section in `SKILL.md` are ajiaskill additions, not upstream.

## rtk-ai — `rtk-ai/rtk`

- Source: https://github.com/rtk-ai/rtk
- Files: `.claude/skills/{code-simplifier,design-patterns,issue-triage,performance,pr-review,pr-triage,repo-recap,rtk-tdd,rtk-triage,security-guardian,ship,tdd-rust}/`
- Used by: `skills/code-simplifier/`, `skills/design-patterns/`, `skills/issue-triage/`, `skills/performance/`, `skills/pr-review/`, `skills/pr-triage/`, `skills/repo-recap/`, `skills/rtk-tdd/`, `skills/rtk-triage/`, `skills/security-guardian/`, `skills/ship/`, `skills/tdd-rust/`
- License: Apache-2.0 (the RTK CLI; the `engine/` BUSL-1.1 tree is not vendored)
- Copyright: rtk-ai contributors
- Note: these skills are RTK/Rust-specific; they reference RTK commands and modules.

## NVIDIA — `NVIDIA/OpenShell`

- Source: https://github.com/NVIDIA/OpenShell
- Files: `crates/openshell-supervisor-process/src/skills/policy-advisor/SKILL.md`
- Used by: `skills/openshell-policy-advisor/`
- License: Apache-2.0
- Copyright: 2026 NVIDIA CORPORATION & AFFILIATES

## Cua AI — `trycua/cua`

- Source: https://github.com/trycua/cua
- Files: `libs/cua-driver/rust/Skills/cua-driver/`
- Used by: `skills/cua-driver/`
- License: MIT
- Copyright: 2025 Cua AI, Inc.

## Ayoub Ghriss — `ayghri/i-have-adhd`

- Source: https://github.com/ayghri/i-have-adhd
- Files: `skills/i-have-adhd/SKILL.md`
- Used by: `skills/i-have-adhd/`
- License: MIT
- Copyright: 2026 Ayoub Ghriss

## Tencent — `Tencent/BrowserSkill`

- Source: https://github.com/Tencent/BrowserSkill
- Files: `crates/bsk-cli/skill/SKILL.md`, `references/`
- Used by: `skills/browser-skill/`
- License: MIT
- Copyright: 2026 Tencent

## Planned adaptations

The remaining skills will adapt these MIT sources. Add their notices when the files land.

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

- **EverMind-AI/SkillCorpus** — Apache-2.0 — per-turn injection, weighted RRF, deduplication, and a valid "none" gate.
- **zhengyanzhao1997/SkillRouter** — MIT — body-aware retrieval and rerank findings.
- **Tencent/R3-Skill** — Apache-2.0 — query-conditional two-stage retrieval.
- **aurelio-labs/semantic-router** — MIT — semantic routing concepts.
- **jax-agent/skill-router** — MIT — compact skill index and on-demand load.
- **LittlePeter52012/skill-router** — MIT — local keyword matching, fuzzy matching, and optional rerank.
- **tsvelovskiysv/claude-skill-router** — MIT — project facets, trust ranking, and diverse selection.
- **wuykjl/neuro-skill** — MIT — weighted RRF and offline hybrid routing.
- **zhaoxuya520/reverse-skill** — MIT — rule priority and regression-case patterns.
- **kerpopule/hermes-jev-skills** — MIT — suggestion UX and fatigue controls.
- **DecimalAI Smart Route** — hosted API — hybrid retrieval, RRF, full-menu fallback, and effectiveness rerank.
- **OATS** — arXiv 2603.13426 — outcome-aware tool selection.
- **DSR** — arXiv 2609.05824 — diversity-aware skill reranking.
- **SkillWeaver** — arXiv 2606.18051 — compositional routing.
- **Semantic tool discovery** — arXiv 2603.20313 — vector retrieval for MCP tools.
- **PinePaper-ToolBench** — benchmark — BM25 and knowledge-graph tool selection.
- **MCP-Bench**, **LiveMCPBench**, **MCPToolBench++** — benchmarks — retrieval as the dominant MCP bottleneck.
- **agentskills/agentskills** — Apache-2.0 / CC-BY-4.0 — Agent Skills format.
- **NVIDIA SkillSpector**, **NVIDIA SkillEvaluator** — Apache-2.0 — safety and quality gates (already used as external tools).
