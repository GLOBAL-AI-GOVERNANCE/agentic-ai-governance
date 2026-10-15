# SPDX-License-Identifier: Apache-2.0
"""Synthetic signed request sequence using ephemeral keys and native validators.

Reference decisions only. No runtime enforcement.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.canonical_json import canonicalize
from tools.crypto import b64e, jwk_thumbprint_kid
from tools.opa_bridge import evaluate
from tools.strict_json import load_strict
from tools.verify_repository import domain_id

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools/validate_artifact.py"
BUNDLE = ROOT / "examples/bundles/valid-bundle-manifest.json"
GRAPH_PATH = ROOT / "examples/action-authority/readonly-graph.json"
HISTORICAL_KEY = ROOT / "examples/trusted-keys/test-ed25519-key.json"
ISSUER = "global-ai-governance.test-issuer"

T_PERMIT = "2026-09-02T12:00:00Z"
T_STALE = "2026-09-02T13:00:00Z"
T_REVOKE = "2026-09-02T14:00:00Z"
T_EXPIRE = "2026-09-10T00:00:00Z"
T_LIST_STALE = "2026-09-20T00:00:00Z"

POLICY_ID = "global-ai-governance.opa-enforcement-bridge"
POLICY_VERSION = "1.0.0-unreleased"
PROFILE_ID = "global-ai-governance.mcp-governance"
PROFILE_VERSION = "0.1.0-alpha.1"


def _run_cli(*args: object) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        capture_output=True,
        text=True,
    )
    assert "Traceback" not in result.stderr, result.stderr
    assert result.stdout.strip(), result.stderr
    return result, json.loads(result.stdout)


def _write(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


class _Signer:
    def __init__(self) -> None:
        self._private = Ed25519PrivateKey.generate()
        public = self._private.public_key().public_bytes_raw()
        jwk = {
            "alg": "Ed25519",
            "crv": "Ed25519",
            "kty": "OKP",
            "key_ops": ["verify"],
            "use": "sig",
            "x": b64e(public),
        }
        self.kid = jwk_thumbprint_kid(jwk)
        self.key_document = {
            "allowed_algorithms": ["Ed25519"],
            "expires_at": "2027-01-01T00:00:00Z",
            "issuer_id": ISSUER,
            "jwk": jwk,
            "kid": self.kid,
            "not_before": "2026-01-01T00:00:00Z",
            "status": "ACTIVE",
        }

    def write_key(self, path: Path) -> Path:
        return _write(path, self.key_document)

    def sign(self, value: dict, *, kind: str) -> dict:
        document = deepcopy(value)
        document.pop("proof", None)
        if kind == "passport":
            document["passport_id"] = domain_id(
                "global-ai-governance.agent-trust-passport.identifier.v1",
                "passport",
                {key: item for key, item in document.items() if key != "passport_id"},
            )
            typ = "atp+jws"
            cty = "application/agent-trust-passport+json"
        elif kind == "revocation":
            for entry in document["entries"]:
                entry["revocation_id"] = domain_id(
                    "global-ai-governance.agent-trust-passport.revocation-entry.identifier.v1",
                    "entry",
                    {key: item for key, item in entry.items() if key != "revocation_id"},
                )
            document["entries"] = sorted(
                document["entries"],
                key=lambda entry: (entry["passport_id"], entry["revocation_id"]),
            )
            document["list_id"] = domain_id(
                "global-ai-governance.agent-trust-passport.revocation-list.identifier.v1",
                "list",
                {key: item for key, item in document.items() if key != "list_id"},
            )
            typ = "atp-revocation+jws"
            cty = "application/agent-revocation-list+json"
        else:
            raise AssertionError(kind)
        header = {"alg": "Ed25519", "cty": cty, "kid": self.kid, "typ": typ}
        protected = b64e(canonicalize(header))
        payload = b64e(canonicalize(document))
        signature = self._private.sign((protected + "." + payload).encode("ascii"))
        document["proof"] = {"jws": protected + ".." + b64e(signature)}
        return document


def _authority(passport: dict) -> tuple[list[str], list[str], int]:
    graph = load_strict(GRAPH_PATH, require_object=True)
    graph_hash = _sha256(canonicalize(graph))
    assert passport["bindings"]["action_authority_graph"] == graph_hash
    assert graph["agent_id"] == passport["subject"]["agent_id"]
    assert graph["dimensions"]["delegation"] is False
    level = graph["computed_level"]
    assert level == passport["issued_assessment"]["maximum_action_level"]
    actions = sorted(
        node["node_id"] for node in graph["nodes"] if node["node_type"] == "TOOL"
    )
    resources = sorted(
        node["node_id"] for node in graph["nodes"] if node["node_type"] == "MCP_SERVER"
    )
    assert actions and resources
    return actions, resources, level


def _policy(actions: list[str], resources: list[str], *, denied: list[str] | None = None) -> dict:
    return {
        "allowed_actions": actions,
        "allowed_resources": resources,
        "approval_required_actions": [],
        "denied_actions": denied or [],
        "max_validation_age_seconds": 900,
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "required_context": ["purpose"],
    }


def _bridge(
    report: dict,
    passport: dict,
    *,
    evaluation_time: str,
    request: dict,
    policy: dict,
    context: dict,
    request_id: str,
) -> dict:
    artifact = load_strict(Path(report["artifact"]), require_object=True)
    if artifact.get("passport_id") != passport.get("passport_id"):
        raise AssertionError("passport identity does not match the validated artifact")
    actions, resources, level = _authority(passport)
    established = (
        report.get("fully_validated") is True
        and report.get("verification_primary_status") == "VALID"
        and report.get("operating_disposition") == "PERMITTED"
        and report.get("checks", {}).get("revocation") == "PASS"
    )
    primary = report.get("verification_primary_status") or "UNKNOWN"
    disposition = report.get("operating_disposition") or "NOT_PERMITTED"
    if disposition not in {
        "PERMITTED",
        "PERMITTED_WITH_CONDITIONS",
        "RESTRICTED",
        "NOT_PERMITTED",
        "INDETERMINATE",
    }:
        disposition = "NOT_PERMITTED"
    revocation_status = "CURRENT_NOT_REVOKED" if established else "NOT_CURRENT"
    if report.get("checks", {}).get("revocation") == "REVOKED":
        revocation_status = "REVOKED"
    evidence = [
        item
        for item in passport["bindings"]["data_authority_evidence"]
        if isinstance(item, str)
    ]
    evidence.append(passport["issued_assessment"]["assessment_id"])
    return {
        "bridge_contract_version": "1.0.0",
        "context": context,
        "evaluation_time": evaluation_time,
        "policy": policy,
        "request": request,
        "request_id": request_id,
        "validated_result": {
            "allowed_actions": actions,
            "allowed_resources": resources,
            "evidence_refs": sorted(set(evidence)),
            "maximum_action_level": level,
            "operating_disposition": "PERMITTED" if established else disposition,
            "passport_id": passport["passport_id"],
            "primary_status": "VALID" if established else primary,
            "revocation_status": revocation_status,
            "valid_until": passport["validity"]["expires_at"],
            "validation_state": "ESTABLISHED" if established else "NOT_ESTABLISHED",
            "verification_result_ref": _sha256(canonicalize(report)),
            "verified_at": report["evaluated_at"],
        },
    }


def _validate(
    passport: Path,
    key: Path,
    revocation: Path,
    at_time: str,
    *,
    state: Path | None = None,
    initialize: bool = False,
    extra: list[object] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict]:
    args: list[object] = [
        "--kind", "passport",
        "--trusted-key", key,
        "--revocation-list", revocation,
        "--bundle-manifest", BUNDLE,
        "--bundle-root", ROOT,
        "--at-time", at_time,
    ]
    if state is not None:
        args.extend(["--revocation-state", state])
    if initialize:
        args.append("--initialize-revocation-state")
    if extra:
        args.extend(extra)
    args.append(passport)
    return _run_cli(*args)


def test_signed_request_sequence_binds_authority_expiry_and_revocation(tmp_path: Path) -> None:
    historical = (ROOT / "examples/passports/signed-unrevoked.json").read_bytes()
    signer = _Signer()
    key_path = signer.write_key(tmp_path / "verification-key.json")
    template = load_strict(ROOT / "examples/passports/signed-unrevoked.json", require_object=True)
    template.pop("proof", None)

    original_body = deepcopy(template)
    original_body["validity"] = {
        "expires_at": T_EXPIRE,
        "not_before": "2026-07-17T20:00:00Z",
    }
    replacement_body = deepcopy(template)
    replacement_body["subject"] = deepcopy(template["subject"])
    replacement_body["subject"]["display_name"] = "Synthetic Replacement Research Agent"
    replacement_body["validity"] = {
        "expires_at": "2026-11-15T00:00:00Z",
        "not_before": "2026-07-17T20:00:00Z",
    }
    original = signer.sign(original_body, kind="passport")
    replacement = signer.sign(replacement_body, kind="passport")
    assert original["passport_id"] != replacement["passport_id"]
    original_path = _write(tmp_path / "original-passport.json", original)
    replacement_path = _write(tmp_path / "replacement-passport.json", replacement)

    list_template = load_strict(
        ROOT / "examples/revocation/valid-revocation-list.json", require_object=True
    )
    list_template.pop("proof", None)
    initial_body = deepcopy(list_template)
    initial_body.update(
        {
            "entries": [],
            "issued_at": "2026-09-01T00:00:00Z",
            "next_update": T_LIST_STALE,
            "previous_list_hash": None,
            "sequence_number": 1,
        }
    )
    initial = signer.sign(initial_body, kind="revocation")
    initial_path = _write(tmp_path / "revocation-1.json", initial)
    entry = {
        "authority": ISSUER,
        "framework": "global-ai-governance.agentic-ai-governance",
        "passport_id": original["passport_id"],
        "reason": "Synthetic replacement of a bounded passport.",
        "reason_code": "PASSPORT_REPLACED",
        "revoked_at": T_REVOKE,
        "superseding_passport_id": replacement["passport_id"],
    }
    successor_body = deepcopy(list_template)
    successor_body.update(
        {
            "entries": [entry],
            "issued_at": T_REVOKE,
            "next_update": T_LIST_STALE,
            "previous_list_hash": initial["list_id"],
            "sequence_number": 2,
        }
    )
    successor = signer.sign(successor_body, kind="revocation")
    successor_path = _write(tmp_path / "revocation-2.json", successor)

    actions, resources, level = _authority(original)
    permit_policy = _policy(actions, resources)
    deny_policy = _policy(actions, resources, denied=actions)
    context = {"purpose": "synthetic-public-reference-read"}
    permitted_request = {
        "action": actions[0],
        "action_level": 1,
        "resource": resources[0],
    }
    assert permitted_request["action_level"] <= level

    result, report = _validate(original_path, key_path, initial_path, T_PERMIT)
    assert result.returncode == 0
    assert report["fully_validated"] is True
    assert report["verification_primary_status"] == "VALID"
    assert report["operating_disposition"] == "PERMITTED"
    assert report["checks"]["signature"] == "PASS"
    assert report["checks"]["revocation"] == "PASS"
    decision = evaluate(
        _bridge(
            report, original,
            evaluation_time=T_PERMIT,
            request=permitted_request,
            policy=permit_policy,
            context=context,
            request_id="request.synthetic.permit",
        )
    )
    assert decision["operating_disposition"] == "PERMITTED"
    assert decision["reason_codes"] == ["POLICY_AND_AUTHORITY_MATCH"]
    assert decision["external_enforcement"] == "NOT_PERFORMED"

    state = tmp_path / "revocation-state.json"
    result, report = _validate(
        original_path, key_path, initial_path, T_PERMIT, state=state, initialize=True
    )
    assert result.returncode == 0
    trusted = load_strict(state, require_object=True)
    assert trusted["sequence_number"] == 1
    assert original["passport_id"] not in trusted["revoked_passport_ids"]
    state_after_permit = state.read_bytes()

    denied = evaluate(
        _bridge(
            report, original,
            evaluation_time=T_PERMIT,
            request=permitted_request,
            policy=deny_policy,
            context=context,
            request_id="request.synthetic.policy-deny",
        )
    )
    assert denied["operating_disposition"] == "NOT_PERMITTED"
    assert "POLICY_DENIED" in denied["reason_codes"]
    assert state.read_bytes() == state_after_permit

    negatives = {
        "elevated-action": {**permitted_request, "action_level": 5},
        "wrong-resource": {**permitted_request, "resource": "resource.synthetic.unbound"},
        "unauthorized-action": {**permitted_request, "action": "delegate:authority"},
    }
    expected_reasons = {
        "elevated-action": "ACTION_LEVEL_EXCEEDS_AUTHORITY",
        "wrong-resource": "RESOURCE_OUTSIDE_AUTHORITY",
        "unauthorized-action": "ACTION_OUTSIDE_AUTHORITY",
    }
    for name, request in negatives.items():
        outcome = evaluate(
            _bridge(
                report, original,
                evaluation_time=T_PERMIT,
                request=request,
                policy=permit_policy,
                context=context,
                request_id=f"request.synthetic.{name}",
            )
        )
        assert outcome["operating_disposition"] == "NOT_PERMITTED", name
        assert expected_reasons[name] in outcome["reason_codes"], outcome["reason_codes"]
        assert outcome["external_enforcement"] == "NOT_PERFORMED"
    missing_context = evaluate(
        _bridge(
            report, original,
            evaluation_time=T_PERMIT,
            request=permitted_request,
            policy=permit_policy,
            context={},
            request_id="request.synthetic.missing-context",
        )
    )
    assert missing_context["operating_disposition"] == "NOT_PERMITTED"
    assert "REQUIRED_CONTEXT_MISSING" in missing_context["reason_codes"]
    assert state.read_bytes() == state_after_permit

    stale = evaluate(
        _bridge(
            report, original,
            evaluation_time=T_STALE,
            request=permitted_request,
            policy=permit_policy,
            context=context,
            request_id="request.synthetic.stale",
        )
    )
    assert stale["operating_disposition"] == "NOT_PERMITTED"
    assert "VALIDATION_STALE" in stale["reason_codes"]
    fresh_later, later_report = _validate(original_path, key_path, initial_path, T_STALE)
    assert fresh_later.returncode == 0
    assert later_report["verification_primary_status"] == "VALID"

    expired, expired_report = _validate(
        original_path, key_path, initial_path, T_EXPIRE
    )
    assert expired.returncode != 0
    assert expired_report["verification_primary_status"] == "EXPIRED"
    assert expired_report["operating_disposition"] == "NOT_PERMITTED"
    assert expired_report["checks"]["revocation"] == "NOT_RUN"
    expired_decision = evaluate(
        _bridge(
            expired_report, original,
            evaluation_time=T_EXPIRE,
            request=permitted_request,
            policy=permit_policy,
            context=context,
            request_id="request.synthetic.expired",
        )
    )
    assert expired_decision["operating_disposition"] == "NOT_PERMITTED"
    assert "CANONICAL_VALIDATION_NOT_VALID" in expired_decision["reason_codes"]
    assert "VALIDATION_NOT_ESTABLISHED" in expired_decision["reason_codes"]

    revoked, revoked_report = _validate(
        original_path, key_path, successor_path, T_REVOKE, state=state
    )
    assert revoked.returncode != 0
    assert revoked_report["verification_primary_status"] == "REVOKED"
    assert revoked_report["operating_disposition"] == "NOT_PERMITTED"
    assert original["passport_id"] in load_strict(state, require_object=True)["revoked_passport_ids"]
    revoked_decision = evaluate(
        _bridge(
            revoked_report, original,
            evaluation_time=T_REVOKE,
            request=permitted_request,
            policy=permit_policy,
            context=context,
            request_id="request.synthetic.revoked",
        )
    )
    assert revoked_decision["operating_disposition"] == "NOT_PERMITTED"
    assert "REVOCATION_NOT_CURRENT" in revoked_decision["reason_codes"]
    persisted = state.read_bytes()

    conflict_body = deepcopy(successor_body)
    conflict_body["next_update"] = "2026-09-20T00:00:01Z"
    conflict = signer.sign(conflict_body, kind="revocation")
    conflict_path = _write(tmp_path / "revocation-conflict.json", conflict)
    rollback, rollback_report = _validate(
        replacement_path, key_path, initial_path, T_REVOKE, state=state
    )
    conflict_result, conflict_report = _validate(
        replacement_path, key_path, conflict_path, T_REVOKE, state=state
    )
    assert rollback.returncode != 0
    assert conflict_result.returncode != 0
    assert rollback_report["verification_primary_status"] == "REVOCATION_STATUS_UNKNOWN"
    assert conflict_report["verification_primary_status"] == "REVOCATION_STATUS_UNKNOWN"
    assert state.read_bytes() == persisted

    stale_list, stale_list_report = _validate(
        replacement_path, key_path, successor_path, T_LIST_STALE
    )
    assert stale_list.returncode != 0
    assert any(error["code"] == "REVOCATION_LIST_EXPIRED" for error in stale_list_report["errors"])
    assert stale_list_report["operating_disposition"] == "NOT_PERMITTED"

    replaced, replaced_report = _validate(
        replacement_path, key_path, successor_path, T_REVOKE, state=state
    )
    assert replaced.returncode == 0
    assert replaced_report["fully_validated"] is True
    assert replaced_report["verification_primary_status"] == "VALID"
    replacement_decision = evaluate(
        _bridge(
            replaced_report, replacement,
            evaluation_time=T_REVOKE,
            request=permitted_request,
            policy=permit_policy,
            context=context,
            request_id="request.synthetic.replacement",
        )
    )
    assert replacement_decision["operating_disposition"] == "PERMITTED"
    assert replacement_decision["external_enforcement"] == "NOT_PERFORMED"
    still_revoked = load_strict(state, require_object=True)
    assert original["passport_id"] in still_revoked["revoked_passport_ids"]
    assert replacement["passport_id"] not in still_revoked["revoked_passport_ids"]

    try:
        _bridge(
            replaced_report, original,
            evaluation_time=T_REVOKE,
            request=permitted_request,
            policy=permit_policy,
            context=context,
            request_id="request.synthetic.restore",
        )
    except AssertionError:
        pass
    else:
        raise AssertionError("copied validation was accepted for the revoked passport")
    again, again_report = _validate(
        original_path, key_path, successor_path, T_REVOKE, state=state
    )
    assert again.returncode != 0
    assert again_report["verification_primary_status"] == "REVOKED"

    tampered = deepcopy(original)
    tampered["proof"]["jws"] = tampered["proof"]["jws"][:-1] + (
        "A" if tampered["proof"]["jws"][-1] != "A" else "B"
    )
    tampered_path = _write(tmp_path / "tampered-passport.json", tampered)
    bad_sig, bad_sig_report = _validate(tampered_path, key_path, initial_path, T_PERMIT)
    assert bad_sig.returncode != 0
    assert bad_sig_report["checks"]["signature"] == "FAIL"

    untrusted, untrusted_report = _validate(
        original_path, HISTORICAL_KEY, initial_path, T_PERMIT
    )
    assert untrusted.returncode != 0
    assert untrusted_report["checks"]["signature"] == "FAIL"

    unbound, unbound_report = _run_cli(
        "--kind", "passport",
        "--trusted-key", key_path,
        "--revocation-list", initial_path,
        "--at-time", T_PERMIT,
        original_path,
    )
    assert unbound.returncode != 0
    assert unbound_report["verification_primary_status"] == "BOUND_INPUTS_UNAVAILABLE"

    unsupported = evaluate(
        _bridge(
            report, original,
            evaluation_time=T_PERMIT,
            request=permitted_request,
            policy={**permit_policy, "profile_version": "9.9.9"},
            context=context,
            request_id="request.synthetic.unsupported-profile",
        )
    )
    assert unsupported["operating_disposition"] == "NOT_PERMITTED"
    assert "PROFILE_UNSUPPORTED" in unsupported["reason_codes"]

    forged = _bridge(
        report, original,
        evaluation_time=T_PERMIT,
        request=permitted_request,
        policy=permit_policy,
        context=context,
        request_id="request.synthetic.enforcement-claim",
    )
    forged["runtime_enforcement"] = "PERFORMED"
    claimed = evaluate(forged)
    assert claimed["operating_disposition"] == "NOT_PERMITTED"
    assert claimed["external_enforcement"] == "NOT_PERFORMED"
    assert "RAW_DECLARATION_REJECTED" in claimed["reason_codes"] or "BRIDGE_INPUT_INVALID" in claimed["reason_codes"]

    assert (ROOT / "examples/passports/signed-unrevoked.json").read_bytes() == historical
