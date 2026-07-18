<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agent Trust Passport

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Structure

An Agent Trust Passport contains:

```text
schema_version
framework
profile
passport_id
issuer
subject
issued_assessment
assurance
bindings
validity
conditions
extensions
critical_extensions
proof, only for signed passports
```

The JSON Schema defines separate signed and unsigned branches.

## Unsigned branch

An unsigned passport MUST use `assurance.attestation_status = NONE` and MUST omit `proof`.

## Signed branch

A signed passport MUST use `assurance.attestation_status = ISSUER_SIGNED` and MUST contain exactly:

```json
{
  "proof": {
    "jws": "<protected-header>..<signature>"
  }
}
```

Outer `algorithm`, `key_id`, `format`, `typ`, and `cty` fields are prohibited. The protected JWS header is the only cryptographic source of truth.

## Identifier

The identifier source is the complete passport without `passport_id` and `proof`.

```text
passport_id = sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agent-trust-passport.identifier.v1",
    "passport": passport_without_passport_id_and_proof
  }))
)
```

The signed payload is the complete passport without `proof`, including `passport_id`.

## Conditions

Conditions are set-like and sorted by `condition_id`. Each condition requires owner, deadline, required evidence, temporary restriction, and closure rule. `expires_at` MUST be earlier than or equal to the earliest condition deadline.

## Extensions

Extension members appear only inside `extensions`. `critical_extensions` is a sorted set of extension keys that must be understood. Every critical extension key MUST exist in `extensions`.

## Bindings

A passport binds to the assessment bundle, action-authority graph, agent inventory, MCP inventory, tool inventory, control profile, machine-readable profile descriptor, evaluator identity and version, assessment-policy identity and version, framework and profile versions, evaluation time, assurance vector, issued result, issuer identity, and all admitted data-authority evidence hashes.

The `issued_assessment` projection includes the bound assessment identifier and data-authority status. The passport condition array MUST equal the complete ordered condition array in the bound assessment. Any semantic change to a bound input requires a new assessment and passport.

### Alpha.1 inventory and profile boundary

Alpha.1 defines minimal agent-, MCP-, and tool-inventory schemas. The reference verifier validates their structure, subject identity, set ordering, non-production declaration, tool-to-graph agreement, and action-level consistency.

The profile descriptor is machine readable. It binds the profile ID and version, assessment policy, evaluator, supported controls, supported data-authority schemes, trusted data-authority issuers, production-use posture, and exact control-profile document hash.

The quickstart uses non-empty synthetic inventories. The SHA-256 hash of JCS-canonical `{}` MUST NOT support a permitted Alpha.1 decision.
