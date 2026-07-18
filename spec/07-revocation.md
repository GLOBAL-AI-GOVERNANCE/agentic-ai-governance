<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Revocation

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
