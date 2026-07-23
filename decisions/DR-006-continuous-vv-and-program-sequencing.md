<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DR-006: Continuous V&V and Program Sequencing

**Status:** Accepted.

**Steward decision date:** July 22, 2026.

**Decision authority:** Global AI Governance steward.

## Decision

Verification and validation is a continuous operating requirement across design, engineering, release, and public communication.

The project will maintain one active implementation increment at a time. The active increment is:

> **Stateful Revocation: From Signed Snapshot to Trusted Lifecycle State**

The locked sequence is:

1. Stateful Revocation.
2. OPA Enforcement Bridge.
3. Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized demonstration.
4. Second independently maintained verifier.
5. Agent Governance Decision Record Profile.
6. Infrastructure Trust Profile.

No new repository will be created for non-human identity lifecycle, infrastructure trust, accountable decision records, or the requirements derived from those analyses. Canonical passport, authority, verification, and revocation semantics remain in `agentic-ai-governance`.

## Claims Discipline

Project capabilities use Delivery Status `PROPOSED`, `DEFINED`, or `SHIPPED`. Claims use Evidence Status `NOT_YET_ESTABLISHED` or `VERIFIED`. External facts omit Delivery Status. No partial or implicit sixth status is permitted.

## Rationale

Alpha.1 already publishes signed cumulative revocation semantics but its reference CLI does not preserve trusted sequence state across executions. Closing that exact gap is the narrowest complete movement from a signed snapshot toward trustworthy lifecycle state.

Parallel implementation would duplicate authority semantics, divide review capacity, and create incompatible sources of truth. Requirements concerning human ownership, telemetry, accountable decisions, operational containment, infrastructure placement, and assurance remain valuable but enter through the locked sequence.

## Assurance Boundary

Stateful Revocation Priority One will preserve unchanged Alpha.1 list artifacts and remain bounded to rollback detection relative to an intact trusted local store. It will not claim host-level anti-rollback, operational containment, production safety, certification, legal compliance, or universal interoperability.

## Change Control

A change to the active increment, locked sequence, claims model, or repository ownership requires a dated superseding governance decision, updated Claims Register entries, and applicable specification, schema, test, and release-gate changes.
