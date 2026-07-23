<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Verification and Validation Policy

**Status:** Controlling repository policy.

Verification and validation is part of design, engineering, release, and public communication. It is not a final review added after development.

## Three V&V Gates

### 1. Design Validation

Before implementation, establish:

- The problem and protected asset.
- The threat or failure condition.
- The responsible authority and trust boundary.
- The required evidence, stop condition, and recovery or reauthorization path.

Every normative field must support a governance decision, evidence requirement, enforcement condition, or recovery action. Convenience fields without a defined decision use are prohibited.

### 2. Engineering Verification

During implementation, require:

- Normative requirements and deterministic behavior.
- Positive, negative, and adversarial fixtures.
- Stable reason codes and non-regression tests.
- Cryptographic, identifier, binding, validity, and state checks where applicable.
- Reproducible machine-readable evidence outputs.

A probabilistic agent must not decide whether its own identity, authority, signature, validity, revocation, policy result, or enforcement disposition is valid. Those decisions require external deterministic evaluation.

### 3. Release Validation

Before public promotion, verify:

- Specification, schema, profile, examples, implementation, and generated distribution agree.
- Hosted CI reports success on every supported runtime.
- Release artifacts, checksums, evidence, limitations, and reproduction instructions are complete.
- Public wording matches the Claims Register.
- Public fixtures expose no protected information.
- Logged-out users may reproduce the documented public workflow.

Automated prohibited-wording checks are case-insensitive exact-phrase scans over explicitly governed repository paths. The authoritative path scope and exclusions are the `repository_globs` and `repository_exclusions` fields in `governance/prohibited-claims.yaml`. The checks do not detect paraphrases, punctuation variants, split wording, or semantically equivalent claims. Human release review remains mandatory.

## Approval Authority

Maintainers review technical conformance. The Global AI Governance steward approves changes to program sequencing, public status, and release promotion. Neither implementation code nor validation tooling may silently promote a claim.

## Status Promotion

A capability remains `PROPOSED` until its requirements are defined. It becomes `DEFINED` when the normative design and acceptance criteria are controlled. It becomes `SHIPPED` only after public release.

A claim remains `NOT_YET_ESTABLISHED` until evidence supports the exact bounded statement. It becomes `VERIFIED` only at the scope demonstrated by that evidence.

## Stop Conditions

Work must stop for correction when any of these occur:

1. A change silently alters an immutable Alpha.1 artifact or identifier.
2. A false-permit path, nondeterministic normative outcome, rollback acceptance, or unbounded claim is found.
3. Required evidence, public-safe fixtures, or a deterministic test path cannot be produced.

## Assurance Boundary

A valid signature authenticates an artifact. It does not prove every statement inside the artifact is true.

A passing validation result proves conformity to the implemented profile and supplied evidence. It does not prove universal safety, legality, institutional approval, production readiness, or complete behavioral trustworthiness.
