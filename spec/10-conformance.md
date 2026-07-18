<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Conformance

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Conformance classes

- `SCHEMA_CONFORMANT`: artifact validates against the identified schema.
- `SEMANTIC_CONFORMANT`: artifact also satisfies ordering, identifier, branch, timing, cross-reference, and result-consistency rules.
- `CRYPTO_CONFORMANT`: signed artifact satisfies the protected-header, signing-input, key, and signature profile.
- `REFERENCE_POLICY_CONFORMANT`: verification and operating mapping match the reference fail-closed policy.

Schema conformance alone does not imply semantic, cryptographic, operational, or security conformance.

## Bundled evidence

The repository includes canonical JSON vectors, valid examples, negative fixtures, passport and revocation identifiers, signed and unsigned branches, deterministic Ed25519 detached JWS fixtures, timestamp boundaries, supported-version and critical-extension decisions, machine-readable profile descriptors, inventory schemas, complete bound-input verification, data-authority evidence admission, evidence-reference resolution, complete condition equality, action-authority graph reconciliation, revocation chronology and authority controls, bundle-path controls, operating mappings, and content-derived identifier checks.

Every JSON fixture in `tests/negative/` MUST be listed in `tests/negative/index.json` and rejected by the designated validator.

## Determinism

Fixtures use exact UTF-8 bytes and committed expected hashes. Test-only cryptographic keys are explicitly labeled and MUST NOT be used operationally.

## Assurance boundary

A green repository test run demonstrates consistency of the bundled examples and implemented reference-validation subset. It does not prove factual declarations, live-system state, secure key custody, legal compliance, institutional authorization, or production safety.
