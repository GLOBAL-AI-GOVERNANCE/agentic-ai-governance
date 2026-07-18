<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Status and Scope

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
