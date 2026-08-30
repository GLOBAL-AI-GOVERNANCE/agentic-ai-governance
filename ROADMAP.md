<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Roadmap

## Active Priority

### OPA Enforcement Bridge

Stateful Revocation shipped in `v0.1.0-alpha.2` with Delivery Status `SHIPPED` and Evidence Status `VERIFIED`. Its claim remains bounded to rollback-aware continuity relative to an intact trusted local store.

The OPA Enforcement Bridge remains the one active implementation increment. Current `main` now contains a bounded reference implementation with Delivery Status `DEFINED` and Evidence Status `VERIFIED`. It is unreleased and no OPA implementation is included in `v0.1.0-alpha.2`.

The bridge consumes validated passport, authority, and revocation results plus bounded policy/context and emits the existing Agentic operating-disposition vocabulary with stable reason codes and evidence references. It does not duplicate passport validation or claim external enforcement.

The increment remains active pending a separate governance decision to close it and activate the lifecycle demonstration. Current-main verification does not create a release or authorize the next increment.

## Locked Sequence

1. **Stateful Revocation** — shipped and verified in `v0.1.0-alpha.2`.
2. **OPA Enforcement Bridge** — active increment; current-main verified, unreleased.
3. **Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized demonstration**.
4. **Second independently maintained verifier**.
5. **Agent Governance Decision Record Profile**.
6. **Infrastructure Trust Profile**.

## Continuing Interoperability

Cross-language RFC 8785 and signature vectors, implementation-independent conformance reports, and broader standards adapters remain important. They must support rather than interrupt the locked sequence.

Schema stabilization, version negotiation, migration guidance, media-type review, Sigstore, SLSA, in-toto, SCITT, transparency, and provenance integrations follow demonstrated lifecycle continuity and independent verification.

Authority vocabulary expands only through versioned profiles, canonical policy anchors, and adversarial regression fixtures.
