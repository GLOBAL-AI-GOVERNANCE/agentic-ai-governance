<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Zero Trust Agent Readiness Mapping

**Status:** Current-main, unreleased reference mapping
**Source boundary:** Concept-to-repository mapping based on the approved Phase 0 concept set

## Purpose and assurance boundary

This document maps Zero Trust agent-security concepts to the current Agentic AI Governance architecture. Agentic AI Governance provides machine-readable reference primitives for declared authority, evidence binding, verification, validity, and revocation that can support—but do not themselves enforce—Zero Trust governance for AI agents.

The mapping describes repository artifacts and their verified behavior. It is not a certification, compliance assessment, third-party conformance determination, production IAM implementation, runtime Zero Trust enforcement system, production authorization, proof of agent safety or operational effectiveness, legal-compliance assurance, or third-party endorsement. The source concept set is informative; no external source version, control identifier, normative traceability, or endorsement is asserted.

The classifications used here are:

- `IMPLEMENTED_AND_VERIFIED`: implemented by repository artifacts and exercised by repository verification within the documented reference boundary.
- `MODELED_REFERENCE_ONLY`: represented by a deterministic reference model or demonstration, without external enforcement.
- `PARTIALLY_MODELED`: some relevant semantics exist, but the complete concept is not represented or enforced.
- `DOCUMENTED_ONLY`: described as a boundary or requirement without a corresponding implemented model.
- `NOT_MODELED`: no current repository model establishes the concept.
- `OUT_OF_SCOPE`: belongs to a runtime or institutional control plane outside this repository's intended implementation boundary.
- `DEFERRED`: deliberately preserved for a separately authorized future increment.

## Concept mapping

Runtime enforcement is **No** throughout unless expressly stated; no row establishes production enforcement. Human or institutional authority remains necessary for every real deployment and consequential decision.

| Concept | Classification | Current supporting artifacts | What current evidence proves | Runtime enforcement | Human authority | Likely runtime/control owner | Future schema/profile implication and limitations |
|---|---|---|---|---|---|---|---|
| Agent inventory | `IMPLEMENTED_AND_VERIFIED` | `schemas/agent-inventory.schema.json`; inventory fixtures; validator tests | Declared agent identifiers, capabilities, data use, and production-use flags are structurally and semantically checked | No | Declaration and approval remain institutional | Agentic for declarations; deployment platform for truth | No immediate new artifact; does not discover running agents |
| Accountable ownership | `PARTIALLY_MODELED` | `spec/00-status-and-scope.md`; assessment and evidence records | Accountability is in the governed boundary and issuers/evaluators are attributable | No | Yes | Agentic governance authority | Canonical accountable-owner binding remains deferred |
| Cryptographically rooted artifact identity | `IMPLEMENTED_AND_VERIFIED` | `spec/05-agent-trust-passport.md`; `spec/06-signature-profile.md`; trusted-key and passport schemas | Content-derived identifiers, Ed25519 detached signatures, and trusted signing-key status are verified | No | Issuer and trust-anchor governance | Agentic artifact trust | Artifact identity is not live workload identity |
| Workload/service authentication | `OUT_OF_SCOPE` | `spec/00-status-and-scope.md`; deferred Infrastructure Trust requirements | The boundary explicitly excludes production credential validation | No | Yes | Identity provider and operational platform | A future integration may bind external authentication evidence |
| Short-lived service credentials | `OUT_OF_SCOPE` | Passport validity boundary; deferred controls | No credential issuance or rotation is implemented | No | Yes | IAM/credential issuer | Passport expiry must not be reused as credential semantics |
| Credential isolation | `OUT_OF_SCOPE` | Action-authority credential-change dimension | Credential changes affect declared authority level only | No | Yes | Secrets and workload platform | Future evidence may declare isolation; enforcement remains external |
| Deny-by-default authorization | `MODELED_REFERENCE_ONLY` | Validator fail-closed behavior; `policies/opa/` bridge | Unsupported, invalid, stale, or insufficient inputs produce non-permitted reference outcomes | No | Policy owner retains authorization | Agentic decision model; operational enforcement plane | Runtime binding and enforcement contract remain deferred |
| Least privilege | `PARTIALLY_MODELED` | Action levels, profile ceilings, controlled scopes | Declared authority can be bounded and excessive authority rejected | No | Approver selects acceptable authority | Agentic governance plus IAM | Does not configure real privileges |
| Least agency | `PARTIALLY_MODELED` | `spec/08-action-authority.md`; conditions and operating dispositions | Reachable consequences and authority ceilings constrain reference decisions | No | Approver remains responsible | Agentic governance | A future profile may strengthen agency-minimization requirements |
| Action scope | `IMPLEMENTED_AND_VERIFIED` | Action-authority schema, graph fixtures, semantic tests | Requested and computed levels and reachable action paths are reconciled | No | Yes | Agentic governance | Limited to declared graph fields |
| Tool scope | `IMPLEMENTED_AND_VERIFIED` | Tool inventory schema; controlled tool effects; graph reconciliation | Declared tool effects and reachable tool nodes must agree with authority | No | Yes | Agentic governance; tool platform at runtime | Does not observe actual tool behavior |
| MCP scope | `IMPLEMENTED_AND_VERIFIED` | MCP inventory schema; `profiles/mcp-governance-profile.md`; action graph | Declared MCP servers and scopes are validated against controlled semantics | No | Yes | Agentic governance; MCP host at runtime | Does not discover live MCP servers or enforce calls |
| Reachable blast radius | `IMPLEMENTED_AND_VERIFIED` | `spec/08-action-authority.md`; action-authority schema | Declared local, team, organization, external, and critical reach contributes deterministic authority floors | No | Yes | Agentic governance; operational platform | Declared reach is not observed impact |
| Multi-agent delegation | `PARTIALLY_MODELED` | `SUBAGENT` nodes; `DELEGATES` edges | Declared delegation is reachable and raises minimum authority | No | Delegating authority remains accountable | Agentic governance and orchestration platform | Delegation-chain depth, inheritance, and termination remain deferred |
| Approval gates | `PARTIALLY_MODELED` | `APPROVAL_GATE` nodes; `APPROVES` edges; assessment conditions | Approval dependencies can be declared in the authority graph | No | Yes, necessarily | Human workflow/decision authority | Approval strength and evidence semantics remain deferred |
| Evidence binding | `IMPLEMENTED_AND_VERIFIED` | Bundle manifest, assessment, passport, and evidence schemas; `spec/09-data-authority-interop.md` | Hashes, references, subjects, validity, issuer trust, and bundle consistency are checked | No | Evidence admission remains institutional | Agentic evidence model; source authorities | Bound supplied evidence is not live telemetry or source truth |
| Logging | `PARTIALLY_MODELED` | Deterministic results, reason codes, lifecycle trace | Reference evaluations emit inspectable decisions and reason codes | No | Logging policy remains operational | Runtime platform/security operations | A runtime audit-event contract is not defined |
| Traceability | `IMPLEMENTED_AND_VERIFIED` | Content-derived IDs, manifests, evidence refs, claims register | Repository artifacts and decisions have deterministic internal trace links | No | Steward review remains required | Agentic governance | Internal traceability does not prove external facts |
| Runtime observability | `OUT_OF_SCOPE` | Honest-assurance boundary | Current verification does not inspect production behavior | No | Yes | Operations/telemetry platform | Future evidence adapter may consume, not create, observations |
| Behavioral monitoring | `OUT_OF_SCOPE` | Prohibited-capability boundary | No behavioral detection capability is claimed | No | Yes | Security monitoring platform | Separate operational integration required |
| Input-boundary controls | `PARTIALLY_MODELED` | Strict JSON parser, JSON Schemas, controlled vocabularies | Submitted governance artifacts fail closed on malformed or unsupported input | No | Runtime policy remains external | Agentic for artifacts; application gateway at runtime | Schema validation is not runtime ingress protection |
| Output-boundary controls | `PARTIALLY_MODELED` | Publication/data-movement dimensions and `PUBLISHES` edges | Declared external publication and data movement raise authority requirements | No | Consequential output approval remains human | Agentic governance plus egress platform | No runtime egress interception |
| Memory/context governance | `NOT_MODELED` | None | No current normative memory lifecycle or context-authorization model | No | Yes | Agentic governance and runtime platform | Future semantics are deferred |
| Memory provenance | `NOT_MODELED` | Generic evidence primitives only | Generic hashes do not establish memory-specific lineage | No | Yes | Runtime memory provider and governance authority | Memory-specific provenance contract is deferred |
| Memory integrity | `NOT_MODELED` | Generic artifact integrity only | Artifact integrity does not establish memory integrity or poisoning resistance | No | Yes | Runtime memory/security platform | Memory integrity evidence and failure semantics are deferred |
| Identity-based workload isolation | `OUT_OF_SCOPE` | Deferred Infrastructure Trust requirements | No workload isolation is implemented or verified | No | Yes | Compute/orchestration platform | Future profile may bind supplied isolation evidence |
| Network boundaries | `OUT_OF_SCOPE` | `spec/00-status-and-scope.md` | No network policy is enforced or observed | No | Yes | Network/control plane | External evidence integration only |
| Sandboxed execution | `OUT_OF_SCOPE` | Deferred Infrastructure Trust requirements | No sandbox is implemented or attested | No | Yes | Workload platform | A future profile could declare required sandbox evidence |
| JIT/JEA privilege | `OUT_OF_SCOPE` | Validity and authority ceilings only | Current artifacts do not issue or elevate privileges | No | Yes | IAM/privileged-access platform | Runtime integration is deferred |
| Continuous authorization | `PARTIALLY_MODELED` | Presentation-time validity, revocation, and OPA reference evaluation | A supplied trust state can be reevaluated deterministically at a stated time | No | Policy authority remains responsible | Agentic decision model plus runtime control plane | No continuous event loop or enforcement binding exists |
| Validity | `IMPLEMENTED_AND_VERIFIED` | Passport, evidence, key, and revocation validity semantics | Supported intervals and presentation-time status are checked | No | Issuers define valid authority | Agentic artifact trust | Valid artifact does not authorize production action by itself |
| Expiry | `IMPLEMENTED_AND_VERIFIED` | Passport/evidence/key expiry tests | Expired artifacts fail relevant trust checks | No | Renewal remains controlled | Agentic artifact trust | Expiry is not credential termination |
| Revocation | `IMPLEMENTED_AND_VERIFIED` | `spec/07-revocation.md`; signed cumulative lists; negative vectors | Supplied trusted revocation state changes reference verification and disposition | No | Revocation authority is institutional | Agentic artifact trust | Does not terminate sessions, credentials, tools, or effects |
| Credential/session termination | `OUT_OF_SCOPE` | README and revocation limitations | The repository explicitly disclaims termination | No | Yes | IAM/session control plane | External runtime contract required |
| Rollback | `PARTIALLY_MODELED` | Alpha.2 Stateful Revocation continuity; rollback tests | Lower, conflicting, or discontinuous revocation state is rejected relative to an intact local store | No | Store custody remains operational | Agentic reference verifier plus host platform | Not host/database anti-rollback or general recovery |
| Reauthorization | `MODELED_REFERENCE_ONLY` | Synthetic incident-readiness lifecycle | Reauthorization requires a distinct newly validated passport; terminal revocation is preserved | No | Issuer and approver decide reauthorization | Agentic governance and operational authority | Production workflow semantics remain deferred |
| Human approval for consequential actions | `PARTIALLY_MODELED` | Levels 4–5, approval gates, conditions, Level 5 prohibition | Consequential declared authority is raised or prohibited by reference rules | No | Yes | Institutional decision workflow | Integrated approvals and evidence strength remain deferred |
| Incident response | `MODELED_REFERENCE_ONLY` | `examples/agent-incident-readiness/`; lifecycle tests | A deterministic synthetic denied/revoked/rollback-rejected/reauthorized sequence is demonstrated | No | Incident authority remains human | Security operations | Synthetic lifecycle is not live response or containment |
| Defensive-agent / SOAR boundaries | `DOCUMENTED_ONLY` | Scope prohibitions and deferred controls | Autonomous remediation and action execution are outside current claims | No | Yes | Security operations/SOAR platform | Any integration requires separate authorization and controls |

## Critical distinctions

- Passport expiry **is not** a short-lived runtime credential.
- A signed Agent Trust Passport **is not** production workload or service authentication.
- Artifact signature verification **is not** live workload identity verification.
- Action-authority modeling **is not** runtime IAM enforcement.
- An authority ceiling **is not** operational privilege enforcement.
- An OPA reference disposition **is not** production authorization.
- Revocation-list semantics **are not** credential or session termination.
- Stateful Revocation continuity **is not** host or database anti-rollback.
- Evidence binding **is not** runtime telemetry.
- MCP inventory and scope validation **are not** live MCP discovery or runtime enforcement.
- Approval-gate modeling **is not** an integrated human approval workflow.
- Input schema validation **is not** runtime ingress protection.
- Publication and data-movement authority modeling **is not** runtime egress enforcement.
- The synthetic incident-readiness lifecycle **is not** live incident response.
- Local revocation rollback detection **is not** general operational rollback or recovery.
- Repository conformance **is not** production deployment conformance.

## Architecture reuse and ownership boundary

Future work must compose the existing Agent Trust Passport, inventories, MCP governance profile, action-authority graph, evidence bindings, signature and validity rules, revocation model, Stateful Revocation, OPA bridge, incident-readiness lifecycle, Claims Register, and conformance model. Parallel Zero Trust-branded replacements would create conflicting authority and are not authorized by this mapping.

Operational controls—including identity providers, credential issuance, secret custody, workload and network isolation, telemetry, behavioral monitoring, session termination, sandboxing, and SOAR execution—belong to external control planes. Possible portfolio integrations are recorded only as unapproved future ownership candidates in `requirements/deferred-zero-trust-agent-controls.md`.

## Machine-readable profile: later gate

A future machine-readable Zero Trust profile under `profiles/` would create a material new conformance surface. It requires separate authorization for a normative control taxonomy, profile identity and version, descriptor and canonical hashes, evidence schemes, trust anchors, deterministic assessment semantics, authority ceilings, fail-closed behavior, positive and negative fixtures, validator support, conformance tests, interoperability vectors, compatibility analysis, Claims Register updates, V&V, and a release-impact decision. This Phase 1 mapping creates no profile or schema.

## Current release boundary

This mapping is current-main, unreleased work. It is not part of `v0.1.0-alpha.2`, does not change the status of other unreleased current-main capabilities, and does not authorize a tag or release.
