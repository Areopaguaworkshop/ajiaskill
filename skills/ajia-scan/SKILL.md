---
name: ajia-scan
description: Use before promoting or running a source skill, or when the user asks whether a skill is safe; runs the local ajia safety stack and returns findings, license, and a verdict.
license: MIT
---

# ajia-scan

## Core principle

Treat every source skill as untrusted. A scanner is triage, not a certificate.

## Run

```bash
ajia scan <id> --json
```

## Read the report

- `verdict`: `allow`, `warn`, or `block`.
- `tools.skillspector`: score, severity, recommendation, issue count.
- `findings`: severity, rule, file, line, evidence.
- `license`: value and source.

## Safety stack

- **NVIDIA SkillEvaluator:** Tier 1 deterministic pass: PII, unicode smuggling, script lint, license compliance, then SkillSpector. If its scan is incomplete, `ajia` falls back to direct SkillSpector. The report also includes `pii` and `lint` sections from SkillEvaluator.
- **NVIDIA SkillSpector:** deep static scan, 71 patterns, JSON and SARIF.
- **Hermes built-in scanner:** quarantine, trust tier, content hash for hub installs.
- **Snyk `mcp-scan`:** optional second opinion for prompt injection and tool poisoning.
- **Docker, OpenShell, or CUA:** runtime sandbox, not a scanner.

## Rules

- Block on a critical built-in finding.
- Block when SkillSpector scores above 50 or reports CRITICAL.
- Warn on a cautious scan or a score above 20.
- Never promote on a block.
- Never treat a pass as a safety guarantee. Re-scan every byte change.
