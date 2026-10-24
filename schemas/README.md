<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Schemas

This directory contains versioned JSON Schemas used by Agentic AI Governance.

Existing Alpha.1 schema identifiers and raw-file SHA-256 digests are immutable. New versions may coexist only when listed in `schema-catalog.json` with an explicit immutable identifier, content digest, artifact version, lifecycle status, and supersession relationship.

The `v0.1.0-alpha.4` Agent Fleet Controls schemas are `fleet-controls-common`, `fleet-controls-profile`, `fleet-action-request`, `sub-agent-passport-binding`, and `passport-suspension-list`. They have new tagged identities and reuse the Alpha.1 common definitions by absolute reference.

`schema-catalog.schema.json` is the fixed repository-governance root used to validate the catalog before other catalog entries are loaded. The catalog is repository metadata, not a protocol artifact.
