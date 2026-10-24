<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agent Fleet Controls

**Version:** `v0.1.0-alpha.4`  
**Status:** Experimental public alpha. Not frozen. Additive to Alpha.1; it changes no Alpha.1 rule, schema identity, or signed example.

## Scope

This section defines how a relying evaluator decides whether one governed agent, or a sub-agent it started, may take a fleet action before the action runs. It covers status freshness by action level, suspension as a state distinct from revocation, a controlled action-term vocabulary, a delegation depth cap, and sub-agent passports bound to their parent.

The machine-readable inputs are the `v0.1.0-alpha.4` schemas `fleet-action-request`, `sub-agent-passport-binding`, `passport-suspension-list`, `fleet-controls-profile`, and `fleet-controls-common`. The profile is `profiles/agent-fleet-controls-profile.json`. The reference evaluator is `tools/fleet_controls.py`.

The evaluator consumes passport and status facts that were already verified, for example by the Alpha.1 passport validator and signed revocation list. It does not verify signatures, perform enforcement, or contact any system. Its result is a decision for an enforcement point to consume, with `external_enforcement: NOT_PERFORMED` and `authority_effect: NONE`.

## Evaluation time

`evaluated_at` is the instant the request is evaluated. A relying deployment MUST supply it from a clock it trusts, not from the requesting agent. Conformance vectors pin it so that results are reproducible.

## Effective action level

Each action term has a minimum level:

| Term | Minimum level |
| --- | --- |
| `spawn_agent` | 4 |
| `provision_compute` | 4 |
| `install_tool` | 4 |
| `network_call` | 4 |
| `spend_funds` | 5 |

The effective level is the higher of `requested_level` and the term minimum. Unknown terms fail schema validation. The acting passport MUST hold the term in `action_terms` (`ACTION_TERM_NOT_AUTHORIZED`) and a `maximum_action_level` at or above the effective level (`ACTION_LEVEL_EXCEEDS_CEILING`). The Alpha.1 Level 5 rule still applies: a Level 5 effective level is never permitted (`LEVEL_5_NOT_PERMITTED`).

## Status freshness by action level

The profile declares a maximum status age in seconds for each level 0 through 5. Maximum ages MUST NOT increase as the level rises, so higher-consequence actions need fresher status. The evaluator applies the maximum age of the effective level to both the revocation status and the suspension list:

- a list whose `issued_at` is after `evaluated_at`, or whose `next_update` is at or before `evaluated_at`, is unusable (`REVOCATION_STATUS_UNKNOWN`, `SUSPENSION_STATUS_UNKNOWN`);
- a list older than the maximum age is unusable for that level (`REVOCATION_STATUS_STALE_FOR_LEVEL`, `SUSPENSION_STATUS_STALE_FOR_LEVEL`).

A request MAY tighten the maximum ages or the depth cap through `policy_overrides`. An override that loosens either value produces `POLICY_OVERRIDE_LOOSENS`. Overrides that would make maximum ages increase with level produce `POLICY_INVALID`.

## Suspension and revocation

Revocation is terminal. A passport listed as revoked is `REVOKED` whatever any suspension entry says, and remains `REVOKED` even when the list is no longer fresh, because cumulative revocation is never undone. Reauthorization requires a distinct passport.

Suspension is reinstatable. A suspension entry is active from `suspended_at` until `reinstated_at`. While active, the passport is `SUSPENDED` and not permitted. After `reinstated_at`, the same passport may be used again. `reinstated_at` MUST be later than `suspended_at`, and a list MUST contain at most one entry per passport (`SUSPENSION_ENTRY_INVALID`). The suspension list identifier is:

```text
list_id = sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agent-fleet.suspension-list.identifier.v1",
    "list": list_without_list_id
  }))
)
```

Revocation or active suspension of any ancestor in the delegation chain applies to every descendant (`ANCESTOR_REVOKED`, `ANCESTOR_SUSPENDED`).

`passport_state` is `REVOKED` when any passport in the lineage is revoked, otherwise `SUSPENDED` when any is actively suspended, otherwise `UNKNOWN` when either status list is unusable, otherwise `ACTIVE`.

## Sub-agent passports

Each sub-agent holds its own passport. A Sub-Agent Passport Binding binds the child passport to its parent passport. The delegation chain lists bindings from the root passport to the acting agent. For each binding:

- `binding_id` MUST equal the identifier below (`DELEGATION_BINDING_ID_MISMATCH`);
- `parent_passport_id` and `issued_by` MUST identify the previous passport and its subject (`DELEGATION_PARENT_MISMATCH`);
- `delegation_depth` MUST be the parent depth plus one, with the root at depth 0 (`DELEGATION_DEPTH_MISMATCH`);
- a passport MUST NOT appear twice in a lineage (`DELEGATION_CYCLE`);
- `maximum_action_level` MUST NOT exceed the parent's (`DELEGATION_LEVEL_EXCEEDS_PARENT`);
- `action_terms` MUST be a subset of the parent's (`DELEGATION_TERMS_EXCEED_PARENT`);
- the validity window MUST lie within the parent's (`DELEGATION_VALIDITY_EXCEEDS_PARENT`).

```text
binding_id = sha256(
  UTF8(JCS({
    "domain": "global-ai-governance.agent-fleet.sub-agent-binding.identifier.v1",
    "binding": binding_without_binding_id
  }))
)
```

Every passport in the lineage MUST be within its validity window at `evaluated_at` (`PASSPORT_NOT_YET_VALID`, `PASSPORT_EXPIRED`).

## Delegation depth cap

The chain length MUST NOT exceed the effective `delegation_max_depth` (`DELEGATION_DEPTH_EXCEEDED`). A `spawn_agent` request whose new sub-agent would exceed the cap is not permitted (`SPAWN_WOULD_EXCEED_DEPTH`).

## Disposition

The result is `PERMITTED` only when no reason code applies and `passport_state` is `ACTIVE`. Otherwise it is `NOT_PERMITTED` with every applicable reason code, in the order listed by the reference evaluator. A schema-invalid request returns `REQUEST_SCHEMA_INVALID`, an unsupported profile reference returns `PROFILE_UNSUPPORTED`, and a profile whose descriptor or document hash differs from the pinned anchor returns `PROFILE_ANCHOR_MISMATCH`.

## Limitations

The evaluator does not verify signatures on passports, bindings, or status lists, does not authenticate the requesting agent, and does not stop an action itself. Conformance vectors are synthetic. Independent verification of these rules is `PROPOSED / NOT_YET_ESTABLISHED`.
