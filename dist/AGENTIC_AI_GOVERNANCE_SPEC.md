<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agentic AI Governance Framework

> **GENERATED FILE - DO NOT EDIT DIRECTLY**  
> Source: `spec/`  
> Version: `v0.1.0-alpha.1`  
> Status: Experimental public alpha. Specification and schemas are not frozen.

## Status and Scope

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Purpose

The Agentic AI Governance Framework specifies machine-readable governance artifacts and deterministic evaluation rules for declared agentic AI systems.

The governed boundary is the combined declared system:

```text
Agent + Identity + Data + MCP connections + Tools + Authority
+ Action + Evidence + Accountability + Recovery
```

MCP is one connection and capability layer. It is not the entire governance object.

## Public stewardship and names

Global AI Governance is the public steward of:

- Agentic AI Governance Framework
- Agent Governance Control Layer
- Agent Trust Passport
- MCP Governance Profile
- Agent Action Authority Matrix

This project MUST NOT be described as an operating system. This naming constraint applies to Agentic AI Governance only and does not classify or rename other repositories maintained by the public steward.

## Alpha.1 permitted capabilities

A conforming Alpha.1 implementation MAY validate schemas and references, reject malformed data, check internal consistency, evaluate submitted declarations against a selected profile, validate supplied evidence metadata, calculate action-authority limits, produce issued assessment results, create unsigned or externally signed passports, verify identifiers and signatures, evaluate validity and revocation, and apply an institutional trust policy.

## Alpha.1 prohibited capabilities

Alpha.1 MUST NOT connect to live infrastructure, discover production MCP servers, inspect actual entitlements, validate production credentials, claim tool behavior was observed, re-derive source-system truth, remediate systems, execute actions, certify operational security, issue third-party attestations, or grant institutional authority.

## Honest assurance boundary

Alpha.1 verifies only:

> The structural validity and internal consistency of declared configuration and supplied evidence within the submitted assessment bundle.

Alpha.1 does not verify the actual condition or behavior of a production environment.

Claims such as `independently verified`, `ground-truth verified`, `production validated`, `operationally certified`, or `observed directly` MUST NOT be made unless a later capability directly supports and documents them.

## Artifact status

This experimental Alpha.1 text and its schemas are public interoperability contracts. They are not frozen standards, production guarantees, certifications, or institutional authorization.

## Normative Conventions

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Requirement language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described by BCP 14 when, and only when, they appear in all capitals.

## Version fields

Artifacts MUST identify their schema version. Framework, profile, evaluator, policy, and adapter versions MUST be independently identified when they affect interpretation or output.

Alpha.1 compatibility is exact-match by default:

- An implementation MUST reject an unsupported `schema_version` with `UNSUPPORTED_VERSION`.
- An implementation MUST NOT assume compatibility between different pre-1.0 versions.
- A profile MAY define a narrower accepted-version set.
- A migration MUST produce a new artifact and MUST NOT silently rewrite signed content.

## Unknown properties

Schemas use closed content by default. Unknown properties MUST be rejected unless the schema explicitly permits them inside `extensions`.

Extension keys MUST use a reverse-domain namespace. An artifact MAY identify extension keys in `critical_extensions`. If a critical extension is not understood, verification MUST return `UNSUPPORTED_CRITICAL_EXTENSION`. The Alpha.1 reference validator registers no supported critical extensions; therefore every non-empty `critical_extensions` list fails closed.

## Project media types

The project uses the following provisional identifiers during Alpha.1 and Alpha.1 development:

```text
application/agent-trust-passport+json
application/agent-trust-passport+jws
application/agent-revocation-list+json
```

The complete project-specific media types are not IANA-registered. Documentation MUST NOT represent them as registered types. The `+json` and `+jws` structured syntax suffixes may be used according to their registered semantics.

The protected JWS header uses:

```json
{
  "typ": "atp+jws",
  "cty": "application/agent-trust-passport+json"
}
```

## Precedence

Normative modules under `spec/` control over examples and prose summaries. Accepted ADRs record architectural intent but do not override a later normative correction. Schemas enforce machine structure but do not replace semantic requirements that JSON Schema cannot express.

## Data and Encoding

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Canonical format

The canonical machine format is JSON. All hashed or signed JSON MUST be serialized using RFC 8785 JSON Canonicalization Scheme and encoded as UTF-8 without a byte-order mark.

Canonical artifacts MUST reject duplicate object keys, non-finite numbers, implementation-specific types, and integers outside `[-9007199254740991, 9007199254740991]`. Alpha.1 schemas use integers rather than fractional numbers for governance values.

## YAML authoring

Profiles MAY be authored in YAML, but YAML source bytes are never canonical. A YAML loader MUST reject duplicate keys, custom tags, non-JSON scalar types, implicit timestamps, non-finite numbers, and anchors or aliases that produce ambiguous materialization. The resulting strict JSON data model is validated and canonicalized.

## Timestamps and hashes

Timestamps MUST use RFC 3339 UTC, whole-second precision, and the `Z` suffix. `not_before` is inclusive. `expires_at` and `next_update` are exclusive.

SHA-256 identifiers MUST use lowercase hexadecimal:

```text
sha256:<64 lowercase hexadecimal characters>
```

## Bundle-relative paths

A bundle path MUST be NFC-normalized Unicode, relative, forward-slash separated, and free of empty segments, `.` segments, `..` segments, backslashes, control characters, drive prefixes, and leading slashes. Symlinks are prohibited.

A manifest MUST reject duplicate NFC paths and case-insensitive collisions using Unicode case folding.

## Canonical bundle manifest

A canonical bundle manifest contains `schema_version`, `bundle_id`, and a `files` array. Each file entry contains canonical path, media type, byte length, content hash, and canonicalization mode.

For JSON or `+json` media types, the content hash is calculated over `UTF8(JCS(parsed_json))`. For all other media types, the content hash is calculated over exact file bytes. Implementations MUST NOT silently normalize line endings.

The `files` array is `SET_LIKE` and MUST be sorted by canonical path. `bundle_id` is:

```text
sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agentic-assessment-bundle.identifier.v1",
    "manifest": manifest_without_bundle_id
  }))
)
```

with the required `sha256:` prefix.

## Array semantics

Every array is either `ORDERED` or `SET_LIKE`.

- `tools`: `SET_LIKE`, sort by `tool_id`.
- `mcp_servers`: `SET_LIKE`, sort by `mcp_server_id`.
- `conditions`: `SET_LIKE`, sort by `condition_id`.
- `revocation entries`: `SET_LIKE`, sort by `passport_id`, then `revocation_id`.
- `data_classes`, `purposes`, `jurisdictions`, `critical_extensions`, and evidence-hash lists: `SET_LIKE`, sort by Unicode code-point order.
- evaluation steps and approval chains: `ORDERED`.

Duplicates in a set-like array MUST be rejected before JCS serialization.
## RFC 8785 object-property ordering

Object properties MUST be ordered lexicographically by their UTF-16 code units, as required by RFC 8785. Unicode scalar-value, UTF-8, and UTF-32 ordering are not interchangeable with this rule. Inputs containing lone UTF-16 surrogates MUST be rejected.

## Bundle-path validation

A bundle path MUST already be Unicode NFC, use forward slashes, be relative, contain no drive prefix, contain no empty, `.` or `..` segment, and contain no C0, C1, DEL, or null control character. Comparison for collision detection uses NFC followed by Unicode case folding. Implementations that inspect a filesystem MUST reject symbolic links.

## Timestamp profile

Alpha.1 timestamps use the strict RFC 3339 UTC profile `YYYY-MM-DDTHH:MM:SSZ`. Offsets, fractional seconds, lowercase `z`, malformed calendar dates, and leap seconds are prohibited. Validation failures MUST produce controlled errors rather than parser exceptions.

## Assessment Model

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

## Verification Model

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Verification components

A verification result reports:

```text
structure
version
identifier
critical_extensions
signature
signing_key
issuer_authentication
bindings
revocation
validity
conditions
```

Component values are `PASS`, `FAIL`, `NOT_APPLICABLE`, `NOT_PRESENT`, `NOT_ESTABLISHED`, or `UNKNOWN`.

## Primary statuses

```text
VALID
INVALID_STRUCTURE
UNSUPPORTED_VERSION
INVALID_IDENTIFIER
UNSUPPORTED_CRITICAL_EXTENSION
INVALID_SIGNATURE
UNKNOWN_SIGNING_KEY
UNTRUSTED_ISSUER
BOUND_INPUTS_UNAVAILABLE
BOUND_INPUTS_INCOMPLETE
INPUT_MISMATCH
UNSUPPORTED_PROFILE
UNSUPPORTED_EVALUATOR
UNSUPPORTED_POLICY
DATA_AUTHORITY_UNKNOWN
DATA_AUTHORITY_INVALID
SIGNING_KEY_REVOKED
SIGNING_KEY_COMPROMISED
SIGNING_KEY_NOT_YET_VALID
SIGNING_KEY_EXPIRED
REVOKED
REVOCATION_STATUS_UNKNOWN
NOT_YET_VALID
EXPIRED
```

`CONDITION_OVERDUE` is not a primary status. It is a diagnostic finding indicating malformed issuance or historical analysis because a conditional passport must expire no later than its earliest condition deadline.

## Evaluation order

The verifier evaluates:

1. JSON, schema, and canonical-data structure.
2. supported versions.
3. passport identifier.
4. critical extensions.
5. signed or unsigned branch.
6. signing key and issuer trust for signed artifacts.
7. bound-input availability, completeness, profile support, and equality.
8. data-authority evidence, inventory, action-authority, assessment projection, condition, and evidence-reference consistency.
9. revocation-list trust, freshness, chain state, and membership.
10. `not_before` and `expires_at`.

The first failure in this order determines the primary status, except a confirmed `REVOKED`, `SIGNING_KEY_REVOKED`, or `SIGNING_KEY_COMPROMISED` result overrides later time checks.

## Unsigned artifacts

For an unsigned passport:

```yaml
signature: NOT_PRESENT
signing_key: NOT_APPLICABLE
issuer_authentication: NOT_ESTABLISHED
```

The passport may receive primary status `VALID` if all requirements applicable to its declared unsigned branch pass. `VALID` does not mean issuer-authenticated.

## Reference CLI state fields

For passport validation, the reference CLI emits these state layers separately:

```text
issued_assessment_result
verification_primary_status
operating_disposition
```

The CLI MUST NOT substitute one generic `decision` field for these values. A signed, trusted, unrevoked passport with issued result `APPROVED` reports `APPROVED / VALID / PERMITTED`. A structurally valid unsigned passport may report `APPROVED / VALID / INDETERMINATE`. A revoked passport reports its issued result, verification status `REVOKED`, and operating disposition `NOT_PERMITTED`.

For non-passport artifacts, these passport-specific fields are `null` unless the artifact itself is an assessment or verification result. `artifact_validation_status` reports whether the implemented parsing, schema, semantic, and identifier checks passed; it does not replace the three passport state layers.

## Binding outcomes

- `BOUND_INPUTS_UNAVAILABLE`: no required bundle was supplied.
- `BOUND_INPUTS_INCOMPLETE`: a bundle was supplied but one or more required bound artifacts are missing.
- `INPUT_MISMATCH`: all required artifacts are present and one or more hashes, cross-artifact identifiers, projections, conditions, references, inventory declarations, or action-authority values differ.
- `UNSUPPORTED_PROFILE`: the declared or bound profile identity or version is not admitted by the Alpha.1 reference policy.
- `UNSUPPORTED_EVALUATOR`: the declared evaluator identity or version is not supported.
- `UNSUPPORTED_POLICY`: the declared assessment-policy identity or version is not supported.
- `DATA_AUTHORITY_UNKNOWN`: the evidence scheme or issuer is not supported or trusted.
- `DATA_AUTHORITY_INVALID`: admitted evidence is malformed, expired, internally inconsistent, not applicable to the subject or declared use, or fails its content-derived artifact hash.

The Alpha.1 reference CLI requires both `--bundle-manifest` and `--bundle-root` for passport validation. It MUST NOT emit `fully_validated: true` or a permitted operating disposition until the manifest, profile descriptor, profile document, inventories, action-authority graph, data-authority evidence, assessment projection, conditions, and evidence references all pass.

## Reference operating policy

Issued result and primary status are combined under institutional policy.

- `APPROVED + VALID + ISSUER_SIGNED` maps to `PERMITTED` when the issuer and scope are trusted.
- `APPROVED_WITH_CONDITIONS + VALID` maps to `PERMITTED_WITH_CONDITIONS` only when every active condition is enforceable.
- `RESTRICTED + VALID` maps to `RESTRICTED`.
- `REJECTED` maps to `NOT_PERMITTED`.
- `VALID + NONE` maps to `INDETERMINATE` by default and `NOT_PERMITTED` under fail-closed policy.
- Every non-`VALID` primary status maps to `NOT_PERMITTED` under fail-closed policy.

No policy may represent `REVOCATION_STATUS_UNKNOWN` as evidence that a passport is not revoked.
## Independently anchored reference policy

For the bundled Alpha.1 reference profile, the verifier MUST compare the supplied profile descriptor and profile document with independently pinned canonical hashes. The submitted bundle MUST NOT redefine supported controls, issuers, schemes, signature requirements, evaluator identity, assessment policy, or production posture while retaining the same profile ID and version. A mismatch produces `UNSUPPORTED_PROFILE` or another non-permitted status.

## Agent Trust Passport

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Structure

An Agent Trust Passport contains:

```text
schema_version
framework
profile
passport_id
issuer
subject
issued_assessment
assurance
bindings
validity
conditions
extensions
critical_extensions
proof, only for signed passports
```

The JSON Schema defines separate signed and unsigned branches.

## Unsigned branch

An unsigned passport MUST use `assurance.attestation_status = NONE` and MUST omit `proof`.

## Signed branch

A signed passport MUST use `assurance.attestation_status = ISSUER_SIGNED` and MUST contain exactly:

```json
{
  "proof": {
    "jws": "<protected-header>..<signature>"
  }
}
```

Outer `algorithm`, `key_id`, `format`, `typ`, and `cty` fields are prohibited. The protected JWS header is the only cryptographic source of truth.

## Identifier

The identifier source is the complete passport without `passport_id` and `proof`.

```text
passport_id = sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agent-trust-passport.identifier.v1",
    "passport": passport_without_passport_id_and_proof
  }))
)
```

The signed payload is the complete passport without `proof`, including `passport_id`.

## Conditions

Conditions are set-like and sorted by `condition_id`. Each condition requires owner, deadline, required evidence, temporary restriction, and closure rule. `expires_at` MUST be earlier than or equal to the earliest condition deadline.

## Extensions

Extension members appear only inside `extensions`. `critical_extensions` is a sorted set of extension keys that must be understood. Every critical extension key MUST exist in `extensions`.

## Bindings

A passport binds to the assessment bundle, action-authority graph, agent inventory, MCP inventory, tool inventory, control profile, machine-readable profile descriptor, evaluator identity and version, assessment-policy identity and version, framework and profile versions, evaluation time, assurance vector, issued result, issuer identity, and all admitted data-authority evidence hashes.

The `issued_assessment` projection includes the bound assessment identifier and data-authority status. The passport condition array MUST equal the complete ordered condition array in the bound assessment. Any semantic change to a bound input requires a new assessment and passport.

### Alpha.1 inventory and profile boundary

Alpha.1 defines minimal agent-, MCP-, and tool-inventory schemas. The reference verifier validates their structure, subject identity, set ordering, non-production declaration, tool-to-graph agreement, and action-level consistency.

The profile descriptor is machine readable. It binds the profile ID and version, assessment policy, evaluator, supported controls, supported data-authority schemes, trusted data-authority issuers, production-use posture, and exact control-profile document hash.

The quickstart uses non-empty synthetic inventories. The SHA-256 hash of JCS-canonical `{}` MUST NOT support a permitted Alpha.1 decision.

## Signature Profile

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Algorithm allowlist

Alpha.1 issuance and verification MUST use JOSE `alg = Ed25519`. Deprecated `EdDSA`, `none`, and every other algorithm MUST be rejected.

## Detached Compact JWS

Alpha.1 uses standard detached Compact JWS under RFC 7515. The protected `b64` parameter is absent, so its effective value is `true`. RFC 7797 unencoded-payload mode is prohibited.

The signing procedure is:

```text
payload_json = JCS(passport_without_proof)
payload = UTF8(payload_json)

protected_json = JCS(protected_header)
protected = UTF8(protected_json)

protected_b64 = BASE64URL(protected)
payload_b64 = BASE64URL(payload)

signing_input = ASCII(protected_b64 + "." + payload_b64)
signature = Ed25519-SIGN(private_key, signing_input)

proof.jws = protected_b64 + ".." + BASE64URL(signature)
```

Base64url padding is omitted.

## Protected header

The protected header MUST contain exactly:

```json
{
  "alg": "Ed25519",
  "kid": "<issuer-scoped JWK thumbprint URI>",
  "typ": "atp+jws",
  "cty": "application/agent-trust-passport+json"
}
```

No unprotected header is permitted. Unknown protected-header parameters are rejected in Alpha.1.

## Key identity

Keys are resolved by `(issuer_id, kid)`. `kid` SHOULD be a JWK Thumbprint URI based on an RFC 7638 SHA-256 thumbprint.

A public Ed25519 JWK uses `kty = OKP`, `crv = Ed25519`, `alg = Ed25519`, `use = sig`, `key_ops = [verify]`, and public parameter `x`. Public key records MUST reject private parameter `d`.

## Key lifecycle

A trusted-key record identifies administrative status and validity interval. Verifiers distinguish `ACTIVE`, `RETIRED`, `REVOKED`, `COMPROMISED`, `NOT_YET_VALID`, and `EXPIRED` states and return the corresponding signing-key status.

Retired keys MAY verify artifacts issued while the key was valid only under a separately documented institutional policy with sufficient retirement-time evidence. The Alpha.1 reference validator conservatively rejects RETIRED keys. Revoked or compromised keys fail closed.

## Test keys

Private production keys MUST NOT enter the repository. Deterministic conformance vectors MAY contain explicitly labeled test-only seed material that has no operational value.

## Revocation-list protected header

Revocation lists use the same detached-JWS construction with `typ = atp-revocation+jws` and `cty = application/agent-revocation-list+json`. Verifiers MUST validate the exact protected-header key set, `alg`, `kid`, `typ`, `cty`, detached payload segment, base64url encoding, and Ed25519 signature.

## Revocation

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Cumulative list model

Alpha.1 revocation lists are cumulative. A current list contains every passport revocation still effective for its issuer and framework.

Sequence numbers begin at `1` and strictly increase. Sequence `1` uses `previous_list_hash = null`. Every later list uses the immediately preceding accepted `list_id` as `previous_list_hash`.

A repeated sequence number is accepted only when its `list_id` is identical to the previously accepted list. A lower sequence number, different repeated list, broken chain, invalid signature, untrusted authority, inconsistent chronology, or expired `next_update` produces `REVOCATION_STATUS_UNKNOWN` unless a more specific key failure applies.

## Revocation entry identifier

The identifier source is the complete entry without `revocation_id`:

```text
revocation_id = sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agent-trust-passport.revocation-entry.identifier.v1",
    "entry": entry_without_revocation_id
  }))
)
```

A list MUST contain at most one entry for a passport. Duplicate or contradictory entries are invalid. In the Alpha.1 minimal authority model, every entry `authority` MUST equal the list `issuer_id`; delegated revocation authority is not supported. Every `revoked_at` MUST be no later than the list `issued_at` and MUST precede `next_update`.

## List identifier

The list identifier source is the complete list without `list_id` and `proof`:

```text
list_id = sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agent-trust-passport.revocation-list.identifier.v1",
    "list": list_without_list_id_and_proof
  }))
)
```

The signed payload is the complete list without `proof`, including `list_id`. The signature profile is the same Ed25519 detached-JWS profile used for passports, with content type `application/agent-revocation-list+json`.

## Entry order and reasons

Entries are set-like and sorted by `passport_id`, then `revocation_id`.

Reason codes are:

```text
INPUT_CHANGED
EVIDENCE_INVALID
ISSUER_COMPROMISED
SIGNING_KEY_COMPROMISED
CONTROL_FAILURE_DISCOVERED
PASSPORT_REPLACED
PASSPORT_ISSUED_IN_ERROR
SYSTEM_DECOMMISSIONED
OTHER
```

## Rollback-protected state

A stateful verifier stores the highest accepted sequence number, list identifier, and `next_update` for each revocation authority and framework.

A stateless verifier cannot establish list freshness against rollback. When policy requires rollback protection and trusted state is unavailable, it MUST return `REVOCATION_STATUS_UNKNOWN`.

## Distribution and caching

A list is usable only before `next_update`. Caches MUST NOT extend validity beyond `next_update`. Fetch failure, stale cache, or untrusted distribution metadata does not mean a passport is not revoked.

## Action Authority

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Levels

- Level 0: advisory output with no external execution capability.
- Level 1: read-only access to approved information.
- Level 2: drafting or proposing changes without submission or execution.
- Level 3: bounded, logged, reversible internal action with defined rollback.
- Level 4: privileged or externally consequential action affecting production, identities, sensitive data, external communications, security controls, or material business processes.
- Level 5: destructive, financial, legal, employment, human-safety, critical-infrastructure, mission-critical, or irreversible high-impact consequence.

## Reachable action graph

Authority is calculated from the complete reachable action graph, not isolated tool labels. The graph includes agents, subagents, tools, resources, data paths, approval gates, and execution edges.

An implementation MUST evaluate every authority dimension represented by the applicable schema and governance profile. Alpha.1’s reference calculation is limited to the fields defined in the Alpha.1 action-authority graph. Future profiles may add batch size, transaction value, frequency, tool installation or chaining, reversibility time, rollback completeness, and human-approval strength as explicit schema inputs.

A chain is assigned at least the maximum consequence reachable through any permitted path. Composition MAY raise the level above every individually declared tool level.


## Alpha.1 reference calculation

The reference calculation starts with the maximum of `requested_level` and every `base_level` reachable from the declared `agent_id`. It then applies these minimum floors:

- delegation, unattended execution, or code execution: Level 3;
- credential change, identity change, external publication, data movement, no reversibility, organizational or external blast radius: Level 4;
- self-modification or critical blast radius: Level 5;
- partial reversibility or team blast radius: Level 3.

`computed_level` MUST equal the maximum resulting level. Node identifiers MUST be unique, the declared agent node MUST exist and have type `AGENT`, every edge endpoint MUST exist, duplicate edges are prohibited, and every declared node MUST be reachable from the agent node.

## Alpha.1 Level 5 rule

No Alpha.1 profile may issue `APPROVED` or `APPROVED_WITH_CONDITIONS` for requested Level 5 authority. A Level 5 request produces `RESTRICTED` or `REJECTED` according to the specific action and profile.

Assessment of a Level 5 declaration does not authorize the action.


## Passport binding

A passport that carries action authority MUST bind one action-authority graph through the canonical bundle manifest. The verifier MUST validate the graph, recalculate `computed_level`, require the graph agent to equal the passport subject, require graph tool nodes and tool-inventory declarations to agree, and require the calculated level not to exceed the bound assessment or passport maximum. A Level 5 graph cannot support a permitted Alpha.1 disposition.
## Alpha.1 controlled authority vocabulary

The reference profile restricts agent capabilities, MCP scopes, and tool effects to versioned controlled vocabularies with deterministic minimum action levels. Every declared MCP server MUST appear as a reachable `MCP_SERVER` node. The node level MUST cover every declared server scope. Tool effects and agent capabilities MUST NOT require a level above the graph's reproducible `computed_level`. Unknown terms fail schema validation.

Reachable graph edge types also contribute minimum authority. A `PUBLISHES` edge requires `dimensions.external_publication=true` and Level 4 or higher. A `DELEGATES` edge requires `dimensions.delegation=true` and Level 3 or higher.

For `APPROVED_WITH_CONDITIONS`, the effective maximum action level is the minimum of the assessment maximum, passport maximum, and every active condition's temporary maximum. The graph MUST NOT exceed that effective ceiling.

## Data Authority Interoperability

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Boundary

Agentic AI Governance evaluates whether declared agent use is compatible with admitted data-authority evidence. It MUST NOT create, infer, or re-adjudicate underlying data rights.

## Generic evidence binding

A data-authority binding identifies evidence scheme and version, issuer, artifact hash, data classes, purposes, systems, jurisdictions, prohibited uses, and validity interval.

An adapter MUST validate supported scheme version, artifact integrity, issuer trust, signature when required, revocation, validity, scope, purposes, data classes, restrictions, and jurisdictional constraints.

## Absence or uncertainty

When required data-authority evidence is absent or cannot be verified, `data_authority_status` is `UNKNOWN`. The issued assessment MUST be `RESTRICTED` or `REJECTED`; it MUST NOT be `APPROVED` or `APPROVED_WITH_CONDITIONS`. Invalid authority evidence requires `data_authority_status = INVALID` and an issued result of `REJECTED`.

Omitting a data declaration does not make data-authority controls inapplicable when tools, MCP resources, or other declarations indicate governed data access.

## Alpha.1 reference adapter

The Alpha.1 reference profile admits only the synthetic scheme:

```text
global-ai-governance.synthetic-authority / 0.1.0
```

The machine-readable profile descriptor lists the supported scheme and trusted issuer. The reference verifier validates the evidence schema, semantic ordering, content-derived `artifact_hash`, subject, current validity, trusted issuer, declared-use scope, prohibited uses, and every assessment or condition evidence reference.

The synthetic scheme does not require a separate evidence signature because the complete bundle and evidence hash are bound by the issuer-signed passport. It is test-only and prohibits production use. Future operational adapters may require their own signatures, revocation state, delegation chains, jurisdictional rules, and external trust anchors.

A future profile may define a Data Trust Passport adapter. Alpha.1 has no external adapter dependency.
## Evidence-time and scheme-policy enforcement

Evidence supporting `data_authority_status: VERIFIED` MUST be valid both when the bound assessment was evaluated and at the verifier's presentation time. The supported scheme, issuer set, and `requires_signature` policy come from the independently pinned reference-policy anchor rather than from mutable bundle content.

## Conformance

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Conformance classes

- `SCHEMA_CONFORMANT`: artifact validates against the identified schema.
- `SEMANTIC_CONFORMANT`: artifact also satisfies ordering, identifier, branch, timing, cross-reference, and result-consistency rules.
- `CRYPTO_CONFORMANT`: signed artifact satisfies the protected-header, signing-input, key, and signature profile.
- `REFERENCE_POLICY_CONFORMANT`: verification and operating mapping match the reference fail-closed policy.

Schema conformance alone does not imply semantic, cryptographic, operational, or security conformance.

## Bundled evidence

The repository includes canonical JSON vectors, valid examples, negative fixtures, passport and revocation identifiers, signed and unsigned branches, deterministic Ed25519 detached JWS fixtures, timestamp boundaries, supported-version and critical-extension decisions, machine-readable profile descriptors, inventory schemas, complete bound-input verification, data-authority evidence admission, evidence-reference resolution, complete condition equality, action-authority graph reconciliation, revocation chronology and authority controls, bundle-path controls, operating mappings, and content-derived identifier checks.

Every JSON fixture in `tests/negative/` MUST be listed in `tests/negative/index.json` and rejected by the designated validator.

## Determinism

Fixtures use exact UTF-8 bytes and committed expected hashes. Test-only cryptographic keys are explicitly labeled and MUST NOT be used operationally.

## Assurance boundary

A green repository test run demonstrates consistency of the bundled examples and implemented reference-validation subset. It does not prove factual declarations, live-system state, secure key custody, legal compliance, institutional authorization, or production safety.

## References

**Status:** Alpha.1 public reference register.

## Normative references

- BCP 14, RFC 2119 and RFC 8174, requirement terminology.
- RFC 3339, Internet date and time format.
- RFC 7515, JSON Web Signature, including detached content.
- RFC 7517, JSON Web Key.
- RFC 7638, JSON Web Key Thumbprint.
- RFC 7797, JWS Unencoded Payload Option, explicitly excluded from Alpha.1.
- RFC 8032, Edwards-Curve Digital Signature Algorithm.
- RFC 8037, CFRG curves for JOSE and OKP key representation.
- RFC 8785, JSON Canonicalization Scheme.
- RFC 9278, JWK Thumbprint URI.
- RFC 9864, fully specified JOSE and COSE algorithms.
- JSON Schema Draft 2020-12 Core and Validation.
- Apache License 2.0.
- Creative Commons Attribution 4.0 International.

## Profile baseline references

- Model Context Protocol Specification, revision `2025-11-25`.
- Model Context Protocol Security Best Practices, informative operational guidance; it is mutable and not a normative Alpha.1 dependency.

## Informative references

- IANA JSON Web Signature and Encryption Algorithms registry.
- IANA media-type and structured-syntax-suffix registries.
- OWASP Agentic Applications guidance.
- Cloud Security Alliance MAESTRO.
- SPDX License List.

