<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DR-010: Alpha.3 Packaging Release

**Status:** Accepted.

**Steward decision date:** October 24, 2026.

**Decision authority:** Global AI Governance steward.

## Decision

Approve `v0.1.0-alpha.3` as the next experimental Agentic AI Governance prerelease.

The release makes the reference Passport validator installable from the release tag and from the release archive. `v0.1.0-alpha.2` predates the package metadata and cannot be installed with `pip`.

The release packages the repository at the protected release commit. That source includes the OPA Enforcement Bridge, the synthetic Agent Incident Readiness demonstration, and the Zero Trust Agent Readiness and Intelligence Assurance Gateway mappings.

This decision promotes no claim. `AAG-OPA-001`, `AAG-LIFECYCLE-001`, `AAG-ZTAR-001`, and `AAG-IA-001` keep Delivery Status `DEFINED` and Evidence Status `VERIFIED`. They are included in the release source as references, not as shipped capabilities. Interface identifiers such as policy version `1.0.0-unreleased` stay unchanged and continue to mark those interfaces as unpromoted.

## Version rationale

`v0.1.0-alpha.3` continues the experimental alpha line. The specification and schemas are not frozen, and the released schema identities remain those of `v0.1.0-alpha.2`.

## Preservation

The Alpha.1 generated distribution, the released schema identities, and the `v0.1.0-alpha.1` and `v0.1.0-alpha.2` tags remain unchanged.

## Assurance boundary

The DR-003 assurance boundary is unchanged. The Second Independently Maintained Verifier remains `PROPOSED / NOT_YET_ESTABLISHED`, and project-authored verification is not independent verification.

## Change control

Promoting any reference included in this release requires a separate steward decision, release-gate evidence, and Claims Register update.
