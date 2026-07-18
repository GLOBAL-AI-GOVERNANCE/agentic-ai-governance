<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# ADR-002: Unsigned Passport Semantics

**Status:** Accepted for `v0.1.0-alpha.1`.

## Decision

Unsigned passports use `attestation_status = NONE` and omit `proof`. Signed passports use `ISSUER_SIGNED` and require `proof.jws`.

An unsigned passport may be structurally and semantically `VALID`, but its verification components report `signature = NOT_PRESENT`, `signing_key = NOT_APPLICABLE`, and `issuer_authentication = NOT_ESTABLISHED`.

The reference policy maps a valid unsigned passport to `INDETERMINATE`, or `NOT_PERMITTED` under fail-closed policy. It is never automatically issuer-authenticated or permitted.
