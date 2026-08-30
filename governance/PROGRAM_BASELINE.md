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

The only active implementation increment is:

> **STATEFUL REVOCATION: FROM SIGNED SNAPSHOT TO TRUSTED LIFECYCLE STATE**

No parallel identity-lifecycle, infrastructure-trust, runtime-containment, or decision-record implementation may interrupt this increment without a superseding governance decision.

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

Agentic AI Governance Alpha.1 is a verified experimental open-source foundation within its published boundary. GitHub reports hosted conformance success. Independent clean-room reproduction of the current public repository and production assurance remain separately classified.

Stateful Revocation remains:

```text
Delivery Status: DEFINED
Evidence Status: VERIFIED
```

The verified evidence is the post-`v0.1.0-alpha.1`, current-main optional local reference implementation and subprocess regression suite. It establishes rollback-aware continuity only relative to an intact explicitly supplied trusted local store. It remains unreleased pending a separate governed release; Delivery Status therefore remains `DEFINED`, and Stateful Revocation remains the one active increment. This does not advance the program to the OPA Enforcement Bridge.

## Change Control

Changes to the active increment, locked sequence, claims statuses, normative precedence, or public assurance boundary require:

1. A dated governance decision.
2. Claims Register updates.
3. Applicable specification, schema, test, and release-gate changes.
