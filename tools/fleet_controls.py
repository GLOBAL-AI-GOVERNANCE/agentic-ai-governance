#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reference evaluator for Agent Fleet Controls (v0.1.0-alpha.4).

Evaluates one fleet action request against the pinned Agent Fleet Controls
profile: status freshness by action level, terminal revocation versus
reinstatable suspension, the action-term vocabulary, the delegation depth cap,
and sub-agent passport bindings whose authority never exceeds the parent.

The evaluator consumes already-verified passport and status facts. It does not
verify signatures, perform enforcement, or contact any system. Its result is a
decision for an enforcement point to consume; external_enforcement is always
NOT_PERFORMED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jsonschema import Draft202012Validator, FormatChecker

from tools.canonical_json import canonicalize
from tools.schema_catalog import full_registry
from tools.strict_json import load_strict

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-alpha.4"
PROFILE_ID = "global-ai-governance.agent-fleet-controls"
PROFILE_JSON = Path("profiles/agent-fleet-controls-profile.json")
PROFILE_MD = Path("profiles/agent-fleet-controls-profile.md")
SCHEMA_BASE = (
    "https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance/"
    "v0.1.0-alpha.4/schemas/"
)
REQUEST_SCHEMA_ID = SCHEMA_BASE + "fleet-action-request.schema.json"
PROFILE_SCHEMA_ID = SCHEMA_BASE + "fleet-controls-profile.schema.json"

# Pinned outside every request so a request cannot redefine the profile.
PINNED_DESCRIPTOR_JCS_SHA256 = "sha256:c31dd00b9fba66780021a4678c75d6933ad0105f5cc5f3fdd7220e226dc27381"
PINNED_DOCUMENT_SHA256 = "sha256:99c20851f51d3c3f9c3a26dc119b1c433d9372b8e3dcce829bf5c3ef82a9f720"

BINDING_DOMAIN = "global-ai-governance.agent-fleet.sub-agent-binding.identifier.v1"
SUSPENSION_LIST_DOMAIN = "global-ai-governance.agent-fleet.suspension-list.identifier.v1"

REASON_CODES = (
    "REQUEST_SCHEMA_INVALID",
    "PROFILE_UNSUPPORTED",
    "PROFILE_ANCHOR_MISMATCH",
    "POLICY_INVALID",
    "POLICY_OVERRIDE_LOOSENS",
    "DELEGATION_BINDING_ID_MISMATCH",
    "DELEGATION_PARENT_MISMATCH",
    "DELEGATION_DEPTH_MISMATCH",
    "DELEGATION_CYCLE",
    "DELEGATION_DEPTH_EXCEEDED",
    "DELEGATION_LEVEL_EXCEEDS_PARENT",
    "DELEGATION_TERMS_EXCEED_PARENT",
    "DELEGATION_VALIDITY_EXCEEDS_PARENT",
    "PASSPORT_NOT_YET_VALID",
    "PASSPORT_EXPIRED",
    "REVOCATION_STATUS_UNKNOWN",
    "REVOCATION_STATUS_STALE_FOR_LEVEL",
    "SUSPENSION_LIST_ID_MISMATCH",
    "SUSPENSION_ENTRY_INVALID",
    "SUSPENSION_STATUS_UNKNOWN",
    "SUSPENSION_STATUS_STALE_FOR_LEVEL",
    "PASSPORT_REVOKED",
    "ANCESTOR_REVOKED",
    "PASSPORT_SUSPENDED",
    "ANCESTOR_SUSPENDED",
    "ACTION_TERM_NOT_AUTHORIZED",
    "ACTION_LEVEL_EXCEEDS_CEILING",
    "LEVEL_5_NOT_PERMITTED",
    "SPAWN_WOULD_EXCEED_DEPTH",
)


def domain_id(domain: str, label: str, value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize({"domain": domain, label: value})).hexdigest()


def binding_id(binding: dict[str, Any]) -> str:
    source = {key: item for key, item in binding.items() if key != "binding_id"}
    return domain_id(BINDING_DOMAIN, "binding", source)


def suspension_list_id(status_list: dict[str, Any]) -> str:
    source = {key: item for key, item in status_list.items() if key != "list_id"}
    return domain_id(SUSPENSION_LIST_DOMAIN, "list", source)


def _instant(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


@lru_cache(maxsize=4)
def _validator(root: Path, schema_id: str) -> Draft202012Validator:
    registry = full_registry(root)
    schema = registry.resolver().lookup(schema_id).contents
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def max_ages_are_non_increasing(ages: dict[str, int]) -> bool:
    values = [ages[str(level)] for level in range(6)]
    return all(later <= earlier for earlier, later in zip(values, values[1:]))


def load_profile(root: Path = ROOT) -> tuple[dict[str, Any], list[str]]:
    """Load the profile and check it against the pinned anchors."""
    profile = load_strict(root / PROFILE_JSON, require_object=True)
    errors = [error.message for error in _validator(root, PROFILE_SCHEMA_ID).iter_errors(profile)]
    document_hash = "sha256:" + hashlib.sha256((root / PROFILE_MD).read_bytes()).hexdigest()
    descriptor_hash = "sha256:" + hashlib.sha256(canonicalize(profile)).hexdigest()
    if document_hash != PINNED_DOCUMENT_SHA256:
        errors.append("profile document hash does not match the pinned anchor")
    if profile.get("control_profile", {}).get("hash") != document_hash:
        errors.append("profile descriptor does not bind the profile document")
    if descriptor_hash != PINNED_DESCRIPTOR_JCS_SHA256:
        errors.append("profile descriptor hash does not match the pinned anchor")
    if not errors and not max_ages_are_non_increasing(profile["revocation_max_age_seconds"]):
        errors.append("profile maximum ages increase with level")
    return profile, errors


def effective_policy(profile: dict[str, Any], overrides: dict[str, Any] | None) -> tuple[dict[str, Any], set[str]]:
    """Apply request overrides, which may only tighten the profile."""
    reasons: set[str] = set()
    ages = dict(profile["revocation_max_age_seconds"])
    depth = profile["delegation_max_depth"]
    overrides = overrides or {}
    for level, value in overrides.get("revocation_max_age_seconds", {}).items():
        if value > ages[level]:
            reasons.add("POLICY_OVERRIDE_LOOSENS")
        ages[level] = min(value, ages[level])
    if "delegation_max_depth" in overrides:
        if overrides["delegation_max_depth"] > depth:
            reasons.add("POLICY_OVERRIDE_LOOSENS")
        depth = min(depth, overrides["delegation_max_depth"])
    if not max_ages_are_non_increasing(ages):
        reasons.add("POLICY_INVALID")
    return {"revocation_max_age_seconds": ages, "delegation_max_depth": depth}, reasons


def _result(request: dict[str, Any], **fields: Any) -> dict[str, Any]:
    result = {
        "result_kind": "global-ai-governance.fleet-action-result",
        "result_version": VERSION,
        "request_id": request.get("request_id") if isinstance(request, dict) else None,
        "evaluated_at": request.get("evaluated_at") if isinstance(request, dict) else None,
        "operating_disposition": "NOT_PERMITTED",
        "passport_state": "UNKNOWN",
        "acting_passport_id": None,
        "delegation_depth": None,
        "effective_level": None,
        "authority_ceiling": None,
        "status_max_age_seconds": None,
        "reason_codes": [],
        "external_enforcement": "NOT_PERFORMED",
        "authority_effect": "NONE",
    }
    result.update(fields)
    result["reason_codes"] = sorted(set(result["reason_codes"]), key=REASON_CODES.index)
    return result


def evaluate(request: Any, root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    if not isinstance(request, dict):
        return _result({}, reason_codes=["REQUEST_SCHEMA_INVALID"])
    if any(True for _ in _validator(root, REQUEST_SCHEMA_ID).iter_errors(request)):
        return _result(request, reason_codes=["REQUEST_SCHEMA_INVALID"])

    reasons: set[str] = set()
    profile_ref = request["profile"]
    if profile_ref["profile_id"] != PROFILE_ID or profile_ref["profile_version"] != VERSION:
        return _result(request, reason_codes=["PROFILE_UNSUPPORTED"])
    profile, profile_errors = load_profile(root)
    if profile_errors:
        return _result(request, reason_codes=["PROFILE_ANCHOR_MISMATCH"])
    policy, policy_reasons = effective_policy(profile, request.get("policy_overrides"))
    reasons |= policy_reasons

    at = _instant(request["evaluated_at"])
    root_passport = request["root_passport"]
    chain = request["delegation_chain"]

    # Delegation chain: each sub-agent passport is bound to its parent and
    # never holds more authority than the parent.
    parent = {
        "passport_id": root_passport["passport_id"],
        "subject_id": root_passport["subject_id"],
        "maximum_action_level": root_passport["maximum_action_level"],
        "action_terms": root_passport["action_terms"],
        "not_before": root_passport["not_before"],
        "expires_at": root_passport["expires_at"],
        "depth": 0,
    }
    lineage = [parent]
    seen = {parent["passport_id"]}
    for binding in chain:
        if binding["binding_id"] != binding_id(binding):
            reasons.add("DELEGATION_BINDING_ID_MISMATCH")
        if binding["parent_passport_id"] != parent["passport_id"] or binding["issued_by"] != parent["subject_id"]:
            reasons.add("DELEGATION_PARENT_MISMATCH")
        if binding["delegation_depth"] != parent["depth"] + 1:
            reasons.add("DELEGATION_DEPTH_MISMATCH")
        if binding["child_passport_id"] in seen:
            reasons.add("DELEGATION_CYCLE")
        if binding["maximum_action_level"] > parent["maximum_action_level"]:
            reasons.add("DELEGATION_LEVEL_EXCEEDS_PARENT")
        if not set(binding["action_terms"]) <= set(parent["action_terms"]):
            reasons.add("DELEGATION_TERMS_EXCEED_PARENT")
        if _instant(binding["not_before"]) < _instant(parent["not_before"]) or _instant(
            binding["expires_at"]
        ) > _instant(parent["expires_at"]):
            reasons.add("DELEGATION_VALIDITY_EXCEEDS_PARENT")
        seen.add(binding["child_passport_id"])
        parent = {
            "passport_id": binding["child_passport_id"],
            "subject_id": binding["child_subject_id"],
            "maximum_action_level": binding["maximum_action_level"],
            "action_terms": binding["action_terms"],
            "not_before": binding["not_before"],
            "expires_at": binding["expires_at"],
            "depth": parent["depth"] + 1,
        }
        lineage.append(parent)
    acting = lineage[-1]
    depth = len(chain)
    if depth > policy["delegation_max_depth"]:
        reasons.add("DELEGATION_DEPTH_EXCEEDED")

    for record in lineage:
        if at < _instant(record["not_before"]):
            reasons.add("PASSPORT_NOT_YET_VALID")
        if at >= _instant(record["expires_at"]):
            reasons.add("PASSPORT_EXPIRED")

    # Effective action level and its status freshness window.
    action = request["action"]
    term_minimum = profile["action_term_minimum_levels"][action["term"]]
    effective_level = max(action["requested_level"], term_minimum)
    max_age = policy["revocation_max_age_seconds"][str(effective_level)]

    # Revocation is terminal: a listed passport is revoked whatever any
    # suspension entry says, and even when the list is no longer fresh.
    revocation = request["revocation_status"]
    revoked_ids = set(revocation["revoked_passport_ids"])
    revocation_usable = _instant(revocation["issued_at"]) <= at < _instant(revocation["next_update"])
    if not revocation_usable:
        reasons.add("REVOCATION_STATUS_UNKNOWN")
    elif (at - _instant(revocation["issued_at"])).total_seconds() > max_age:
        reasons.add("REVOCATION_STATUS_STALE_FOR_LEVEL")
        revocation_usable = False
    revoked_self = acting["passport_id"] in revoked_ids
    revoked_ancestor = any(record["passport_id"] in revoked_ids for record in lineage[:-1])
    if revoked_self:
        reasons.add("PASSPORT_REVOKED")
    if revoked_ancestor:
        reasons.add("ANCESTOR_REVOKED")

    # Suspension is reinstatable: an entry is active from suspended_at until
    # reinstated_at, after which the same passport may be used again.
    suspensions = request["suspension_list"]
    suspension_usable = True
    if suspensions["list_id"] != suspension_list_id(suspensions):
        reasons.add("SUSPENSION_LIST_ID_MISMATCH")
        suspension_usable = False
    entry_ids = [entry["passport_id"] for entry in suspensions["entries"]]
    if len(entry_ids) != len(set(entry_ids)) or any(
        entry["reinstated_at"] is not None and _instant(entry["reinstated_at"]) <= _instant(entry["suspended_at"])
        for entry in suspensions["entries"]
    ):
        reasons.add("SUSPENSION_ENTRY_INVALID")
        suspension_usable = False
    if suspension_usable:
        if not _instant(suspensions["issued_at"]) <= at < _instant(suspensions["next_update"]):
            reasons.add("SUSPENSION_STATUS_UNKNOWN")
            suspension_usable = False
        elif (at - _instant(suspensions["issued_at"])).total_seconds() > max_age:
            reasons.add("SUSPENSION_STATUS_STALE_FOR_LEVEL")
            suspension_usable = False

    def suspended(passport_id: str) -> bool:
        for entry in suspensions["entries"]:
            if entry["passport_id"] != passport_id or at < _instant(entry["suspended_at"]):
                continue
            if entry["reinstated_at"] is None or at < _instant(entry["reinstated_at"]):
                return True
        return False

    suspended_self = suspension_usable and suspended(acting["passport_id"])
    suspended_ancestor = suspension_usable and any(suspended(r["passport_id"]) for r in lineage[:-1])
    if suspended_self:
        reasons.add("PASSPORT_SUSPENDED")
    if suspended_ancestor:
        reasons.add("ANCESTOR_SUSPENDED")

    if revoked_self or revoked_ancestor:
        state = "REVOKED"
    elif suspended_self or suspended_ancestor:
        state = "SUSPENDED"
    elif not (revocation_usable and suspension_usable):
        state = "UNKNOWN"
    else:
        state = "ACTIVE"

    # Authority of the acting passport.
    ceiling = acting["maximum_action_level"]
    if action["term"] not in acting["action_terms"]:
        reasons.add("ACTION_TERM_NOT_AUTHORIZED")
    if effective_level > ceiling:
        reasons.add("ACTION_LEVEL_EXCEEDS_CEILING")
    if effective_level >= 5 and not profile["level_5_permitted"]:
        reasons.add("LEVEL_5_NOT_PERMITTED")
    if action["term"] == "spawn_agent" and depth + 1 > policy["delegation_max_depth"]:
        reasons.add("SPAWN_WOULD_EXCEED_DEPTH")

    permitted = not reasons and state == "ACTIVE"
    return _result(
        request,
        operating_disposition="PERMITTED" if permitted else "NOT_PERMITTED",
        passport_state=state,
        acting_passport_id=acting["passport_id"],
        delegation_depth=depth,
        effective_level=effective_level,
        authority_ceiling=ceiling,
        status_max_age_seconds=max_age,
        reason_codes=sorted(reasons),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate an Agent Fleet Controls action request.")
    parser.add_argument("request", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        request = load_strict(args.request, require_object=True)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": f"unreadable request: {exc}"}))
        return 1
    result = evaluate(request, args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["operating_disposition"] == "PERMITTED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
