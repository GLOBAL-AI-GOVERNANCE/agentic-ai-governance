<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agent Fleet Controls Profile

**Profile ID:** `global-ai-governance.agent-fleet-controls`  
**Version:** `0.1.0-alpha.4`  
**Reference evaluator:** `tools/fleet_controls.py`  
**Status:** Experimental public alpha profile. Not frozen. Not approved for production use.

This profile applies the Agent Fleet Controls rules in `spec/11-agent-fleet-controls.md` to a governed agent and the sub-agents it starts. It is additive to the Alpha.1 MCP Governance Profile and does not change any Alpha.1 rule, schema identity, or signed example.

## Status freshness by action level

A relying evaluator MUST reject revocation and suspension status older than the maximum age for the effective action level:

| Level | Maximum status age |
| --- | --- |
| 0 | 86400 seconds |
| 1 | 86400 seconds |
| 2 | 43200 seconds |
| 3 | 3600 seconds |
| 4 | 900 seconds |
| 5 | 300 seconds |

Maximum ages MUST NOT increase as the level rises. A request may tighten these values; it MUST NOT loosen them.

## Action terms

| Term | Minimum level |
| --- | --- |
| `spawn_agent` | 4 |
| `provision_compute` | 4 |
| `install_tool` | 4 |
| `network_call` | 4 |
| `spend_funds` | 5 |

The effective level of a request is the higher of the requested level and the term minimum. Level 5 is not permitted under this profile, so `spend_funds` is never permitted.

## Delegation

The maximum delegation depth is 3. The root passport has depth 0. Each sub-agent holds its own passport, bound to its parent by a Sub-Agent Passport Binding. A binding MUST NOT grant a higher action level, any action term, or a longer validity window than its parent holds.

## Canonical policy anchor

The reference evaluator pins the descriptor JCS hash and this document's byte hash. A request MUST NOT redefine the maximum ages, depth cap, term levels, or Level 5 posture while retaining this profile identity.
