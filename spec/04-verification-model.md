<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Verification Model

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Verification components

A verification result reports:

```text
structure
version
identifier
critical_extensions
signature
signing_key
issuer_authentication
bindings
revocation
validity
conditions
```

Component values are `PASS`, `FAIL`, `NOT_APPLICABLE`, `NOT_PRESENT`, `NOT_ESTABLISHED`, or `UNKNOWN`.

## Primary statuses

```text
VALID
INVALID_STRUCTURE
UNSUPPORTED_VERSION
INVALID_IDENTIFIER
UNSUPPORTED_CRITICAL_EXTENSION
INVALID_SIGNATURE
UNKNOWN_SIGNING_KEY
UNTRUSTED_ISSUER
BOUND_INPUTS_UNAVAILABLE
BOUND_INPUTS_INCOMPLETE
INPUT_MISMATCH
UNSUPPORTED_PROFILE
UNSUPPORTED_EVALUATOR
UNSUPPORTED_POLICY
DATA_AUTHORITY_UNKNOWN
DATA_AUTHORITY_INVALID
SIGNING_KEY_REVOKED
SIGNING_KEY_COMPROMISED
SIGNING_KEY_NOT_YET_VALID
SIGNING_KEY_EXPIRED
REVOKED
REVOCATION_STATUS_UNKNOWN
NOT_YET_VALID
EXPIRED
```

`CONDITION_OVERDUE` is not a primary status. It is a diagnostic finding indicating malformed issuance or historical analysis because a conditional passport must expire no later than its earliest condition deadline.

## Evaluation order

The verifier evaluates:

1. JSON, schema, and canonical-data structure.
2. supported versions.
3. passport identifier.
4. critical extensions.
5. signed or unsigned branch.
6. signing key and issuer trust for signed artifacts.
7. bound-input availability, completeness, profile support, and equality.
8. data-authority evidence, inventory, action-authority, assessment projection, condition, and evidence-reference consistency.
9. revocation-list trust, freshness, chain state, and membership.
10. `not_before` and `expires_at`.

The first failure in this order determines the primary status, except a confirmed `REVOKED`, `SIGNING_KEY_REVOKED`, or `SIGNING_KEY_COMPROMISED` result overrides later time checks.

## Unsigned artifacts

For an unsigned passport:

```yaml
signature: NOT_PRESENT
signing_key: NOT_APPLICABLE
issuer_authentication: NOT_ESTABLISHED
```

The passport may receive primary status `VALID` if all requirements applicable to its declared unsigned branch pass. `VALID` does not mean issuer-authenticated.

## Reference CLI state fields

For passport validation, the reference CLI emits these state layers separately:

```text
issued_assessment_result
verification_primary_status
operating_disposition
```

The CLI MUST NOT substitute one generic `decision` field for these values. A signed, trusted, unrevoked passport with issued result `APPROVED` reports `APPROVED / VALID / PERMITTED`. A structurally valid unsigned passport may report `APPROVED / VALID / INDETERMINATE`. A revoked passport reports its issued result, verification status `REVOKED`, and operating disposition `NOT_PERMITTED`.

For non-passport artifacts, these passport-specific fields are `null` unless the artifact itself is an assessment or verification result. `artifact_validation_status` reports whether the implemented parsing, schema, semantic, and identifier checks passed; it does not replace the three passport state layers.

## Binding outcomes

- `BOUND_INPUTS_UNAVAILABLE`: no required bundle was supplied.
- `BOUND_INPUTS_INCOMPLETE`: a bundle was supplied but one or more required bound artifacts are missing.
- `INPUT_MISMATCH`: all required artifacts are present and one or more hashes, cross-artifact identifiers, projections, conditions, references, inventory declarations, or action-authority values differ.
- `UNSUPPORTED_PROFILE`: the declared or bound profile identity or version is not admitted by the Alpha.1 reference policy.
- `UNSUPPORTED_EVALUATOR`: the declared evaluator identity or version is not supported.
- `UNSUPPORTED_POLICY`: the declared assessment-policy identity or version is not supported.
- `DATA_AUTHORITY_UNKNOWN`: the evidence scheme or issuer is not supported or trusted.
- `DATA_AUTHORITY_INVALID`: admitted evidence is malformed, expired, internally inconsistent, not applicable to the subject or declared use, or fails its content-derived artifact hash.

The Alpha.1 reference CLI requires both `--bundle-manifest` and `--bundle-root` for passport validation. It MUST NOT emit `fully_validated: true` or a permitted operating disposition until the manifest, profile descriptor, profile document, inventories, action-authority graph, data-authority evidence, assessment projection, conditions, and evidence references all pass.

## Reference operating policy

Issued result and primary status are combined under institutional policy.

- `APPROVED + VALID + ISSUER_SIGNED` maps to `PERMITTED` when the issuer and scope are trusted.
- `APPROVED_WITH_CONDITIONS + VALID` maps to `PERMITTED_WITH_CONDITIONS` only when every active condition is enforceable.
- `RESTRICTED + VALID` maps to `RESTRICTED`.
- `REJECTED` maps to `NOT_PERMITTED`.
- `VALID + NONE` maps to `INDETERMINATE` by default and `NOT_PERMITTED` under fail-closed policy.
- Every non-`VALID` primary status maps to `NOT_PERMITTED` under fail-closed policy.

No policy may represent `REVOCATION_STATUS_UNKNOWN` as evidence that a passport is not revoked.
## Independently anchored reference policy

For the bundled Alpha.1 reference profile, the verifier MUST compare the supplied profile descriptor and profile document with independently pinned canonical hashes. The submitted bundle MUST NOT redefine supported controls, issuers, schemes, signature requirements, evaluator identity, assessment policy, or production posture while retaining the same profile ID and version. A mismatch produces `UNSUPPORTED_PROFILE` or another non-permitted status.

