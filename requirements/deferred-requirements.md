<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Deferred Requirements

**Status:** Recorded requirements; not active implementation scope.

This record preserves requirements learned from enterprise non-human identity governance, CISO accountability, agentic infrastructure, remediation assurance, and adjacent standards analysis. Recording a requirement does not promote it to shipped or verified capability.

## Next Locked Increments

### OPA Enforcement Bridge

- Consume validated passport, authority, and revocation results rather than raw declarations.
- Produce `PERMIT`, `DENY`, or `REQUIRE_APPROVAL`.
- Fail closed for invalid, expired, revoked, unsupported, inconsistent, or insufficiently evidenced authority.

### Lifecycle Demonstration and Second Verifier

- Demonstrate Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized operation.
- Preserve policy denial as distinct from passport revocation.
- Require the new passport to pass the complete ordinary trust path.
- Reproduce canonical outcomes through an independently maintained verifier.

### Agent Governance Decision and Infrastructure Trust

- Bind technical decisions to accountable organizational authority through an immutable Agent Governance Decision Record and separate Outcome Receipt.
- Later bind authorization to execution environment, endpoint, region, jurisdiction, residency, isolation, resources, and attestation.

## Enterprise Identity Requirements

Preserve for the Toolkit or future composed profiles:

- Accountable human ownership and reassignment.
- Expiration, recertification, and telemetry-aware inactivity decisions.
- Broad non-human and agent inventory.
- Production admission with actual blocking authority.
- Declared-versus-observed capability comparison.

Absence of one telemetry signal must not be represented as proof of inactivity.

## Containment and Recovery Requirements

The AI Cyber Resilience Framework may define containment requirements, blast-radius controls, evidence, and restoration criteria. Operational IAM, credential services, gateways, runtimes, orchestrators, workload platforms, and network controls perform the actual actions.

A revocation declaration is not proof that sessions, credentials, tools, workloads, or downstream effects were contained.

## Assurance and Closure Requirements

Apply the assurance pattern:

> **VERIFY → CORRECT → TEST → SIGN → DELIVER**

Verified Vulnerability Governance may later consume lifecycle-control findings, corrective evidence, retest results, and closure records. It must not redefine passport or revocation semantics.

## Deferred Requirement Placement

This table gives end users the public rationale, canonical owner, locked priority, and current status for deferred requirements. It preserves the requirements without exposing or elevating inaccessible internal analysis records.

| Deferred requirement | Public rationale or scope boundary | Canonical owner | Locked priority | Current status |
| --- | --- | --- | --- | --- |
| Human ownership and lifecycle governance | Enterprise use requires accountable ownership, reassignment, recertification, expiration, and telemetry-aware decommissioning. These requirements do not establish implementation effectiveness. | Global AI Governance Toolkit | Deferred | PROPOSED |
| Least agency | Agents should receive only the minimum action authority necessary for an approved purpose. This refines the existing authority model without expanding Priority One. | Agentic AI Governance | Existing model and future refinement | DEFINED |
| Operational containment evidence | Revocation does not itself terminate credentials, sessions, workloads, tools, or network paths. Enterprise enforcement systems perform those actions and must produce evidence. | AI Cyber Resilience Framework and enterprise enforcement systems | Deferred | PROPOSED |
| Accountable governance decisions | Future AGDR work should preserve roles, separation of duties, bounded residual-risk acceptance, and accountable decision authority without becoming a second policy engine. | Agentic AI Governance | Priority Five | DEFINED |
| Continuing assurance | Material dependency, runtime, placement, or security changes should trigger reassessment, revalidation, signed delivery evidence, and closure discipline. | Repository governance and future profiles | Multi-stage | DEFINED |
| Outcome evidence | A future immutable Outcome Receipt should remain separate from, and cryptographically linked to, the pre-execution AGDR. | Agentic AI Governance | Priority Five | DEFINED |
| Infrastructure trust | Future authorization profiles should bind execution environment, endpoint, region, jurisdiction, residency, placement, isolation, resources, attestation, and bidirectional trust. | Infrastructure Trust Profile | Priority Six | DEFINED |

### Public Placement Rules

- Advisory and commercial material is not a formal standard or normative technical authority.
- Public requirements must state their scope boundary without implying implementation, certification, or independent validation.
- Public architecture, ownership, schemas, specifications, claims, decisions, requirements, and release materials use **GLOBAL AI GOVERNANCE** as the sole public project identity.
- Authority level, assurance status, risk classification, and lifecycle state remain separate dimensions and must not be collapsed into one status.
- Dependency drift, runtime drift, workload-placement change, and security incidents are preserved as future reassessment or revalidation triggers.

## Exclusions From the Active Increment

Stateful Revocation Priority One does not implement:

- Epoch or temporary suspension semantics.
- Dynamic trust-policy administration.
- Universal runtime containment.
- Enterprise identity discovery or inactivity analytics.
- Board dashboards, hosted SaaS, or vendor bake-off tooling.
- Agent Governance Decision Record or Infrastructure Trust schemas.
