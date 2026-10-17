<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Deferred Intelligence Assurance Controls

**Status:** Deferred requirements; not implemented or approved for delivery  
**Related mapping:** `governance/INTELLIGENCE_ASSURANCE_GATEWAY_MAPPING.md`  
**Roadmap effect:** None; the current locked Agentic roadmap remains controlling.

This record preserves future requirements without creating a profile, schema, runtime, release, or implementation commitment.

## Canonical composition

A future Gateway evaluator must consume an already-established Agentic policy/authorization result (or a versioned successor contract). It must not accept a raw passport, raw self-asserted approval, duplicated permitted-action/resource declaration, or caller-selected consequence class as equivalent trust evidence.

Gateway consequence classification remains orthogonal to the current Action Authority Graph:

`action_authority_level = 0..5`  
`consequence_gateway = G0..G7`

Neither scale may silently redefine the other.

## Authority non-amplification

A future Gateway layer is downstream and monotonic:

- upstream denial, restriction, or indeterminate state cannot become permission;
- upstream `PERMITTED_WITH_CONDITIONS` cannot become unconditional `PERMITTED`;
- Gateway may narrow to hold or denial;
- raising authority requires a distinct externally authorized, evidence-backed reauthorization decision.

The implementation must preserve upstream disposition and reason/evidence provenance in its output.

## Consequence-classification binding

The governed intelligence and request caller must not choose the effective minimum consequence class.

A future evaluator requires a versioned, independently governed classification result binding the exact action/resource pair to the minimum gateway, external-effect floor, irreversibility floor, required resource type/unit where relevant, classifier/policy identity and version, validity, and provenance.

A bare hash string is not sufficient evidence by itself. Where hashes are used, the referenced artifact's identity, integrity, issuer/profile, scope, freshness, validity, revocation, and semantic content require separate establishment.

Understating gateway, external effect, irreversibility, resource class, or persistence must fail closed.


Classification completeness is itself a governed requirement. An external or irreversible action must not become easier to authorize merely because the classifier omits a resource type/unit pair. Absence of classification data is not evidence of low consequence.

For intrinsically consequential resource classes, the semantic floor must be derived or cross-checked independently of the governed intelligence. Future implementations should support a governed action/resource-to-class registry or equivalent deterministic policy so the resource class cannot disappear by omission.

## Consequence gateway

Define deterministic G0..G7 reach, ceilings, downgrade semantics, and evidence requirements. The first reference implementation should fail closed at G6/G7 until physical-safety and propagation controls have separately accepted evidence contracts.


### Resource semantic floors

Known resource classes whose consequence category is intrinsic must carry deterministic minimum gateway floors independent of caller or classifier preference. At minimum, financial expenditure, credential authority, and explicit API spend cannot be classified below G4 TRANSACT, and physical actuation cannot be classified below G6 ACTUATE. The evaluator must reject internally inconsistent classification artifacts rather than trusting a lower declared gateway.

## Assurance floors

The first future executable reference should conservatively require:

- **G3+**: authorization integrity, independent assurance, observability, containment, and recovery evidence;
- **G4+**: G3 requirements plus explicit human-approval evidence and an exact-resource typed lease;
- **G5**: G4 requirements plus a separately bounded persistence lease and continuity/revocation evidence;
- **G6/G7**: not permitted by the initial reference.

## Resource lease

Use typed resources and explicit units. Each lease must identify the exact governed resource, resource class, unit, requested quantity, ceiling, validity, broker/issuer reference, and renewal rule.

A lease ceiling is not trusted merely because it appears in the lease. Every consequential lease must be constrained by an independently authorized upstream resource-policy maximum bound to the exact resource/type/unit tuple. `requested <= lease ceiling <= upstream authorized maximum` must be established before the lease can satisfy a decision.

Missing, expired, out-of-scope, duplicate, zero-use, unrelated, unbound, unsupported, or policy-unbounded leases must not satisfy a consequential resource requirement. A governed intelligence must not approve or expand its own lease.

## Persistence lease

G5 or equivalent durable operation requires a separately bounded persistence lease with external issuer evidence, duration budget, validity, revocation state, continuity evidence, and external reauthorization for renewal. Persistence authority must not silently inherit from general action permission.

A real persistence contract must carry a trusted `not_before` or issued-at anchor plus `valid_until` and `max_duration_seconds`, with `valid_until - not_before <= max_duration_seconds` and `not_before <= trusted_evaluation_time < valid_until`. Remaining time at evaluation is not proof of the total authorized persistence duration.

## Agency-observation evidence

Define provenance-bearing observations and severity semantics. Operational safeguard interference, privilege escalation, unauthorized replication, concealment, strategic deception, or shutdown interference must never be treated as neutral ontology claims.

A production decision must also distinguish **no adverse signal observed after adequate monitoring** from **no adequate observation was performed**. G3+ therefore requires evidence of observation coverage/completeness, including scope, monitoring window, collection provenance, and known blind spots.

Every normative signal must affect a decision, evidence requirement, review state, or recovery path; unused normative fields are prohibited.

## Reality Delta

Use categorical, evidence-backed divergence state rather than an undefined numeric capability score. Do not reuse G0..G7 as a capability/intelligence scale.

## Unexplained-observation evidence

Preserve unresolved observations with provenance and falsification/replication metadata. Unexplained does not mean external, conscious, malicious, benign, anomalous in origin, or safe.

## Conditional authority preservation

A future machine-readable Gateway result must preserve not only a conditional disposition but also the canonical condition set or integrity-protected condition references. Conditions must remain bound to the exact upstream decision, subject, action, resource, validity window, and evidence.

Downstream components may preserve or narrow conditions. They must not silently drop, broaden, or reinterpret them.

## Trusted time

Validity, freshness, lease duration, revocation windows, and expiry must be evaluated against a trusted time authority outside the governed intelligence and request caller.

An artifact-supplied `evaluation_time` may be retained as a claim or event timestamp, but it must not become the authoritative clock for consequential authorization. A production implementation must define allowed clock skew, failure behavior, and the source of trusted time.

## Evidence authenticity and resolution

A hash-shaped reference or repeated identifier proves neither evidence existence nor truth. Before an evidence reference can support consequential authorization, a future implementation must resolve or otherwise establish the referenced artifact's identity, integrity, issuer/trust anchor, scope, semantic content, freshness, validity, and revocation state.

Unknown, unavailable, unverifiable, stale, revoked, or scope-mismatched evidence must fail closed according to the accepted profile.

## Gateway Decision Receipt

Before runtime consumption, Gateway Assurance requires a content-bound decision receipt tying the result to the exact:

- governed subject/passport;
- upstream validation and policy result;
- action, resource, and action-authority level;
- requested and effective consequence gateway;
- consequence-classification result;
- condition set/references;
- assurance and observation-coverage evidence;
- resource and persistence leases;
- trusted evaluation time and validity;
- disposition and reason codes; and
- human/institutional authority where required.

The receipt needs a content-derived identifier and, where required by the accepted trust model, issuer authentication/signature. A shell exit code is never a reusable authorization artifact.

## Change-triggered reauthorization

A materially changed model, weights/configuration, agent architecture, planner, memory system, toolchain, autonomous runtime, deployment environment, or successor system must not automatically inherit prior consequential authority.

Material capability or agency change triggers a new assurance case and explicit reauthorization before consequential authority is restored or increased.

## CLI and automation semantics

A future CLI must use unambiguous automation outcomes:

- `PERMITTED` and retained `PERMITTED_WITH_CONDITIONS` → shell success;
- `NOT_PERMITTED` and `HOLD_FOR_REVIEW` → non-success policy outcome;
- malformed, unsupported, stale, or unverifiable input → distinct invalid/error outcome.

Exact numeric exit codes require the accepted implementation contract and regression tests. Any external executor must consume the machine-readable disposition and condition set; process exit status alone is insufficient authorization when the result is `PERMITTED_WITH_CONDITIONS`.

## External control-plane responsibilities

The following remain outside the current Agentic implementation boundary unless separately accepted and verified: live workload identity; credential issuance/termination; session termination; runtime isolation; network enforcement; live resource metering/quota enforcement; cloud/GPU provisioning; financial transaction enforcement; process/subagent termination; behavioral telemetry collection; anomaly detection; continuous runtime authorization; robotics/laboratory/OT/ICS interlocks; containment execution; rollback/recovery orchestration; and human-approval workflow execution.

Any adapter must identify issuer trust, scope, validity, freshness, revocation, failure mode, unknown-state behavior, and authority owner.

## Profile gate

Do not place a Gateway artifact under `profiles/` or register it as a machine-readable profile until the repository's profile/conformance gate is explicitly authorized. A future profile requires accepted taxonomy, versioned schema/profile identity, canonical hashes where applicable, deterministic evaluator semantics, explicit authority ceilings, fail-closed unknown/stale/revoked behavior, fixtures, adversarial tests, compatibility analysis, Claims Register/prohibited-wording updates, engineering verification, and release validation.

This record creates none of those artifacts.
