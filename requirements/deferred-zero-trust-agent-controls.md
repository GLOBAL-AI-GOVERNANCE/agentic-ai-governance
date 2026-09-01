<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Deferred Zero Trust Agent Controls

**Status:** Deferred requirements; not implemented or approved for delivery
**Related mapping:** `governance/ZERO_TRUST_AGENT_READINESS_MAPPING.md`

This file preserves material requirements identified by the approved Zero Trust Agent Readiness concept mapping. It is not a roadmap, implementation commitment, profile, certification program, or approval of any cross-portfolio integration. Items require separate design authority, evidence, V&V, compatibility analysis, and release decisions before they can become normative or implemented.

## A. Agentic future governance semantics

### Accountable-owner binding

Define a canonical, verifiable binding between an agent governance subject and the organizational role accountable for its declaration, approval, operation, suspension, and retirement. Avoid embedding mutable personal data when stable organizational identifiers can provide accountability.

### Delegation-chain semantics

Define bounded delegation depth, authority inheritance and reduction, subagent identity binding, transitive reachability, termination, and evidence requirements. Delegation must never expand authority beyond the delegator's effective ceiling.

### Human approval evidence and strength

Define approval type, approver authority, separation of duties, freshness, scope, conditions, expiry, and revocation. Approval evidence must remain distinct from the runtime workflow that collects or enforces it.

### Memory and context governance

Define authorized memory classes, purposes, sources, retention, deletion, subject binding, cross-agent sharing, and context-boundary requirements. Include explicit uncertainty and absence behavior.

### Memory provenance

Define lineage for memory creation, transformation, retrieval, and reuse, including content integrity, source identifiers, timestamps, and admissible evidence schemes.

### Memory integrity

Define integrity and poisoning-resistance evidence, trust anchors, validation failure behavior, conflict handling, and recovery boundaries without claiming the governance verifier observes live memory behavior.

### Runtime reevaluation contract

Define a fail-closed interoperability contract through which an external runtime control plane can reevaluate established validation results when time, revocation, policy, context, or requested action changes. The contract must not turn the reference verifier into an enforcement engine.

### Production-state evidence adapters

Define how independently governed adapters may supply signed, scoped, time-bounded evidence concerning workload identity, isolation, telemetry, network state, credentials, or other production conditions. Adapters must preserve issuer trust, validity, revocation, source limitations, and unknown-state behavior.

### Reauthorization semantics

Define the institutional decision, new authority artifact, required evidence, approval, and audit linkage for reauthorization. A terminally revoked passport must never be restored or silently reused.

## B. External or operational control plane

The following capabilities are outside Agentic AI Governance's current implementation boundary. Future integration may consume their evidence or decisions but must not claim they are supplied by the present repository:

- Workload identity provider and service authentication.
- Short-lived credential issuance, rotation, and binding.
- Secret vaulting and credential isolation.
- Credential and session termination.
- Workload, process, tenant, and identity-based isolation.
- Sandboxed execution and containment.
- Network segmentation, policy, and enforcement.
- Runtime telemetry and audit-event collection.
- Behavioral monitoring and anomaly detection.
- Just-in-time and just-enough privileged access infrastructure.
- Continuous runtime authorization and enforcement.
- Human approval workflow execution.
- SOAR execution and defensive-agent orchestration.
- Remediation execution, rollback, and operational recovery.

Any operational binding must identify the enforcing system, trust boundary, failure mode, evidence source, authority owner, audit obligations, and safe-stop behavior.

## C. Possible future cross-portfolio ownership

The following repositories are possible later integration owners, not approved delivery commitments:

- **Governed Systems Administration:** possible workload identity, privileged access, isolation, session-control, and infrastructure evidence integration.
- **AI Cyber Resilience Framework:** possible telemetry, behavioral monitoring, incident-response, and defensive-agent boundary integration.
- **Verified Vulnerability Governance:** possible governed vulnerability evidence or remediation-authorization integration.
- **Global AI Governance Toolkit:** possible human-facing adoption guidance after Agentic semantics are stable and released.

No change to those repositories is authorized by this file. Ownership, sequencing, interfaces, and release timing require separate decisions.

## D. Machine-readable Zero Trust profile gate

A future profile under `profiles/` would be a material new conformance surface. Authorization must cover, at minimum:

- Normative control taxonomy.
- Profile identity, version, and descriptor.
- Canonical profile and document hashes.
- Supported evidence schemes and trust anchors.
- Deterministic assessment semantics and authority ceilings.
- Fail-closed unknown, unsupported, invalid, stale, and revoked behavior.
- Positive and negative fixtures.
- Validator and evaluator support.
- Conformance tests and interoperability vectors.
- Compatibility with existing Alpha artifacts and profiles.
- Claims Register and prohibited-wording updates.
- Design validation, engineering verification, release validation, and release-impact decision.

Phase 1 creates none of these machine-readable profile artifacts.
