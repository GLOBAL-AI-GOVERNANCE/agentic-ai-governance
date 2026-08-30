<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Roadmap

## Active Priority

### Stateful Revocation: From Signed Snapshot to Trusted Lifecycle State

Preserve the Alpha.1 revocation-list contract while adding an explicitly initialized, rollback-aware persistent reference verifier. The increment must retain trusted state across normal process restarts, reject broken continuity, return unknown status when current state cannot be established, and keep revoked passports terminally revoked.

Current main now contains the verified local reference implementation and subprocess regressions. Stateful Revocation remains Delivery Status `DEFINED` and Evidence Status `VERIFIED`; the increment remains active, and the implementation remains unreleased until a separate governed release. The OPA Enforcement Bridge remains locked as the next planned increment and has not begun.

## Locked Sequence

1. **Stateful Revocation**
2. **OPA Enforcement Bridge**
3. **Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized demonstration**
4. **Second independently maintained verifier**
5. **Agent Governance Decision Record Profile**
6. **Infrastructure Trust Profile**

## Continuing Interoperability

Cross-language RFC 8785 and signature vectors, implementation-independent conformance reports, and broader standards adapters remain important. They must support rather than interrupt the locked sequence.

Schema stabilization, version negotiation, migration guidance, media-type review, Sigstore, SLSA, in-toto, SCITT, transparency, and provenance integrations follow demonstrated lifecycle continuity and independent verification.

Authority vocabulary expands only through versioned profiles, canonical policy anchors, and adversarial regression fixtures.
