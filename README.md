<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agentic AI Governance

An experimental, machine-readable trust layer for describing what an AI agent is, what it may reach, what it may do, what evidence supports it, and when its authority expires or is revoked.

**Release:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. The specification and schemas are not frozen.

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

## Five-minute validation

Install the development dependencies:

```bash
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

The three public state fields are deliberately separate. The issued assessment records what was approved, the verification status records what was established at presentation time, and the operating disposition records what the reference policy permits now.

A signed passport is never reported as fully validated or permitted when its version, profile, evaluator, policy, or critical extensions are unsupported; required evidence is missing, expired, invalid, or untrusted; conditions or evidence references disagree with the bound assessment; inventories or action authority are inconsistent; its signature or key fails; its identifier or validity fails; or current revocation state was not supplied.

## Validation levels

- **Structural validation:** strict JSON parsing, schema validation, and semantic consistency.
- **Artifact validation:** structural validation plus content-derived identifiers and reproducible graph calculations.
- **Trust validation:** artifact validation plus critical-extension handling, signature verification, signing-key trust, supported profile and evaluator checks, full semantic verification of bound evidence and inventories, action-authority reconciliation, time validity, and supplied revocation state.

Unsigned passports may have `verification_primary_status: VALID` while remaining `operating_disposition: INDETERMINATE` because they do not establish issuer authentication.

> **Stateless revocation note:** the reference CLI validates the signed revocation-list snapshot supplied for the current run. It does not remember the highest accepted list sequence across runs and therefore does not provide rollback protection by itself. Production verifiers must persist trusted revocation state.

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

Passing these checks confirms that the bundled examples and implemented Alpha.1 validation subset remain internally consistent. It does not establish operational safety, factual truth of declarations, production key custody, legal compliance, certification, or institutional authorization.

See [CONFORMANCE.md](CONFORMANCE.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md).

## Licensing

Code, schemas, tests, utilities, and machine-readable fixtures are Apache-2.0. Specifications, profiles, ADRs, and prose documentation are CC-BY-4.0. See [LICENSE_POLICY.md](LICENSE_POLICY.md).

### Canonical profile and authority semantics

The reference validator does not accept a submitted bundle as the authority for redefining a supported profile. It independently pins the canonical profile descriptor and profile-document hashes for Alpha.1. The permitted decision path also applies active condition ceilings and controlled minimum action levels for agent capabilities, MCP scopes, tool effects, and graph edge types. Unknown declaration terms fail closed.

