<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Changelog

## Unreleased

- Added a bounded, non-enforcing OPA bridge reference adapter, policy, synthetic vectors, stable reason codes, adversarial tests, and hosted OPA v1.19.1 verification. The implementation consumes established validation results, preserves canonical operating dispositions, and remains unreleased.

## v0.1.0-alpha.2 - 2026-08-30

- Added an explicitly initialized, atomic local revocation continuity store to the reference verifier, with subprocess regressions for restart persistence, monotonic chaining, fail-closed corruption and freshness handling, and terminal cumulative revocation. This Alpha.2 reference capability provides rollback detection only relative to an intact trusted local store.
- Added a regression-checked sole-public-project-identity statement for GLOBAL AI GOVERNANCE.
- Established continuous V&V, one-active-increment sequencing, and the Stateful Revocation-first public roadmap.
- Added machine-readable Claims Register, prohibited-claims controls, and mixed-version schema catalog governance.
- Preserved the Alpha.1 generated distribution while making the distribution builder extensible to separately versioned future profiles.
- Added repository enforcement and tests for governance, claims, schema-catalog, and generated-distribution integrity.
- Enforced evidence references, verification method, and verification date for every `VERIFIED` claim.
- Added deterministic prohibited-wording scans for declared repository paths while retaining release review for external surfaces.
- Added catalog-wide local and cross-schema `$ref` resolution plus protected baseline schema identities.
- Recorded the steward-approved Alpha.2 release decision, promoted released current-main claims where justified, and advanced the one-active-increment program boundary to OPA without implementing OPA.

## v0.1.0-alpha.1

- Added semantic evidence admission, profile descriptors, inventory schemas, action-authority binding, complete condition equality, and evaluator/policy support checks.
- Added signed adversarial regressions for expired or untrusted evidence, unresolved references, profile drift, unsupported evaluator or policy metadata, destructive action graphs, and inventory-subject mismatch.
- Added pinned `pip-audit` to the connected CI gate.
- Enforced bidirectional equality between declared MCP inventory servers and reachable `MCP_SERVER` action-graph nodes.
- Published the experimental specification, versioned schemas, reusable profile, and synthetic examples.
- Added strict JSON parsing, RFC 8785 canonicalization, content-derived identifiers, and Ed25519 detached-JWS verification.
- Added assessment, verification-result, revocation, validity, signing-key, and action-authority consistency checks.
- Enforced the assessment `data_authority_status` result cap and added versioned Alpha.1 inventory schemas.
- Renamed the revoked passport example to `signed-revoked.json` to remove quickstart ambiguity.
- Added public governance decision records for stewardship, licensing, assurance, decision states, and release sequencing.
- Recorded the steward-approved release-sequencing supersession in DR-005, limiting release dependencies to explicitly documented causal dependencies.
- Added a complete signed-passport trust command with structured errors and fail-closed decisions.
- Separated issued assessment result, verification primary status, and operating disposition in the public CLI output.
- Added positive, negative, malformed-input, and trust-policy regressions across Python 3.11–3.13 CI.
- Added fail-closed bound-input verification for the canonical bundle manifest, inventories, control profile, data-authority evidence, and assessment summary.
- Rejected unknown critical extensions, contradictory passport summaries, unsupported versions, invalid revocation chronology, unrelated revocation authorities, and unusable Ed25519 verification keys.
- Replaced empty inventory placeholders in the quickstart with non-empty synthetic inventories and reconciled every passport binding.
- Updated GitHub Actions to SHA-pinned Node 24-compatible official releases.
- Pinned `cryptography==49.0.0` and `pytest==9.0.3` for the public-alpha validation environment.

- Closed the final policy-anchor and authority-semantics findings by pinning canonical profile hashes, enforcing condition ceilings, validating evidence at assessment and verification time, and mapping controlled capabilities, MCP scopes, tool effects, and graph edges to minimum action levels.
