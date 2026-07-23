<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Deferred Agent Governance Decision Record Requirements

**Abbreviation:** AGDR.

**Status:** Defined future requirement; not implemented.

## Purpose

The Agent Governance Decision Record will bind an evaluated agent request, canonical trust result, policy decision, approvals, exceptions, and accountable organizational decision authority. It must not become a second passport, authority graph, revocation evaluator, or policy engine.

## Decision Chain

```text
Agent Trust Passport and bound evidence
        ↓
Canonical verification and current revocation result
        ↓
OPA or equivalent policy decision
        ↓
Agent Governance Decision Record
        ↓
Enterprise enforcement
        ↓
Outcome Receipt
```

## Required Boundaries

### References, Not Restatement

The AGDR references canonical passport, authority graph, verification, revocation, policy, and approval artifacts. It does not copy them into a competing source of truth.

### Immutable Pre-Execution Decision

The finalized AGDR records what was requested, known, evaluated, and decided before execution. Post-execution facts belong in a separately linked Outcome Receipt.

### Profile-Based Accountability

Consequential profiles may require distinct business, security, operational, and risk authorities. The requesting subject, operator, reviewer, and final decision authority may be combined only where the applicable profile explicitly permits it.

## Candidate Fields

- `decision_id`
- `request_id`
- `agent_id`
- `passport_id`
- `authority_graph_id`
- `verification_result_reference`
- `revocation_state_reference`
- `policy_decision_reference`
- `requesting_subject`
- `business_authority`
- `security_authority`
- `operational_authority`
- `risk_owner`
- `requested_action`
- `requested_resource`
- `approval_evidence`
- `decision`
- `primary_reason_code`
- `reason_codes`
- `exceptions`
- `residual_risk_acceptance`
- `enforcement_point`
- `decision_time`
- `evidence_references`

## Residual-Risk Acceptance

Residual-risk acceptance must be authenticated, scope-limited, time-limited, evidence-backed, and bound to a named authority. It may not override law, regulation, contract, mandatory safety requirements, profile hard-deny rules, invalid or untrusted passports, unknown revocation status, or prohibited Alpha.1 Level 5 authorization.

## Outcome Receipt

A separate Outcome Receipt may record enforcement status, execution result, affected resources, errors, rollback or compensation, incidents, completion time, and evidence references.

## Prohibited Claims

The AGDR and its evidence do not create legal immunity, privilege, indemnification, guaranteed admissibility, or protection from liability.
