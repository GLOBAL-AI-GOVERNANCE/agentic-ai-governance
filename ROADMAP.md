<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Roadmap

## Active Priority

### Agent Incident Readiness

Stateful Revocation shipped in `v0.1.0-alpha.2` with Delivery Status `SHIPPED` and Evidence Status `VERIFIED`. Its claim remains bounded to rollback-aware continuity relative to an intact trusted local store.

The OPA Enforcement Bridge engineering increment is governance-closed by `DR-008`. Current `main` contains its bounded reference implementation with Delivery Status `DEFINED` and Evidence Status `VERIFIED`. It remains unreleased and no OPA implementation is included in `v0.1.0-alpha.2`.

The bridge consumes validated passport, authority, and revocation results plus bounded policy/context and emits the existing Agentic operating-disposition vocabulary with stable reason codes and evidence references. It does not duplicate passport validation or claim external enforcement.

The active synthetic **Agent Incident Readiness** lifecycle demonstration is implemented on current `main`: Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized. It is Delivery Status `DEFINED`, Evidence Status `VERIFIED`, and unreleased.

Policy denial does not mutate revocation state. A revoked passport cannot be restored; reauthorization requires a new governed passport. OPA produces a policy decision, not external enforcement. Human authority remains explicit.

## Locked Sequence

1. **Stateful Revocation** — shipped and verified in `v0.1.0-alpha.2`.
2. **OPA Enforcement Bridge** — governance-closed increment; current-main verified, unreleased.
3. **Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized demonstration** — current-main verified, unreleased synthetic Agent Incident Readiness scenario.
4. **Second independently maintained verifier** — waiting on genuinely external independent maintenance; project-authored work cannot satisfy this gate.
5. **Agent Governance Decision Record Profile**.
6. **Infrastructure Trust Profile**.

## Continuing Interoperability

Cross-language RFC 8785 and signature vectors, implementation-independent conformance reports, and broader standards adapters remain important. They must support rather than interrupt the locked sequence.

Schema stabilization, version negotiation, migration guidance, media-type review, Sigstore, SLSA, in-toto, SCITT, transparency, and provenance integrations follow demonstrated lifecycle continuity and independent verification.

Authority vocabulary expands only through versioned profiles, canonical policy anchors, and adversarial regression fixtures.
