<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DR-011: Alpha.4 Agent Fleet Controls

**Status:** Accepted.

**Steward decision date:** October 24, 2026.

**Decision authority:** Global AI Governance steward.

## Decision

Approve `v0.1.0-alpha.4` as the next experimental Agentic AI Governance prerelease, adding Agent Fleet Controls as a bounded, additive reference:

- revocation and suspension status maximum ages per action level, shorter for higher levels;
- a reinstatable `SUSPENDED` state distinct from terminal revocation;
- the action terms `spawn_agent`, `provision_compute`, `spend_funds`, `network_call`, and `install_tool`, each with a minimum action level;
- a delegation depth cap;
- a Sub-Agent Passport Binding that gives each sub-agent its own passport bound to its parent, with action level, action terms, and validity never above the parent's.

The normative source is `spec/11-agent-fleet-controls.md`. The machine-readable artifacts are five new schemas with `v0.1.0-alpha.4` identities, the profile `profiles/agent-fleet-controls-profile.json` and its document, the reference evaluator `tools/fleet_controls.py`, synthetic vectors in `examples/fleet-controls/`, and the conformance manifest `conformance/fleet-controls/manifest.json`.

This decision is the superseding governance decision required by the Program Baseline for work outside the locked sequence. It does not change the active increment, which remains the Second Independently Maintained Verifier.

The new claim `AAG-FLEET-001` has Delivery Status `DEFINED` and Evidence Status `NOT_YET_ESTABLISHED`. This decision promotes no claim.

## Version rationale

`v0.1.0-alpha.4` continues the experimental alpha line. The additions use new schema identities and a new profile; no released schema identity, profile, or signed example changes. The specification and schemas are not frozen.

## Profile hash anchor

The Agent Fleet Controls descriptor binds its profile document by `control_profile.hash`, the SHA-256 of the document bytes. The reference evaluator pins both that document hash and the descriptor's JCS hash outside every request. A request cannot redefine the maximum ages, depth cap, term levels, or Level 5 posture while keeping the profile identity. The Alpha.1 MCP Governance Profile anchor and the bundle that binds it are unchanged.

## Verifier target version

The independent-verifier reproduction kit stays pinned to its existing controlling commit on the `v0.1.0-alpha.2` line. The Agent Fleet Controls vectors target `v0.1.0-alpha.4` and are published separately in `conformance/fleet-controls/`. They are not added to the kit. Moving the kit target to `v0.1.0-alpha.4`, or adding these vectors to it, requires a separate steward decision.

## Preservation

The Alpha.1 generated distribution, the released schema identities and digests, the MCP Governance Profile, the signed examples, and the `v0.1.0-alpha.1`, `v0.1.0-alpha.2`, and `v0.1.0-alpha.3` tags remain unchanged.

## Assurance boundary

The DR-003 assurance boundary is unchanged. The Second Independently Maintained Verifier remains `PROPOSED / NOT_YET_ESTABLISHED`, and project-authored verification is not independent verification. The reference evaluator consumes already-verified facts, does not verify signatures, and performs no enforcement.

## Change control

Promoting Agent Fleet Controls, changing the kit target, or freezing these schemas requires a separate steward decision, release-gate evidence, and Claims Register update.
