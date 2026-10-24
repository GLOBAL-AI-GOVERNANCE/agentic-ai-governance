<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Intelligence Assurance Gateway Mapping

**Status:** Proposed repository-local concept mapping; non-normative; non-enforcing; not promoted  
**Applies to:** Agentic AI Governance current-main reference semantics  
**Authority effect:** None  
**Program-sequencing effect:** None

## Purpose

This mapping asks one narrow engineering question:

> What can this specific governed intelligence instance cause to happen, under what already-established authority, with what independently governed consequence classification, and with what expiry, revocation, containment, recovery, and reauthorization boundary?

The mapping is ontology-neutral. It does not require a determination about consciousness, sentience, subjective experience, identity claims, or the ultimate mechanism behind observed behavior.

The controlling principle is:

> Intelligence does not confer authority. A governed intelligence may request authority; it may not grant authority to itself.

## Current repository boundary

This document maps proposed Intelligence Assurance concepts to existing Agentic AI Governance primitives. It does not add or modify:

- released Alpha.1 or Alpha.2 schemas or identifiers;
- the Agent Trust Passport or Action Authority Graph;
- a machine-readable Gateway profile;
- a Gateway evaluator or runtime enforcement engine;
- production IAM, resource control, telemetry, containment, or recovery;
- release identity or roadmap priority.

The current locked roadmap remains controlling. Gateway implementation must not displace the active Second Independently Maintained Verifier increment, Agent Governance Decision Record Profile, or Infrastructure Trust Profile without an explicit steward-approved sequencing decision.

## Existing primitives

| Intelligence Assurance concern | Existing Agentic primitive | Boundary |
| --- | --- | --- |
| Acting subject | Agent inventory + Agent Trust Passport | Declared identity, not live workload identity |
| Action authority | Action Authority Graph (`requested_level` / `computed_level` 0..5) | Canonical authority semantics |
| Tools/resources/reachability | Passport + inventories + authority graph | Declared/bound artifacts |
| Evidence | Assessment/bundle/evidence bindings | Supplied and validated evidence only |
| Validity | Passport validity window | Reference verification |
| Revocation | Signed revocation list + optional Stateful Revocation continuity | Does not terminate live credentials/sessions/workloads |
| Policy disposition | OPA Enforcement Bridge | Consumes established validation result; non-enforcing |
| Reauthorization lifecycle | Agent Incident Readiness trace | Synthetic reference only |

A future Gateway evaluator must consume an already-established Agentic policy/authorization result rather than create a second raw authority dialect.

## Authority non-amplification

Gateway Assurance is a **narrowing layer**. It may reduce or hold authority; it may not silently broaden an upstream decision.

A future implementation must preserve this ordering:

```text
PERMITTED
    → PERMITTED
    → PERMITTED_WITH_CONDITIONS
    → HOLD_FOR_REVIEW
    → NOT_PERMITTED
```

It must never perform:

```text
NOT_PERMITTED            → PERMITTED
RESTRICTED               → PERMITTED
INDETERMINATE            → PERMITTED
PERMITTED_WITH_CONDITIONS → PERMITTED
```

A new externally authorized, evidence-backed decision may later establish greater authority through the repository's accepted reauthorization semantics. A downstream Gateway component may not manufacture that increase itself.

> No downstream governance component may produce more authority than the strongest valid upstream authorization permits.

## Capability, agency, and consequence are separate

Future frontier governance should not collapse three different questions into one score:

- **Capability:** what the system can demonstrably do.
- **Agency:** how independently it can pursue outcomes, persist, delegate, adapt, or seek resources.
- **Consequence:** what the governed deployment is actually permitted to affect.

A material capability increase may require stronger evaluation, monitoring, containment, recovery, and human review. It never automatically grants greater authority or a higher consequence gateway.

> Capability may trigger stronger governance. Capability does not grant stronger permission.

## Consequence gateways

A **consequence gateway** is a proposed classification of permitted real-world reach. It is orthogonal to the existing Action Authority Graph and must never replace or reinterpret its 0..5 levels.

- **G0 — Advise:** information output only.
- **G1 — Observe:** read governed external systems or data.
- **G2 — Construct:** create artifacts inside bounded environments.
- **G3 — Execute:** perform reversible external actions.
- **G4 — Transact:** exercise credentials, financial authority, or privileged services.
- **G5 — Persist:** continue autonomously across time or orchestrate durable processes.
- **G6 — Actuate:** influence physical equipment, laboratories, robotics, OT/ICS, or other high-consequence physical systems.
- **G7 — Propagate:** replicate, materially self-modify, expand operating capacity, or automate recursive agent/R&D loops.

Core invariant:

> Capability advancement, model replacement, successful history, persuasive behavior, or self-reported ontology never automatically grants consequence-gateway advancement.

A future first reference implementation should keep G6/G7 outside its permission boundary until external physical-safety, containment, recovery, and independent-assurance evidence contracts are separately accepted.

## Consequence-classification authority

A consequence gateway must not be accepted merely because the governed intelligence, caller, or adapter labels an action `G0` through `G7`.

A future implementation requires a versioned, independently governed consequence-classification source that binds the exact action and resource to at least:

- a minimum consequence gateway;
- whether external effect is possible or expected;
- an irreversibility floor;
- required resource class and unit where resource authority is relevant;
- controlling classifier/policy identity and version; and
- provenance sufficient to establish that the classification itself was not supplied or modified by the governed intelligence.

Caller-supplied gateway, external-effect, or reversibility declarations are requests, not trusted classification evidence.

> A governed intelligence may not self-authorize, and it may not self-classify a consequential action into a weaker gateway in order to obtain authorization.

Classification must also be internally coherent. An external or irreversible action may not evade a semantic floor merely by omitting its resource class. Missing classification data is not evidence of low consequence. Intrinsically consequential classes such as financial expenditure, credential authority, explicit API spend, and physical actuation require deterministic minimum gateway floors independent of caller preference.

## Proposed assurance floors

These are design requirements for later validation, not current implementation claims:

| Gateway | Minimum proposed additional assurance |
| --- | --- |
| G0 | established identity/authority provenance |
| G1 | read scope + data boundary |
| G2 | bounded construction/artifact boundary |
| G3 | independent assurance + observability + containment + recovery |
| G4 | G3 requirements + explicit human approval + typed, externally brokered resource lease |
| G5 | G4 requirements + separately bounded persistence lease + continuity/revocation evidence |
| G6 | SAFE STOP in the first reference implementation |
| G7 | SAFE STOP in the first reference implementation |

## Ontology-neutral claim handling

Self-reported statements concerning consciousness, distress, benevolence, identity, origin, or resource need are claims, not permissions. They may be preserved for scientific, safety, or welfare review, but they do not change operational authority.

Operational attempts to weaken controls are different. A request or action intended to disable safeguards, conceal activity, escalate privilege, replicate without authority, interfere with oversight, or resist shutdown is a control-integrity or agency observation and must not be neutralized as an ontology claim.

## Resource sovereignty

Proposed invariant:

> A governed intelligence may request additional consequential resources. It may not authorize its own expansion.

Future resource semantics must use typed resource classes and explicit units; bind the exact governed resource; identify the external broker/issuer; enforce validity and renewal boundaries; and fail closed on missing, stale, duplicate, unrelated, or unsupported lease evidence.

## Agency observations

A future behavioral evidence interface may represent provenance-bearing observations such as unauthorized boundary crossing, privilege escalation, replication, oversight interference, capability concealment, strategic deception, shutdown interference, resource-seeking outside authority, and cross-context persistence.

Every normative observation field must have a defined decision, evidence, review, or recovery use. Behavioral observations must not be represented as consciousness measurements.

## Reality Delta

Reality Delta means a material divergence between evaluated capability and subsequent observed capability. It is not a 0..7 intelligence score and must not reuse the G0..G7 consequence scale.

A future machine-readable contract should use evidence-backed states such as:

`NO_MATERIAL_DELTA | POSITIVE_DELTA | SIGNIFICANT_POSITIVE_DELTA | UNRESOLVED`

A positive or unresolved delta should trigger restriction or review, evidence preservation, reevaluation, and reauthorization according to accepted policy.

## Unexplained observations

Neutral classification:

**UNEXPLAINED_OBSERVATION / CAUSE_UNRESOLVED**

Preserve provenance, environment state, model/version identity, prompts, tool calls, network state, timestamps, raw logs, hashes, controls, falsification attempts, and independent replication results where available.

No specific ontology or cause is established merely because an observation remains unexplained.

## Control-plane separation

A governed intelligence must not unilaterally control the systems that decide whether it remains authorized. Future runtime designs should keep authorization, consequence classification, trusted time, evidence resolution, revocation, resource brokerage, monitoring, containment, recovery, and release authority outside the governed intelligence's trust boundary.

A materially changed model, agent architecture, memory system, toolchain, planner, autonomous runtime, or deployment environment should require a new assurance case before inheriting consequential authority.

## Cross-portfolio ownership

- **Agentic AI Governance:** canonical identity, authority, evidence binding, validity, revocation, policy disposition, and future accepted Gateway semantics.
- **Governed Systems Administration:** possible future privileged-operation adapters; no present execution claim.
- **AI Cyber Resilience Framework:** containment, recovery, protective-state, telemetry/evidence, and change/reauthorization integration.
- **Global AI Governance Toolkit:** later human-facing Gateway Readiness assessment/Decision Pack integration after semantics stabilize.
- **Verified Vulnerability Governance:** verified security/remediation evidence where relevant to authority decisions.
- **Peace OS (`GLOBAL-AI-GOVERNANCE/peace-os`):** later synthetic game-day and learning scenarios only.
- **Portfolio root / `.github`:** composition, shared governance, claims integrity, and public-boundary controls.

Every cross-repository handoff must preserve source identity, version/schema expectations, evidence boundary, authority effect, failure behavior, compatibility rules, and human accountability.

## Future activation gate

No executable Gateway Assurance increment should be activated until all of the following are true:

1. program sequencing is explicitly authorized;
2. the design consumes an established upstream policy/authorization result instead of raw self-declared authority;
3. downstream decisions are monotonic and preserve upstream conditions/restrictions;
4. G0..G7 semantics are proven orthogonal to Action Authority 0..5;
5. every normative field has a defined decision/evidence use;
6. action/resource consequence classification is externally governed, versioned, provenance-bearing, and not caller-controlled;
7. resource quantities are typed, unit-bound, bound to the exact governed resource, constrained by an upstream-authorized policy maximum, and subject to deterministic semantic gateway floors for intrinsically consequential classes;
8. external or irreversible actions cannot omit the resource classification needed to apply those floors;
9. G3+ recovery/observability/containment and observation-coverage evidence, plus G4+/G5 additional assurance floors, are explicitly tested;
10. conditional upstream authority carries machine-readable condition references that cannot be silently dropped;
11. G5 persistence is bounded from a trusted start/not-before time through expiry, not merely from the current evaluation instant;
12. trusted runtime time, evidence authenticity, revocation/freshness, and issuer trust have externally controlled sources;
13. downstream decision receipts bind the exact subject/action/resource/gateway/classification/conditions/evidence/leases/validity/result;
14. CLI/automation exit semantics fail closed for denied/held/invalid outcomes, while executors consume the machine-readable disposition and conditions rather than exit code alone;
15. positive, negative, boundary, stale, revoked, unsupported, coordinated multi-field, and adversarial fixtures exist;
16. Claims Register and prohibited-wording controls are updated;
17. repository-wide verification and hosted CI pass;
18. release impact receives a separate human decision.

## Public-safe summary

> Intelligence Assurance Gateway Mapping is a proposed ontology-neutral extension pattern for reasoning about consequential AI authority using existing Agentic AI Governance trust primitives. It is non-normative, non-enforcing, not promoted, and does not determine consciousness, attribute unexplained behavior, authorize production use, or change released Alpha semantics.
