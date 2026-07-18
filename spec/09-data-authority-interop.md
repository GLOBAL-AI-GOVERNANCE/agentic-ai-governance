<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Data Authority Interoperability

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Boundary

Agentic AI Governance evaluates whether declared agent use is compatible with admitted data-authority evidence. It MUST NOT create, infer, or re-adjudicate underlying data rights.

## Generic evidence binding

A data-authority binding identifies evidence scheme and version, issuer, artifact hash, data classes, purposes, systems, jurisdictions, prohibited uses, and validity interval.

An adapter MUST validate supported scheme version, artifact integrity, issuer trust, signature when required, revocation, validity, scope, purposes, data classes, restrictions, and jurisdictional constraints.

## Absence or uncertainty

When required data-authority evidence is absent or cannot be verified, `data_authority_status` is `UNKNOWN`. The issued assessment MUST be `RESTRICTED` or `REJECTED`; it MUST NOT be `APPROVED` or `APPROVED_WITH_CONDITIONS`. Invalid authority evidence requires `data_authority_status = INVALID` and an issued result of `REJECTED`.

Omitting a data declaration does not make data-authority controls inapplicable when tools, MCP resources, or other declarations indicate governed data access.

## Alpha.1 reference adapter

The Alpha.1 reference profile admits only the synthetic scheme:

```text
global-ai-governance.synthetic-authority / 0.1.0
```

The machine-readable profile descriptor lists the supported scheme and trusted issuer. The reference verifier validates the evidence schema, semantic ordering, content-derived `artifact_hash`, subject, current validity, trusted issuer, declared-use scope, prohibited uses, and every assessment or condition evidence reference.

The synthetic scheme does not require a separate evidence signature because the complete bundle and evidence hash are bound by the issuer-signed passport. It is test-only and prohibits production use. Future operational adapters may require their own signatures, revocation state, delegation chains, jurisdictional rules, and external trust anchors.

A future profile may define a Data Trust Passport adapter. Alpha.1 has no external adapter dependency.
## Evidence-time and scheme-policy enforcement

Evidence supporting `data_authority_status: VERIFIED` MUST be valid both when the bound assessment was evaluated and at the verifier's presentation time. The supported scheme, issuer set, and `requires_signature` policy come from the independently pinned reference-policy anchor rather than from mutable bundle content.

