# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.agent_incident_readiness import verify_trace


ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "examples/agent-incident-readiness/synthetic-lifecycle.json"
KEY = ROOT / "examples/trusted-keys/test-ed25519-key.json"
REVOCATION = ROOT / "examples/revocation/valid-revocation-list.json"
BUNDLE = ROOT / "examples/bundles/valid-bundle-manifest.json"


def fixture() -> dict:
    return json.loads(TRACE.read_text(encoding="utf-8"))


def test_complete_synthetic_lifecycle_is_deterministic() -> None:
    trace = fixture()
    first = verify_trace(trace)
    second = verify_trace(copy.deepcopy(trace))
    assert first == second
    assert first["status"] == "VERIFIED"
    assert first["states"] == [
        "AUTHORIZED", "POLICY_DENIED", "REVOKED", "ROLLBACK_REJECTED",
        "NEW_PASSPORT_REAUTHORIZED",
    ]
    assert first["revoked_passport_remains_revoked"] is True
    assert first["revoked_passport_id"] != first["replacement_passport_id"]
    assert first["external_enforcement"] == "NOT_PERFORMED"


def test_policy_denial_is_not_revocation() -> None:
    trace = fixture()
    result = verify_trace(trace)
    assert result["status"] == "VERIFIED"
    denied = trace["events"][1]["bridge_input"]["validated_result"]
    assert denied["revocation_status"] == "CURRENT_NOT_REVOKED"
    assert trace["passports"]["revoked"]["passport_id"] in trace["revocation_continuity"]["revoked_passport_ids"]


@pytest.mark.parametrize(
    ("passport_key", "expected_status", "expected_exit"),
    [("revoked", "REVOKED", 1), ("replacement", "VALID", 0)],
)
def test_trace_passports_use_canonical_signature_binding_and_revocation_validation(
    passport_key: str, expected_status: str, expected_exit: int,
) -> None:
    trace = fixture()
    passport = trace["passports"][passport_key]
    run = subprocess.run(
        [
            sys.executable, "tools/validate_artifact.py", "--kind", "passport",
            "--trusted-key", str(KEY), "--revocation-list", str(REVOCATION),
            "--bundle-manifest", str(BUNDLE), "--bundle-root", str(ROOT),
            "--at-time", "2026-07-18T12:00:00Z", passport["source_artifact"],
        ],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    report = json.loads(run.stdout)
    assert run.returncode == expected_exit, run.stderr
    assert report["verification_primary_status"] == expected_status
    artifact = json.loads((ROOT / passport["source_artifact"]).read_text(encoding="utf-8"))
    assert artifact["passport_id"] == passport["passport_id"]


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (lambda v: v["events"][1]["bridge_input"]["validated_result"].update(primary_status="REVOKED", revocation_status="REVOKED"), "POLICY_DENIAL_INVALID"),
        (lambda v: v["events"][2]["bridge_input"]["validated_result"].update(primary_status="VALID", operating_disposition="PERMITTED", revocation_status="CURRENT_NOT_REVOKED"), "REVOKED_USE_NOT_REJECTED"),
        (lambda v: v["revocation_continuity"].update(rollback_attempt_sequence=2), "ROLLBACK_NOT_REJECTED"),
        (lambda v: v["revocation_continuity"].update(same_sequence_conflict_result="ACCEPTED"), "REVOCATION_SEQUENCE_CONFLICT"),
        (lambda v: v["revocation_continuity"].update(current_evidence="UNKNOWN"), "REVOCATION_EVIDENCE_UNKNOWN"),
        (lambda v: v["human_authority"].update(attribution_verified=False), "APPROVAL_UNATTRIBUTED"),
        (lambda v: v["events"][0].update(peer_delegation={"approved": True}), "MALFORMED_LIFECYCLE_EVIDENCE"),
        (lambda v: v["events"][0]["bridge_input"]["request"].update(action="publish:external"), "AUTHORIZED_REQUEST_REJECTED"),
        (lambda v: v["events"][0]["bridge_input"]["request"].update(resource="resource.synthetic.outside"), "AUTHORIZED_REQUEST_REJECTED"),
        (lambda v: v["events"][0]["bridge_input"]["validated_result"].update(verified_at="2026-08-30T11:00:00Z"), "AUTHORIZED_REQUEST_REJECTED"),
        (lambda v: v["events"][0].pop("technical_evidence"), "MALFORMED_LIFECYCLE_EVIDENCE"),
        (lambda v: v["revocation_continuity"].update(revoked_passport_ids=[]), "REVOKED_PASSPORT_RESTORED"),
        (lambda v: v["passports"]["replacement"].update(passport_id=v["passports"]["revoked"]["passport_id"]), "NEW_PASSPORT_REQUIRED"),
        (lambda v: v["passports"]["replacement"].update(signature="INVALID"), "PASSPORT_VALIDATION_INVALID"),
        (lambda v: v["passports"]["replacement"].update(binding="INVALID"), "PASSPORT_VALIDATION_INVALID"),
        (lambda v: v["passports"]["replacement"].update(trust="UNKNOWN"), "PASSPORT_VALIDATION_INVALID"),
        (lambda v: v["passports"]["replacement"].update(authority_actions=[]), "ACTION_OUTSIDE_NEW_PASSPORT_AUTHORITY"),
        (lambda v: v.update(external_enforcement="PERFORMED"), "EXTERNAL_ENFORCEMENT_CLAIM_UNSUPPORTED"),
        (lambda v: v.update(runtime_containment="ESTABLISHED"), "MALFORMED_LIFECYCLE_EVIDENCE"),
        (lambda v: v.update(production_iam="ESTABLISHED"), "MALFORMED_LIFECYCLE_EVIDENCE"),
    ],
)
def test_adversarial_trace_fails_closed(mutation, reason: str) -> None:
    trace = fixture()
    mutation(trace)
    result = verify_trace(trace)
    assert result["status"] == "NOT_VERIFIED"
    assert result["reason_codes"] == [reason]
    assert result["external_enforcement"] == "NOT_PERFORMED"


def test_cli_is_deterministic_and_malformed_input_fails_closed(tmp_path: Path) -> None:
    runs = [
        subprocess.run(
            [sys.executable, "tools/agent_incident_readiness.py", str(TRACE)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        for _ in range(2)
    ]
    assert all(run.returncode == 0 for run in runs)
    assert runs[0].stdout == runs[1].stdout

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, "tools/agent_incident_readiness.py", str(malformed)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert rejected.returncode == 1
    assert json.loads(rejected.stdout)["reason_codes"] == ["MALFORMED_LIFECYCLE_EVIDENCE"]
