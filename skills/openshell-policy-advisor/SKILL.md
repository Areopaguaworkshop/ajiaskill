---
name: openshell-policy-advisor
description: Use when an OpenShell sandbox returns policy_denied, mentions policy.local, or needs a narrow network policy proposal.
license: Apache-2.0
---

<!-- Vendored from https://github.com/NVIDIA/OpenShell at 5c533d6fbbda46657372b7e56abac7c9347b1a1a. Upstream path: crates/openshell-supervisor-process/src/skills/policy-advisor. See LICENSE and THIRD_PARTY_NOTICES.md. -->
# OpenShell Policy Advisor

When a request fails with `policy_denied`, do not treat the denial as final if the user task still needs the request. Read `/etc/openshell/skills/policy_advisor.md`, inspect `http://policy.local/v1/policy/current`, submit the narrowest proposal to `http://policy.local/v1/proposals`, wait on `/v1/proposals/{chunk_id}/wait?timeout=300`, and retry only after approval with `policy_reloaded: true`.
