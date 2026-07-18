<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# ADR-003: Revocation List Model

**Status:** Accepted for `v0.1.0-alpha.1`.

## Decision

Alpha.1 uses cumulative, Ed25519-signed revocation lists with strictly increasing sequence numbers and a `previous_list_hash` chain. Verifiers persist the highest accepted sequence, list identifier, and `next_update` by authority and framework.

When rollback-protected state or a fresh trusted list is unavailable and policy requires revocation checking, the result is `REVOCATION_STATUS_UNKNOWN`, never evidence of non-revocation.
