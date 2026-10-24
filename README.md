<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agentic AI Governance

<!-- gaig:nav -->
**[Global AI Governance](https://ai-governance.solutions/)** · `v0.1.0-alpha.4 · available` · `authority_effect: NONE`

[Connect your agent](https://ai-governance.solutions/connect.html#agents) · [Specifications](https://ai-governance.solutions/connect.html#spec) · [All products](https://ai-governance.solutions/#products)
<!-- /gaig:nav -->

A machine-readable trust layer for describing what an AI agent is, what it may reach, what it may do, what evidence supports it, and when its authority expires or is revoked.

**Latest tagged release:** `v0.1.0-alpha.4`
**Status:** Available. Schemas, validator, CLI, and the installable package ship in `v0.1.0-alpha.4` and are tested on every change. Schemas stay open to change until a second, independent verifier confirms them; that review is open.
**Stateful Revocation:** `Released · tested` in Alpha.2 as bounded optional local continuity relative to an intact trusted local store.
**Alpha.1:** remains an immutable historical release and does not contain Stateful Revocation.
**OPA Enforcement Bridge:** on main · `tested` reference implementation; non-enforcing.

**Agent Incident Readiness:** on main · `tested` synthetic lifecycle demonstration; it does not act on live systems.

**Agent Fleet Controls:** `v0.1.0-alpha.4` · `tested` reference. Per-level status freshness, suspension, fleet action terms, a delegation depth cap, and sub-agent passports bound to their parent. See [Agent Fleet Controls](#agent-fleet-controls).

The repository provides specifications, JSON Schemas, examples, conformance fixtures, and a reference validator for teams building governed agentic systems.

> This is not an MCP scanner, autonomous remediation platform, certification service, production policy engine, or legal-compliance guarantee.

## Start here

**Five-minute path:** [validate a complete signed passport decision](examples/quickstart/README.md)  
**Specification:** [read the generated Alpha.1 specification](dist/AGENTIC_AI_GOVERNANCE_SPEC.md)

## Who this is for

Designed for AI platform teams, security architects, governance engineers, assurance teams, framework authors, and developers building compatible validation tooling.

## How it works

1. **Describe requested authority.** Model the agent, tools, resources, and reachable actions.
2. **Assess the request.** Record control outcomes, evidence, restrictions, and the maximum action level.
3. **Issue a passport.** Produce an unsigned declaration or issuer-signed Agent Trust Passport.
4. **Validate trust.** Check strict JSON, supported versions, schema, semantics, identifiers, critical extensions, signatures, signing-key trust, profile and evaluator support, complete bound evidence, inventory and action-authority consistency, validity, and revocation.
5. **Expire or revoke authority.** Apply time limits and a signed cumulative revocation list.
6. **Evaluate bounded policy.** An optional current-main OPA bridge consumes the established validation result and returns the existing operating-disposition vocabulary without performing external enforcement.

**Lead agents and sub-agents.** A lead agent (orchestrator) that coordinates a fleet declares its sub-agents as `SUBAGENT` nodes and its delegations as `DELEGATES` edges in its action graph. Any declared delegation sets a minimum of Level 3 ([Action Levels](spec/08-action-authority.md)), so the lead agent is assessed for everything it can reach through other agents. Delegation-chain depth, authority inheritance, and termination are not yet modeled.

## Five-minute validation

Install the development dependencies. A virtual environment can live inside or outside the checkout: the schema-catalog check skips `.venv/`, `venv/`, `node_modules/`, and similar local environment folders.

```bash
python -m venv ../agentic-venv && . ../agentic-venv/bin/activate   # optional
python -m pip install -r requirements-dev.txt
```

Run a complete signed-passport validation using the synthetic examples:

```bash
python tools/validate_artifact.py \
  --kind passport \
  --trusted-key examples/trusted-keys/test-ed25519-key.json \
  --revocation-list examples/revocation/valid-revocation-list.json \
  --bundle-manifest examples/bundles/valid-bundle-manifest.json \
  --bundle-root . \
  --at-time 2026-07-18T12:00:00Z \
  examples/passports/signed-unrevoked.json
```

PowerShell:

```powershell
python tools/validate_artifact.py --kind passport --trusted-key examples/trusted-keys/test-ed25519-key.json --revocation-list examples/revocation/valid-revocation-list.json --bundle-manifest examples/bundles/valid-bundle-manifest.json --bundle-root . --at-time 2026-07-18T12:00:00Z examples/passports/signed-unrevoked.json
```

A successful trust decision returns exit code `0` and reports:

```json
{
  "artifact_validation_status": "PASS",
  "structurally_valid": true,
  "fully_validated": true,
  "valid": true,
  "issued_assessment_result": "APPROVED",
  "verification_primary_status": "VALID",
  "operating_disposition": "PERMITTED",
  "checks": {
    "parsing": "PASS",
    "version": "PASS",
    "schema": "PASS",
    "semantics": "PASS",
    "identifier": "PASS",
    "critical_extensions": "PASS",
    "signature": "PASS",
    "signing_key_trust": "PASS",
    "bindings": "PASS",
    "validity": "PASS",
    "revocation": "PASS"
  }
}
```

> **This is an assessment, not authorization.** `APPROVED` and `PERMITTED` in this sample come from a synthetic passport checked against the reference policy. They mean the passport passed every check against the supplied key, evidence, and revocation list at the stated time. They do not authorize a deployment, an action, or access. An accountable human decides whether the agent may act, and any system that acts on this report needs its own control.

The three public state fields are deliberately separate. The issued assessment records what was approved, the verification status records what was established at presentation time, and the operating disposition records what the reference policy permits now.

A signed passport is never reported as fully validated or permitted when its version, profile, evaluator, policy, or critical extensions are unsupported; required evidence is missing, expired, invalid, or untrusted; conditions or evidence references disagree with the bound assessment; inventories or action authority are inconsistent; its signature or key fails; its identifier or validity fails; or current revocation state was not supplied.

### Install as a package

The reference validator installs from the release tag as an importable package with a `validate-passport` command. The wheel carries the validator, schemas, profiles, and synthetic examples, so no checkout is needed:

```bash
python -m pip install "git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance.git@v0.1.0-alpha.4"
validate-passport --example signed-unrevoked     # exit 0, artifact_validation_status PASS
validate-passport --example signed-revoked       # exit 1, verification_primary_status REVOKED
validate-passport passport.json --trusted-key key.json \
  --bundle-manifest bundle.json --bundle-root . --revocation-list revocations.json
```

```python
from agentic_ai_governance import validate_example, validate_passport

result = validate_example("signed-unrevoked")
print(result.exit_code, result.report["verification_primary_status"])
```

`validate_passport()` and `validate-passport` run `tools/validate_artifact.py --kind passport` in a separate process and return its JSON report unchanged. Package version `0.1.0a4` is the `v0.1.0-alpha.4` release; the attested release archive installs the same way with `python -m pip install agentic-ai-governance-v0.1.0-alpha.4.zip`. Verification is not authorization.

## Validation levels

- **Structural validation:** strict JSON parsing, schema validation, and semantic consistency.
- **Artifact validation:** structural validation plus content-derived identifiers and reproducible graph calculations.
- **Trust validation:** artifact validation plus critical-extension handling, signature verification, signing-key trust, supported profile and evaluator checks, full semantic verification of bound evidence and inventories, action-authority reconciliation, time validity, and supplied revocation state.

Unsigned passports may have `verification_primary_status: VALID` while remaining `operating_disposition: INDETERMINATE` because they do not establish issuer authentication.

### Alpha.1 and Alpha.2 revocation behavior

The tagged `v0.1.0-alpha.1` reference CLI validates only the signed revocation-list snapshot supplied for that run. `v0.1.0-alpha.2` preserves that stateless default and adds an optional local continuity mechanism. Nothing is written unless `--revocation-state PATH` is explicitly supplied, and a missing store is created only with `--initialize-revocation-state` after the supplied list passes all trust and freshness checks.

Initialize once with a fresh trusted list by adding:

```text
--revocation-state /path/to/trusted-revocation-state.json --initialize-revocation-state
```

On later invocations, supply the same path without the initialization flag. The verifier then rejects lower sequences, conflicting repeated sequences, broken predecessor links, authority/framework mismatches, malformed stores, stale lists, and cumulative lists that omit a previously trusted revocation. Invalid or unavailable state produces `REVOCATION_STATUS_UNKNOWN` and `NOT_PERMITTED`; it is never evidence of non-revocation.

This is deterministic local reference rollback protection relative to an intact trusted local store. It does not prevent host or database rollback, replacement, or deletion. It does not terminate credentials, sessions, tools, workloads, network paths, or downstream effects, and it is not production IAM, runtime containment, certification, a legal determination, or a universal safety guarantee. The local continuity implementation is released in `v0.1.0-alpha.2` within these bounded limitations.

One revocation-state path is a single-writer reference continuity store. Concurrent writers to the same state path are outside the supported Alpha.2 reference boundary.

### OPA Enforcement Bridge (reference, not promoted)

The repository includes a bounded Python reference adapter, OPA policy, synthetic vectors, and adversarial tests under [`policies/opa/`](policies/opa/README.md). The bridge accepts only an already-established canonical validation result plus a requested action, resource, policy, and context. It cannot expand validated authority, and it keeps policy denial distinct from passport revocation.

The bridge is included in `v0.1.0-alpha.3` as a reference with Delivery Status `DEFINED`; it is not promoted to a shipped capability. It makes a deterministic policy decision only; it does not verify raw passports, terminate credentials or sessions, contain workloads, enforce network or tool actions, provide production IAM, or establish certification or compliance.

### Agent Incident Readiness (reference, not promoted)

The repository includes a deterministic synthetic trace under [`examples/agent-incident-readiness/`](examples/agent-incident-readiness/README.md). It demonstrates Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized while preserving terminal revocation of the original passport. Reauthorization uses a distinct newly validated passport.

The demonstration composes existing validation-result, OPA bridge, operating-disposition, reason-code, and Stateful Revocation semantics. It adds no schema and performs no external action. It is included in `v0.1.0-alpha.3` as a reference with Delivery Status `DEFINED`; it is not promoted to a shipped capability, and it is not proof of runtime enforcement, containment, production IAM, credential or session termination, certification, compliance, or real-world effectiveness.

### Zero Trust Agent Readiness mapping (reference, not promoted)

The repository includes a [Zero Trust Agent Readiness mapping](governance/ZERO_TRUST_AGENT_READINESS_MAPPING.md) that relates existing Agentic reference primitives for declared authority, evidence binding, verification, validity, and revocation to Zero Trust agent-security concepts and records [deferred runtime controls](requirements/deferred-zero-trust-agent-controls.md). These primitives do not themselves enforce Zero Trust. The mapping is included in `v0.1.0-alpha.3` as a reference with Delivery Status `DEFINED`; it is not promoted to a shipped capability, and it does not implement production workload identity, continuous authorization, runtime isolation, behavioral monitoring, or credential or session termination; institutional authority remains necessary.

### Agent Fleet Controls

[`spec/11-agent-fleet-controls.md`](spec/11-agent-fleet-controls.md) defines how an evaluator decides whether an agent, or a sub-agent it started, may take a fleet action before it runs:

- **Status freshness by level.** Revocation and suspension status must be newer than a maximum age set per action level: 24 hours at Levels 0-1, 12 hours at Level 2, 1 hour at Level 3, 15 minutes at Level 4, and 5 minutes at Level 5. A request may tighten these values, never loosen them.
- **Suspension.** `SUSPENDED` is a reinstatable state. Revocation stays terminal, even when a suspension entry or a stale list is presented.
- **Fleet action terms.** `spawn_agent`, `provision_compute`, `install_tool`, and `network_call` require Level 4; `spend_funds` requires Level 5, which stays not permitted.
- **Delegation depth cap.** At most 3 levels below the root passport; a spawn that would exceed it is refused.
- **Sub-agent passports.** Each sub-agent has its own passport, bound to its parent by a content-addressed Sub-Agent Passport Binding. Its level, terms, and validity never exceed the parent's, and revocation or suspension of any ancestor applies to every descendant.

```bash
python tools/fleet_controls.py examples/fleet-controls/sub-agent-spawn-permitted.json   # exit 0, PERMITTED
python tools/fleet_controls.py examples/fleet-controls/ancestor-suspended.json          # exit 3, SUSPENDED
```

The profile is anchored by document and descriptor hashes pinned in the evaluator. Twenty-three synthetic vectors with pinned expected outcomes are in [`conformance/fleet-controls/`](conformance/fleet-controls/README.md). Approved by `DR-011` with Delivery Status `DEFINED` and Evidence Status `NOT_YET_ESTABLISHED`. The evaluator consumes already-verified passport and status facts; it does not verify signatures or enforce the decision. It runs from a source checkout and is not part of the installed package.

### Intelligence Assurance Gateway mapping (proposed)

A proposed [Intelligence Assurance Gateway mapping](governance/INTELLIGENCE_ASSURANCE_GATEWAY_MAPPING.md) relates existing Agentic trust primitives to ontology-neutral consequential-authority concepts while preserving current Action Authority, validation, policy, validity, revocation, and reauthorization boundaries. Its [deferred controls](requirements/deferred-intelligence-assurance-controls.md) record future requirements without changing the locked roadmap or creating a profile, evaluator, runtime-control claim, or release.

The mapping is non-normative, non-enforcing, and not promoted; it is included in the `v0.1.0-alpha.3` source as a proposal. It does not determine consciousness or sentience, attribute unexplained behavior, authorize production use, or change released Alpha semantics.

## Repository map

```text
spec/         Normative specification modules
schemas/      Versioned machine-readable contracts and schema catalog
examples/     Valid synthetic reference artifacts and quickstart
profiles/     Reusable governance profiles
governance/   Program baseline, V&V, claims, and release controls
requirements/ Deferred requirements preserved outside the active increment
tests/        Positive, negative, interoperability, governance, and CLI regressions
tools/        Build, strict parsing, validation, and conformance utilities
decisions/    Architecture and governance decisions
dist/         Reproducibly generated versioned distributions
```

## Verify the repository

```bash
python tools/build_dist.py --check
python tools/verify_repository.py .
python -m pip_audit --strict -r requirements-dev.txt
pytest -q
```

The repository verifier also enforces grounded Claims Register evidence requirements, performs case-insensitive exact-phrase scanning over declared repository surfaces, validates cataloged schema content digests, and resolves every cataloged `$ref`. Human review remains required for paraphrases and external surfaces.

Passing these checks confirms that the bundled examples, preserved Alpha.1 normative distribution, and released Alpha.2 reference tooling remain internally consistent. It does not establish operational safety, factual truth of declarations, production key custody, legal compliance, certification, or institutional authorization.

See [CONFORMANCE.md](CONFORMANCE.md), [governance/DEVELOPMENT.md](governance/DEVELOPMENT.md), and [SECURITY.md](SECURITY.md).

## Licensing

Code, schemas, tests, utilities, and machine-readable fixtures are Apache-2.0. Specifications, profiles, ADRs, and prose documentation are CC-BY-4.0. See [LICENSE_POLICY.md](LICENSE_POLICY.md).

### Canonical profile and authority semantics

The reference validator does not accept a submitted bundle as the authority for redefining a supported profile. It independently pins the canonical profile descriptor and profile-document hashes for Alpha.1. The permitted decision path also applies active condition ceilings and controlled minimum action levels for agent capabilities, MCP scopes, tool effects, and graph edge types. Unknown declaration terms fail closed.

<!-- gaig:footer -->
## Part of Global AI Governance

This repository is the **AUTHORIZE** layer: machine-readable agent authority, passport, evidence, expiry, and revocation artifacts.

**[ai-governance.solutions](https://ai-governance.solutions/)** · [Connect your agent](https://ai-governance.solutions/connect.html#agents) · [Specifications](https://ai-governance.solutions/connect.html#spec) · [All products](https://ai-governance.solutions/#products)

For agents: [llms.txt](https://ai-governance.solutions/llms.txt) · [machine-interface.json](https://ai-governance.solutions/machine-interface.json) · [AI Governance MCP](https://github.com/GLOBAL-AI-GOVERNANCE/ai-governance-mcp) (`gaig-mcp`). Compatible with Model Context Protocol (MCP) based agents.

Framework-neutral and jurisdiction-neutral. Outputs are non-authorizing (`authority_effect: NONE`). Not affiliated with or endorsed by any AI lab or platform.
<!-- /gaig:footer -->
