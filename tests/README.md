<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Tests

The suite covers strict JSON input handling, RFC 8785 canonicalization, schema registration, supported versions, critical extensions, semantic consistency, complete bound-input verification, passport-summary consistency, content-derived identifiers, Ed25519 proofs, signing-key trust, validity, revocation chronology and authority, action-authority calculation, and deterministic CLI errors.

- `negative/` contains valid JSON artifacts that must be rejected by a designated schema, semantic, identifier, or protected-header validator.
- `cli-negative/` and generated CLI regressions cover malformed input, altered signatures, wrong identifiers, unusable keys, unsupported versions and critical extensions, incomplete or mismatched bindings, contradictory signed summaries, and invalid revocation state.

Every JSON file in `negative/` is registered in `negative/index.json`; unregistered or unexpectedly accepted fixtures fail repository verification.
The bound semantic-integrity tests rebuild identifiers, manifest hashes, bundle bindings, and Ed25519 signatures before asserting rejection of policy-anchor substitution, active-condition escalation, evidence-time mismatch, MCP-scope mismatch, tool-effect escalation, agent-capability escalation, and graph-edge contradiction.

