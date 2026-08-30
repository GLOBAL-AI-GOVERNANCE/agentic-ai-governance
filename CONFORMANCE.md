<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Conformance

**Release:** `v0.1.0-alpha.1`

The reference implementation performs strict JSON parsing, JSON Schema validation, semantic checks, content-derived identifier checks, detached Ed25519 signature verification, signing-key trust evaluation, bound-input verification, validity checks, and signed revocation evaluation.

Implemented passport trust checks include:

- distinct issued, verification, and operating state layers;
- supported framework, profile, evaluator, assessment-policy, and critical-extension decisions;
- canonical bundle-manifest identity, path, size, hash, and required-file verification;
- machine-readable profile identity, version, policy, evaluator, supported-control, trusted-issuer, and content-hash binding;
- Alpha.1 agent, MCP, and tool inventory schemas with subject and action-authority reconciliation;
- bidirectional equality between MCP inventory servers and reachable `MCP_SERVER` action-graph nodes;
- complete action-authority graph validation and recalculation;
- data-authority evidence schema, semantic, content-hash, validity, scheme, issuer, subject, scope, and evidence-reference verification;
- complete assessment projection and ordered condition equality;
- trusted-key, signature, validity, revocation chronology, revocation authority, and membership checks.

The Alpha.1 quickstart may report `fully_validated: true` only when every required declared artifact passes these checks. This remains structural and declared-evidence assurance. It does not prove factual claims, live-system state, legal rights, secure key custody, or production safety.

Every committed JSON vector in `tests/negative/` is registered in `tests/negative/index.json` and must be rejected. Additional signed regression tests rebuild dependent hashes, identifiers, bundle manifests, and signatures so earlier integrity failures cannot hide semantic defects.

Run:

```bash
python tools/build_dist.py --check
python tools/verify_repository.py .
python -m pip check
python -m pip_audit --strict -r requirements-dev.txt
pytest -q
```

## Unreleased current-main OPA bridge

The OPA Enforcement Bridge is a separately bounded current-main reference implementation, not part of the Alpha.1 normative distribution or the Alpha.2 release. Its Python adapter validates the local bridge contract; its OPA policy is verified with OPA v1.19.1 in every hosted Python matrix job. Positive and adversarial vectors confirm that policy cannot widen established authority and that invalid, stale, expired, revoked, unknown, incomplete, mismatched, or insufficiently contextualized inputs remain `NOT_PERMITTED`.

The bridge returns policy dispositions and stable reason codes. It performs no external enforcement and establishes no runtime containment.

## Unreleased current-main lifecycle demonstration

The synthetic Agent Incident Readiness trace composes established validator results, OPA bridge decisions, and Stateful Revocation continuity. Deterministic positive and adversarial tests cover policy denial without revocation, terminal revoked-passport rejection, rollback and same-sequence conflict rejection, unknown evidence, human-attribution failure, authority violations, stale input, malformed evidence, distinct new-passport reauthorization, and unsupported enforcement or containment claims.

This current-main demonstration is not part of `v0.1.0-alpha.2`, introduces no schema, and performs no external action.


## Canonical policy and authority semantics

A conforming Alpha.1 reference-validator run MUST verify the independently pinned profile descriptor and document hashes, apply every active condition maximum to the effective action ceiling, require data-authority evidence to be valid at assessment and verification time, and enforce the controlled capability, MCP-scope, tool-effect, and edge-type minimum levels.
