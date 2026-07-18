<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Assessment Model

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Three-layer model

The framework maintains three separate decisions:

1. `issued_assessment_result`, immutable after issuance.
2. `verification.primary_status`, calculated when an artifact is presented.
3. `operating_disposition`, calculated under current institutional policy.


They MUST NOT be collapsed into one field.

```text
Assessment issuance                    Presentation-time verification
┌─────────────────────────┐            ┌─────────────────────────────┐
│ issued_assessment_result│ ─────────► │ verification.primary_status │
└─────────────────────────┘            └──────────────┬──────────────┘
                                                     │ current policy
                                                     ▼
                                      ┌─────────────────────────────┐
                                      │ operating_disposition       │
                                      └─────────────────────────────┘
```

The first value records what the issuer decided. The second records whether the presented artifact verifies now. The third records what the relying institution permits now.

## Issued assessment result

Permitted values are:

```text
APPROVED
APPROVED_WITH_CONDITIONS
RESTRICTED
REJECTED
```

`APPROVED` requires every applicable mandatory control to pass, all required evidence to be present, no unresolved condition, no prohibited capability, and no more-restrictive aggregation result.

`APPROVED_WITH_CONDITIONS` requires explicit condition owner, deadline, measurable closure evidence, temporary restriction, and compensating controls. The passport MUST expire no later than the earliest condition deadline.

`RESTRICTED` applies when the requested scope is not conformant but a narrower declared scope remains possible, including missing evidence, `NOT_EVALUATED` mandatory controls, unknown data authority, or a requested Level 5 capability that is not directly prohibited.

`REJECTED` applies when submitted declarations establish an unacceptable or contradictory configuration, a critical mandatory control fails, a prohibited capability is declared, or a Level 5 action is explicitly prohibited.

## Control outcomes

Every evaluated control produces exactly one of:

```text
PASS
FAIL
NOT_APPLICABLE
NOT_EVALUATED
ERROR
```

The submitter MUST NOT directly select `NOT_APPLICABLE`. A closed evaluator-supported applicability predicate determines it.

An `ERROR` in a mandatory critical control produces `REJECTED`. An `ERROR` in another mandatory control produces at least `RESTRICTED`.

Aggregation order is:

```text
REJECTED > RESTRICTED > APPROVED_WITH_CONDITIONS > APPROVED
```

## Data-authority status

Each issued assessment records exactly one `data_authority_status`:

```text
VERIFIED
UNKNOWN
INVALID
NOT_APPLICABLE
```

`UNKNOWN` permits only `RESTRICTED` or `REJECTED`. `INVALID` requires `REJECTED`. `NOT_APPLICABLE` may be used only when the selected profile determines through a closed applicability rule that no governed data authority is required.

## Assurance vector

Assurance is multidimensional:

```yaml
assurance:
  evidence_basis: DECLARED
  validation_method: STRUCTURAL
  attestation_status: NONE
```

Alpha.1 supports only `DECLARED` evidence basis and `STRUCTURAL` validation method. It supports `NONE` and `ISSUER_SIGNED` attestation status and MUST NOT issue `THIRD_PARTY_ATTESTED`.

An issuer signature protects integrity and authenticates the signing key under a trust policy. It does not prove that submitted declarations are true.


## Assessment identifier

`assessment_id` is content-derived from the complete assessment without `assessment_id`:

```text
assessment_id = sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agentic-assessment.identifier.v1",
    "assessment": assessment_without_assessment_id
  }))
)
```

The required `sha256:` prefix is part of the identifier.

## Deterministic time

Assessment time MUST be injected. Core assessment logic MUST NOT directly call a wall clock. Given identical inputs, versions, evaluation time, profile, and signing configuration, unsigned output MUST be byte-identical. Ed25519 signed output is deterministic for identical signing input and key.
