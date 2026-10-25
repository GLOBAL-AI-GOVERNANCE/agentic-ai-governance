<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DR-012: Alpha.5 Unattended Issuance and Reference Lead Agent

**Status:** Accepted.

**Steward decision date:** October 24, 2026.

**Decision authority:** Global AI Governance steward.

## Decision

Approve `v0.1.0-alpha.5` as the next experimental Agentic AI Governance prerelease. It is a bounded tooling release that adds two references and their console scripts:

- `tools/issue_passports.py` (`issue-passports`): issues signed passports and Sub-Agent Passport Bindings for every agent in a fleet policy file, writes a signed revocation list, validates every passport, and handles revocation and refresh, with no manual step. The policy rejects Level 5, `spend_funds`, and any sub-agent that would exceed its parent.
- `examples/lead-agent/lead_agent.py` (`lead-agent`): a reference lead agent / orchestrator. It runs a guard on every tool call and Agent Fleet Controls for fleet actions, caps delegation depth at 3, suspends, reinstates and revokes with cascade, runs shutdown tests, and keeps a hash-chained audit ledger. Level 5 is always denied. Level 4 goes to the approver the operator's policy names: a person by default, or the operator's own automation for the calls it lists.

## Version rationale

`v0.1.0-alpha.5` continues the experimental alpha line. No schema identity, profile, profile hash anchor, conformance vector, or signed example changes. The Agent Fleet Controls version remains `0.1.0-alpha.4`.

## Unattended operation boundary

Unattended issuance replaces a manual operator step with a scripted one under a policy file the operator controls. It does not let an agent widen its own authority: the policy is validated before issuance, every sub-agent stays within its parent, and Level 5 is never issued. Routing Level 4 to an automated approver is an operator safety setting, off by default.

## Assurance boundary

The DR-003 assurance boundary is unchanged. `AAG-FLEET-001` stays `DEFINED / NOT_YET_ESTABLISHED`. The Second Independently Maintained Verifier remains `PROPOSED / NOT_YET_ESTABLISHED`; project-authored tests are not independent verification. Both references carry `authority_effect: NONE`.

## Preservation

The Alpha.1 generated distribution, the released schema identities and digests, the MCP Governance Profile, the Agent Fleet Controls profile and vectors, the signed examples, and the `v0.1.0-alpha.1` through `v0.1.0-alpha.4` tags remain unchanged. The independent-verifier kit target is unchanged.
