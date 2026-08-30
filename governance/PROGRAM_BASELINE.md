<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Program Baseline

**Status:** Controlling project baseline.

**Effective date:** July 22, 2026.

**Decision authority:** Global AI Governance steward.

## Purpose

This index identifies the controlling architecture, active increment, normative precedence, claims model, and release sequence for Agentic AI Governance. It does not replace the versioned specification, schemas, profiles, or accepted decision records.

## Controlling System

> **TRUST CORE → ENFORCEMENT BRIDGE → RECOVERY LOOP**

## Controlling Doctrine

> **BOUND → VERIFY → RECOVER**

## Controlling Execution Sequence

> **INVENTORY → INTEGRATE → IMPLEMENT**

## One Active Increment

The active external increment authorized by `DR-009` is:

> **SECOND INDEPENDENTLY MAINTAINED VERIFIER**

Agent Incident Readiness is governance-closed at its verified unreleased boundary. Priority 4 remains `PROPOSED / NOT_YET_ESTABLISHED` pending attributable evidence from a genuinely separate maintainer and control boundary. Project- or Codex-authored verification is not independent verification. No AGDR, Infrastructure Trust, or later-roadmap implementation may interrupt this gate without a superseding governance decision.

## Normative Precedence

When project artifacts conflict, use this order:

1. Versioned JSON Schema and normative specification.
2. Versioned profile and accepted architecture decision.
3. Governance and sequencing decision.
4. This program baseline index.
5. Operations guidance, examples, implementation code, and README material.

A README, example, test helper, or implementation behavior may not silently change a normative rule.

## Claims Model

Project claims use two independent dimensions.

### Delivery Status

- `PROPOSED`
- `DEFINED`
- `SHIPPED`

### Evidence Status

- `NOT_YET_ESTABLISHED`
- `VERIFIED`

External facts omit Delivery Status. Broad or partially supported statements must be divided into atomic claims rather than assigned an additional status.

## Locked Program Sequence

1. Stateful Revocation.
2. OPA Enforcement Bridge.
3. Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized demonstration.
4. Second independently maintained verifier.
5. Agent Governance Decision Record Profile.
6. Infrastructure Trust Profile.

Broader Sigstore, SLSA, in-toto, SCITT, transparency, and provenance integrations follow the six priorities unless a documented dependency requires earlier work.

## Portfolio Boundary

Agentic AI Governance remains canonical for passports, evidence bindings, authority, verification, validity, revocation, and reauthorization boundaries. Adjacent repositories may consume these semantics but must not redefine them.

- `global-ai-governance-toolkit`: govern and measure.
- `ai-cyber-resilience-framework`: contain and recover.
- `verified-vulnerability-governance`: verify and close.

## Current Boundary

Agentic AI Governance `v0.1.0-alpha.2` is a verified experimental prerelease within its published boundary. The Alpha.1 normative distribution remains preserved.

Stateful Revocation is:

```text
Delivery Status: SHIPPED
Evidence Status: VERIFIED
```

The released evidence is the optional local reference continuity implementation and subprocess regression suite. It establishes rollback-aware continuity only relative to an intact explicitly supplied trusted local store. One revocation-state path is a single-writer reference continuity store; concurrent writers to the same path are outside the supported Alpha.2 boundary.

The OPA Enforcement Bridge engineering increment is governance-closed by `DR-008`. Its bounded current-main reference implementation remains:

```text
Delivery Status: DEFINED
Evidence Status: VERIFIED
```

The evidence is the current-main Python adapter, OPA policy, synthetic vectors, adversarial tests, and hosted OPA verification. The bridge remains unreleased and is not part of Alpha.2. It performs a policy decision only; no runtime enforcement or external containment claim is established.

The bridge remains unreleased current-main development. `v0.1.0-alpha.2` remains the current public release, no new release identity is selected, and no release is authorized.

The lifecycle demonstration is governance-closed by `DR-009` with objective current-main reference evidence:

```text
Delivery Status: DEFINED
Evidence Status: VERIFIED
```

Policy denial is not passport revocation. A revoked passport is not restorable. New authorization requires a new governed passport. An OPA policy decision is not external enforcement. Human authority remains explicit.

The evidence is the deterministic synthetic Agent Incident Readiness trace, reference orchestrator, human-readable walkthrough, and adversarial regressions. It is unreleased and non-operational.

The Second Independently Maintained Verifier is the active external increment:

```text
Delivery Status: PROPOSED
Evidence Status: NOT_YET_ESTABLISHED
```

Independent maintenance requires a genuinely separate maintainer and control boundary. Neutral reproduction material prepared by this project does not establish independent verification. AGDR and Infrastructure Trust remain deferred, `v0.1.0-alpha.2` remains the current release, and no new release is authorized.

## Change Control

Changes to the active increment, locked sequence, claims statuses, normative precedence, or public assurance boundary require:

1. A dated governance decision.
2. Claims Register updates.
3. Applicable specification, schema, test, and release-gate changes.
