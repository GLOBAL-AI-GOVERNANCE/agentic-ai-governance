<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# v0.1.0-alpha.1 Release Notes

Agentic AI Governance is an experimental machine-readable trust layer for describing and validating agent identity, data authority, MCP connections, tools, action authority, evidence, validity, and revocation.

## Available now

- Modular specification and versioned JSON Schemas.
- Signed and unsigned Agent Trust Passports.
- Assessment, bundle, verification, trusted-key, revocation, data-authority, and action-authority artifacts.
- Machine-enforced data-authority status caps for issued assessments.
- Versioned Alpha.1 agent, MCP, and tool inventory schemas with subject and action-authority consistency checks.
- Strict JSON and RFC 8785 reference utilities.
- Ed25519 detached-JWS and signing-key trust validation.
- A five-minute synthetic quickstart with a complete, internally coherent bound-input bundle and signed-passport decision path.
- Separate issued-assessment, verification-status, and operating-disposition fields in machine-readable CLI output.
- Fail-closed supported-version, critical-extension, bound-input, passport-summary, trusted-key, revocation-chronology, and revocation-authority validation.
- Positive, negative, malformed-input, identifier, signature, key-lifecycle, validity, binding, and revocation tests.


- Machine-readable agent, MCP, tool, and control-profile descriptor schemas.
- Complete semantic admission of data-authority evidence, including current validity, supported scheme, trusted issuer, subject, scope, content-derived artifact hash, and reference resolution.
- Exact assessment ID, data-authority status, control summary, and condition reconciliation.
- Required action-authority graph binding with graph recalculation and tool-inventory agreement.
- Bidirectional MCP inventory and action-graph reconciliation, rejecting both missing and undeclared MCP server nodes.
- Exact supported profile, evaluator, and assessment-policy identifiers and versions.
- Connected dependency advisory auditing in CI through pinned `pip-audit`.

## Assurance boundary

This alpha is not a certification system, production authorization service, live-system monitor, legal-compliance determination, or guarantee that declarations and evidence are factually true. The schemas and specification are experimental and not frozen.

- The Alpha.1 verifier independently anchors the canonical profile and enforces active condition restrictions plus controlled capability, MCP-scope, tool-effect, and graph-edge authority semantics.
