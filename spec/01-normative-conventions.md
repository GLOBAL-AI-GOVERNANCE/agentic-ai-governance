<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Normative Conventions

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
