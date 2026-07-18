<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Data and Encoding

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

