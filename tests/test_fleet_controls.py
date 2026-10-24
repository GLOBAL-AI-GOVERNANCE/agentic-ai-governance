# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools.canonical_json import canonicalize
from tools.fleet_controls import (
    PINNED_DESCRIPTOR_JCS_SHA256,
    PINNED_DOCUMENT_SHA256,
    REASON_CODES,
    binding_id,
    effective_policy,
    evaluate,
    load_profile,
    max_ages_are_non_increasing,
    suspension_list_id,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "conformance/fleet-controls/manifest.json").read_text(encoding="utf-8"))
VECTORS = {Path(v["path"]).stem: v for v in MANIFEST["vectors"]}


def _load(name: str) -> dict:
    return json.loads((ROOT / "examples/fleet-controls" / f"{name}.json").read_text(encoding="utf-8"))


def _rebind(request: dict) -> dict:
    for binding in request["delegation_chain"]:
        binding["binding_id"] = binding_id(binding)
    request["suspension_list"]["list_id"] = suspension_list_id(request["suspension_list"])
    return request


def test_manifest_pins_every_artifact_digest() -> None:
    assert MANIFEST["target_release"] == "v0.1.0-alpha.4"
    assert MANIFEST["independent_verification_established"] is False
    assert MANIFEST["independent_verifier_kit_target"] == "v0.1.0-alpha.2"
    for record in MANIFEST["normative_artifacts"] + MANIFEST["vectors"]:
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], record["path"]
    listed = {Path(v["path"]).name for v in MANIFEST["vectors"]}
    actual = {p.name for p in (ROOT / "examples/fleet-controls").glob("*.json")}
    assert listed == actual


@pytest.mark.parametrize("name", sorted(VECTORS))
def test_vector_reproduces_expected_outcome(name: str) -> None:
    request = _load(name)
    assert request["evaluated_at"] == MANIFEST["evaluation_time"]
    result = evaluate(request)
    expected = VECTORS[name]["expected"]
    for key, value in expected.items():
        assert result[key] == value, (name, key)
    assert result["external_enforcement"] == "NOT_PERFORMED"
    assert result["authority_effect"] == "NONE"


def test_vectors_cover_every_fleet_reason_family() -> None:
    seen = {code for v in VECTORS.values() for code in v["expected"]["reason_codes"]}
    for code in (
        "REVOCATION_STATUS_STALE_FOR_LEVEL",
        "SUSPENSION_STATUS_STALE_FOR_LEVEL",
        "PASSPORT_SUSPENDED",
        "PASSPORT_REVOKED",
        "ANCESTOR_REVOKED",
        "ANCESTOR_SUSPENDED",
        "DELEGATION_DEPTH_EXCEEDED",
        "SPAWN_WOULD_EXCEED_DEPTH",
        "DELEGATION_LEVEL_EXCEEDS_PARENT",
        "DELEGATION_TERMS_EXCEED_PARENT",
        "DELEGATION_VALIDITY_EXCEEDS_PARENT",
        "DELEGATION_PARENT_MISMATCH",
        "DELEGATION_BINDING_ID_MISMATCH",
        "ACTION_TERM_NOT_AUTHORIZED",
        "LEVEL_5_NOT_PERMITTED",
        "POLICY_OVERRIDE_LOOSENS",
    ):
        assert code in seen, code
    assert {v["expected"]["passport_state"] for v in VECTORS.values()} == {"ACTIVE", "SUSPENDED", "REVOKED", "UNKNOWN"}


def test_vector_identifiers_are_reproducible() -> None:
    for name in VECTORS:
        request = _load(name)
        if name != "sub-agent-binding-tampered":
            for binding in request["delegation_chain"]:
                assert binding["binding_id"] == binding_id(binding), name
        assert request["suspension_list"]["list_id"] == suspension_list_id(request["suspension_list"]), name


def test_profile_hash_anchor_binds_document_and_descriptor() -> None:
    profile, errors = load_profile()
    assert errors == []
    md = (ROOT / "profiles/agent-fleet-controls-profile.md").read_bytes()
    assert profile["control_profile"]["hash"] == "sha256:" + hashlib.sha256(md).hexdigest() == PINNED_DOCUMENT_SHA256
    assert "sha256:" + hashlib.sha256(canonicalize(profile)).hexdigest() == PINNED_DESCRIPTOR_JCS_SHA256


def _copy_profile(tmp_path: Path) -> Path:
    for rel in ("schemas", "governance", "profiles"):
        shutil.copytree(ROOT / rel, tmp_path / rel)
    return tmp_path


def test_edited_profile_document_fails_the_anchor(tmp_path: Path) -> None:
    root = _copy_profile(tmp_path)
    md = root / "profiles/agent-fleet-controls-profile.md"
    md.write_text(md.read_text(encoding="utf-8").replace("900 seconds", "7200 seconds"), encoding="utf-8")
    assert load_profile(root)[1]
    assert evaluate(_load("root-network-call-permitted"), root)["reason_codes"] == ["PROFILE_ANCHOR_MISMATCH"]


def test_edited_profile_descriptor_fails_the_anchor(tmp_path: Path) -> None:
    root = _copy_profile(tmp_path)
    path = root / "profiles/agent-fleet-controls-profile.json"
    profile = json.loads(path.read_text(encoding="utf-8"))
    profile["delegation_max_depth"] = 8
    path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    assert any("descriptor hash" in e for e in load_profile(root)[1])


def test_profile_max_ages_are_shorter_for_higher_levels() -> None:
    profile, _ = load_profile()
    ages = profile["revocation_max_age_seconds"]
    assert max_ages_are_non_increasing(ages)
    assert ages["5"] < ages["4"] < ages["3"] < ages["2"] <= ages["1"] <= ages["0"]
    assert profile["action_term_minimum_levels"] == {
        "install_tool": 4,
        "network_call": 4,
        "provision_compute": 4,
        "spawn_agent": 4,
        "spend_funds": 5,
    }
    assert profile["level_5_permitted"] is False


def test_overrides_only_tighten() -> None:
    profile, _ = load_profile()
    policy, reasons = effective_policy(profile, {"revocation_max_age_seconds": {"3": 60, "4": 60, "5": 60}, "delegation_max_depth": 1})
    assert reasons == set()
    assert policy["delegation_max_depth"] == 1 and policy["revocation_max_age_seconds"]["3"] == 60
    _, reasons = effective_policy(profile, {"revocation_max_age_seconds": {"2": 30}})
    assert reasons == {"POLICY_INVALID"}
    _, reasons = effective_policy(profile, {"delegation_max_depth": 4})
    assert reasons == {"POLICY_OVERRIDE_LOOSENS"}


def test_policy_invalid_override_is_not_permitted() -> None:
    request = _load("root-network-call-permitted")
    request["policy_overrides"] = {"revocation_max_age_seconds": {"2": 30}}
    result = evaluate(request)
    assert result["operating_disposition"] == "NOT_PERMITTED"
    assert "POLICY_INVALID" in result["reason_codes"]


def test_depth_mismatch_and_cycle_fail_closed() -> None:
    request = _load("sub-agent-spawn-permitted")
    request["delegation_chain"][1]["delegation_depth"] = 3
    result = evaluate(_rebind(request))
    assert "DELEGATION_DEPTH_MISMATCH" in result["reason_codes"]

    request = _load("sub-agent-spawn-permitted")
    second = request["delegation_chain"][1]
    second["child_passport_id"] = request["root_passport"]["passport_id"]
    result = evaluate(_rebind(request))
    assert "DELEGATION_CYCLE" in result["reason_codes"]
    assert result["operating_disposition"] == "NOT_PERMITTED"


def test_expired_or_future_passport_in_lineage_fails_closed() -> None:
    request = _load("sub-agent-spawn-permitted")
    request["evaluated_at"] = "2026-12-31T12:00:00Z"
    result = evaluate(_rebind(request))
    assert "PASSPORT_EXPIRED" in result["reason_codes"]

    request = _load("sub-agent-spawn-permitted")
    request["delegation_chain"][0]["not_before"] = "2026-10-24T13:00:00Z"
    request["delegation_chain"][1]["not_before"] = "2026-10-24T13:00:00Z"
    result = evaluate(_rebind(request))
    assert "PASSPORT_NOT_YET_VALID" in result["reason_codes"]


def test_suspension_list_integrity_and_entries() -> None:
    request = _load("sub-agent-suspended")
    request["suspension_list"]["entries"] = []
    result = evaluate(request)
    assert "SUSPENSION_LIST_ID_MISMATCH" in result["reason_codes"]
    assert result["passport_state"] == "UNKNOWN"

    request = _load("suspension-reinstated-same-passport")
    entry = request["suspension_list"]["entries"][0]
    entry["reinstated_at"] = entry["suspended_at"]
    result = evaluate(_rebind(request))
    assert "SUSPENSION_ENTRY_INVALID" in result["reason_codes"]

    request = _load("sub-agent-suspended")
    request["suspension_list"]["entries"].append(copy.deepcopy(request["suspension_list"]["entries"][0]))
    result = evaluate(_rebind(request))
    assert "SUSPENSION_ENTRY_INVALID" in result["reason_codes"]

    request = _load("sub-agent-suspended")
    request["suspension_list"]["next_update"] = "2026-10-24T12:00:00Z"
    result = evaluate(_rebind(request))
    assert "SUSPENSION_STATUS_UNKNOWN" in result["reason_codes"]


def test_future_suspension_is_not_yet_active() -> None:
    request = _load("sub-agent-suspended")
    request["suspension_list"]["entries"][0]["suspended_at"] = "2026-10-24T13:00:00Z"
    result = evaluate(_rebind(request))
    assert result["operating_disposition"] == "PERMITTED"
    assert result["passport_state"] == "ACTIVE"


def test_unknown_terms_and_unsupported_profile_fail_closed() -> None:
    request = _load("root-network-call-permitted")
    request["action"]["term"] = "delete_everything"
    assert evaluate(request)["reason_codes"] == ["REQUEST_SCHEMA_INVALID"]
    request = _load("root-network-call-permitted")
    request["profile"]["profile_version"] = "0.1.0-alpha.1"
    assert evaluate(request)["reason_codes"] == ["PROFILE_UNSUPPORTED"]
    assert evaluate(["not", "an", "object"])["reason_codes"] == ["REQUEST_SCHEMA_INVALID"]


def test_requested_level_above_term_minimum_raises_effective_level() -> None:
    request = _load("root-network-call-permitted")
    request["action"]["requested_level"] = 5
    result = evaluate(request)
    assert result["effective_level"] == 5
    assert "LEVEL_5_NOT_PERMITTED" in result["reason_codes"]


def test_reason_codes_follow_declared_order() -> None:
    for name in VECTORS:
        codes = evaluate(_load(name))["reason_codes"]
        assert codes == sorted(codes, key=REASON_CODES.index)


def test_cli_exit_codes() -> None:
    tool = ROOT / "tools/fleet_controls.py"
    ok = subprocess.run([sys.executable, str(tool), str(ROOT / "examples/fleet-controls/root-network-call-permitted.json")], capture_output=True, text=True)
    assert ok.returncode == 0 and json.loads(ok.stdout)["operating_disposition"] == "PERMITTED"
    denied = subprocess.run([sys.executable, str(tool), str(ROOT / "examples/fleet-controls/ancestor-revoked.json")], capture_output=True, text=True)
    assert denied.returncode == 3 and json.loads(denied.stdout)["passport_state"] == "REVOKED"
