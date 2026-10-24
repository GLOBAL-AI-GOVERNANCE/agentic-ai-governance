<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Roadmap

## Active Priority

### Second Independently Maintained Verifier

Stateful Revocation shipped in `v0.1.0-alpha.2` with Delivery Status `SHIPPED` and Evidence Status `VERIFIED`. Its claim remains bounded to rollback-aware continuity relative to an intact trusted local store.

The OPA Enforcement Bridge engineering increment is governance-closed by `DR-008`. Its bounded reference implementation has Delivery Status `DEFINED` and Evidence Status `VERIFIED`. It is included in the `v0.1.0-alpha.3` source and is not promoted to a shipped capability.

The bridge consumes validated passport, authority, and revocation results plus bounded policy/context and emits the existing Agentic operating-disposition vocabulary with stable reason codes and evidence references. It does not duplicate passport validation or claim external enforcement.

The synthetic **Agent Incident Readiness** lifecycle demonstration is governance-closed by `DR-009`: Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized. It remains Delivery Status `DEFINED` and Evidence Status `VERIFIED`; it is included in the `v0.1.0-alpha.3` source and is not promoted.

Policy denial does not mutate revocation state. A revoked passport cannot be restored; reauthorization requires a new governed passport. OPA produces a policy decision, not external enforcement. Human authority remains explicit.

Priority 4, **Second Independently Maintained Verifier**, is now the active external increment at Delivery Status `PROPOSED` and Evidence Status `NOT_YET_ESTABLISHED`. A second project-authored or otherwise same-control-boundary implementation does not satisfy the gate. Evidence must come from a genuinely separate maintainer and control boundary.

## Locked Sequence

1. **Stateful Revocation** — shipped and verified in `v0.1.0-alpha.2`.
2. **OPA Enforcement Bridge** — governance-closed increment; verified reference included in `v0.1.0-alpha.3`, not promoted.
3. **Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized demonstration** — governance-closed; verified synthetic Agent Incident Readiness scenario included in `v0.1.0-alpha.3`, not promoted.
4. **Second independently maintained verifier** — active external increment; `PROPOSED / NOT_YET_ESTABLISHED`; waiting on genuinely external independent maintenance.
5. **Agent Governance Decision Record Profile**.
6. **Infrastructure Trust Profile**.

## Continuing Interoperability

Cross-language RFC 8785 and signature vectors, implementation-independent conformance reports, and broader standards adapters remain important. They must support rather than interrupt the locked sequence.

Schema stabilization, version negotiation, migration guidance, media-type review, Sigstore, SLSA, in-toto, SCITT, transparency, and provenance integrations follow demonstrated lifecycle continuity and independent verification.

Authority vocabulary expands only through versioned profiles, canonical policy anchors, and adversarial regression fixtures.
