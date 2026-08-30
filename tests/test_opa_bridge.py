# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.opa_bridge import evaluate


ROOT = Path(__file__).resolve().parents[1]
PERMITTED = ROOT / "examples/opa/permitted-read.json"
POLICY_DENIED = ROOT / "examples/opa/policy-denied-read.json"


def fixture() -> dict:
    return json.loads(PERMITTED.read_text(encoding="utf-8"))


def test_valid_authorized_request_is_permitted_and_reconstructable() -> None:
    document = fixture()
    first = evaluate(document)
    second = evaluate(copy.deepcopy(document))
    assert first == second
    assert first["operating_disposition"] == "PERMITTED"
    assert first["reason_codes"] == ["POLICY_AND_AUTHORITY_MATCH"]
    assert first["external_enforcement"] == "NOT_PERFORMED"
    assert first["request_id"] == document["request_id"]
    assert first["evaluated_at"] == document["evaluation_time"]
    assert first["evidence_refs"] == sorted(first["evidence_refs"])


def test_policy_denial_is_not_passport_revocation() -> None:
    result = evaluate(json.loads(POLICY_DENIED.read_text(encoding="utf-8")))
    assert result["operating_disposition"] == "NOT_PERMITTED"
    assert result["reason_codes"] == ["POLICY_DENIED"]
    assert "REVOCATION_NOT_CURRENT" not in result["reason_codes"]


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (
            lambda value: value["validated_result"].update(
                primary_status="EXPIRED", valid_until="2026-08-30T12:05:00Z"
            ),
            "VALIDATION_OUTSIDE_VALIDITY",
        ),
        (
            lambda value: value["validated_result"].update(
                primary_status="REVOKED", revocation_status="REVOKED"
            ),
            "REVOCATION_NOT_CURRENT",
        ),
        (
            lambda value: value["validated_result"].update(
                primary_status="REVOCATION_STATUS_UNKNOWN",
                revocation_status="UNKNOWN",
            ),
            "REVOCATION_NOT_CURRENT",
        ),
        (
            lambda value: value["validated_result"].update(
                validation_state="INCOMPLETE"
            ),
            "VALIDATION_NOT_ESTABLISHED",
        ),
        (
            lambda value: value["validated_result"].update(evidence_refs=[]),
            "VALIDATED_RESULT_INVALID",
        ),
        (
            lambda value: value["validated_result"].update(
                verified_at="2026-08-30T11:00:00Z"
            ),
            "VALIDATION_STALE",
        ),
        (
            lambda value: value["request"].update(action_level=2),
            "ACTION_LEVEL_EXCEEDS_AUTHORITY",
        ),
        (
            lambda value: value["request"].update(
                resource="resource.synthetic.outside-authority"
            ),
            "RESOURCE_OUTSIDE_AUTHORITY",
        ),
        (
            lambda value: value["policy"].update(
                policy_version="2.0.0-unsupported"
            ),
            "POLICY_UNSUPPORTED",
        ),
        (
            lambda value: value["policy"].update(
                profile_version="9.9.9-unsupported"
            ),
            "PROFILE_UNSUPPORTED",
        ),
        (lambda value: value.update(context=[]), "CONTEXT_INVALID"),
        (lambda value: value.update(context={}), "REQUIRED_CONTEXT_MISSING"),
        (
            lambda value: value["validated_result"].update(
                operating_disposition="UNKNOWN_DECISION"
            ),
            "CANONICAL_DISPOSITION_UNSUPPORTED",
        ),
    ],
)
def test_adversarial_inputs_fail_safe(mutation, reason: str) -> None:
    document = fixture()
    mutation(document)
    result = evaluate(document)
    assert result["operating_disposition"] == "NOT_PERMITTED"
    assert reason in result["reason_codes"]
    assert result["external_enforcement"] == "NOT_PERFORMED"


def test_policy_cannot_expand_validated_authority() -> None:
    document = fixture()
    action = "publish:external"
    document["request"].update(action=action, action_level=1)
    document["policy"]["allowed_actions"].append(action)
    result = evaluate(document)
    assert result["operating_disposition"] == "NOT_PERMITTED"
    assert "ACTION_OUTSIDE_AUTHORITY" in result["reason_codes"]


def test_raw_unvalidated_passport_attempt_is_rejected() -> None:
    document = fixture()
    document["raw_passport"] = {"declared_valid": True}
    result = evaluate(document)
    assert result["operating_disposition"] == "NOT_PERMITTED"
    assert result["reason_codes"] == ["RAW_DECLARATION_REJECTED"]


def test_approval_requirement_uses_existing_conditional_disposition() -> None:
    document = fixture()
    document["policy"]["approval_required_actions"] = [
        document["request"]["action"]
    ]
    result = evaluate(document)
    assert result["operating_disposition"] == "PERMITTED_WITH_CONDITIONS"
    assert result["reason_codes"] == ["POLICY_APPROVAL_REQUIRED"]


def test_cli_is_deterministic_and_fail_safe(tmp_path: Path) -> None:
    output = []
    for _ in range(2):
        run = subprocess.run(
            [sys.executable, "tools/opa_bridge.py", str(PERMITTED)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert run.returncode == 0, run.stderr
        output.append(run.stdout)
    assert output[0] == output[1]

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    blocked = subprocess.run(
        [sys.executable, "tools/opa_bridge.py", str(malformed)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode == 1
    assert json.loads(blocked.stdout)["operating_disposition"] == "NOT_PERMITTED"
