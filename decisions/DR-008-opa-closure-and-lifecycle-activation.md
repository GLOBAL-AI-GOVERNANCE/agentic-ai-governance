<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DR-008: OPA Closure and Lifecycle Activation

**Status:** Accepted.

**Steward decision date:** August 30, 2026.

**Decision authority:** Global AI Governance steward.

## Decision

Close the OPA Enforcement Bridge engineering increment at Delivery Status `DEFINED` and Evidence Status `VERIFIED`. The implementation remains unreleased current-main development. `v0.1.0-alpha.2` remains the current public Agentic AI Governance release; this decision selects no new release identity and authorizes no release.

Activate the locked lifecycle demonstration as the one active implementation increment:

> Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized

Its human-facing synthetic scenario is **Agent Incident Readiness**. At activation, `AAG-LIFECYCLE-001` remains Delivery Status `PROPOSED` and Evidence Status `NOT_YET_ESTABLISHED` until objective implementation evidence exists.

The second independently maintained verifier remains a later, external increment. A verifier maintained by this project, its operator, or the implementation agent does not establish that independence.

## Invariants

- Policy denial is not passport revocation.
- A revoked passport is not restorable.
- New authorization requires a new governed passport.
- An OPA policy decision is not external enforcement.
- Human authority remains explicit.

## Assurance boundary

This decision does not establish runtime enforcement, containment, IAM, credential or session termination, autonomous restoration, production effectiveness, certification, compliance, or independent verification.

## Change control

The lifecycle demonstration requires a bounded engineering increment, deterministic synthetic evidence, adversarial regression coverage, claims updates only after verification, and protected review. No later roadmap increment is authorized by this decision.
