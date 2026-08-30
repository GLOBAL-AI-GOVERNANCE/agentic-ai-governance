<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DR-007: Stateful Revocation Alpha.2 Release and OPA Transition

**Status:** Accepted.

**Steward decision date:** August 30, 2026.

**Decision authority:** Global AI Governance steward.

## Decision

Approve `v0.1.0-alpha.2` as the next experimental Agentic AI Governance prerelease.

The release packages the complete verified post-`v0.1.0-alpha.1` repository delta at the protected release commit. This includes bounded Stateful Revocation continuity plus the Claims Register, continuous V&V, schema-catalog integrity, public-release scrub, and related repository-governance controls.

Promote `AAG-RVK-002` and `AAG-GOV-001` to Delivery Status `SHIPPED` while retaining Evidence Status `VERIFIED`, subject to the release gate passing on the exact release commit.

Close Stateful Revocation as the one active implementation increment and activate the OPA Enforcement Bridge as the next increment in the locked sequence. This decision does not implement OPA and does not establish OPA evidence.

## Version rationale

`v0.1.0-alpha.2` continues the existing experimental alpha line. The specification and schemas are not frozen, Alpha.1 remains immutable, and the delta does not justify a stable or minor-version maturity claim.

## Preservation

The Alpha.1 generated distribution and released schema identities remain unchanged. No release claim may retroactively attribute Stateful Revocation to Alpha.1.

## Assurance boundary

Stateful Revocation establishes local reference rollback-aware continuity only relative to an intact trusted local store. One revocation-state path is a single-writer reference continuity store; concurrent writers to the same path are outside the supported Alpha.2 boundary. It does not establish host/database anti-rollback, runtime containment, credential/session termination, production IAM, legal compliance, certification, universal safety, or independent reproduction.

## Change control

OPA implementation requires its own bounded engineering increment, protected review, tests, claims updates, and evidence. No subsequent roadmap increment is authorized by this release decision.
