# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pathlib import Path

from tools.canonical_json import canonicalize
from tools.crypto import b64e, jwk_thumbprint_kid, trusted_key_errors
from tools.semantic_rules import parse_time
from tools.strict_json import StrictJSONError, load_strict
from tools.verify_repository import domain_id

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools/validate_artifact.py"
AT_TIME = "2026-07-18T12:00:00Z"
AT = parse_time(AT_TIME)
KEY = ROOT / "examples/trusted-keys/test-ed25519-key.json"
REVOCATION = ROOT / "examples/revocation/valid-revocation-list.json"
SIGNED = ROOT / "examples/passports/signed-unrevoked.json"
BUNDLE_MANIFEST = ROOT / "examples/bundles/valid-bundle-manifest.json"
BUNDLE_ARGS = ("--bundle-manifest", BUNDLE_MANIFEST, "--bundle-root", ROOT)


def run_cli(*args: object) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        capture_output=True,
        text=True,
    )
    assert "Traceback" not in result.stderr
    assert result.stdout.strip(), result.stderr
    return result, json.loads(result.stdout)


def test_full_signed_passport_validation_passes() -> None:
    result, report = run_cli(
        "--kind", "passport", "--trusted-key", KEY,
        "--revocation-list", REVOCATION, *BUNDLE_ARGS, "--at-time", AT_TIME, SIGNED,
    )
    assert result.returncode == 0
    assert report["fully_validated"] is True
    assert report["valid"] is True
    assert report["issued_assessment_result"] == "APPROVED"
    assert report["verification_primary_status"] == "VALID"
    assert report["operating_disposition"] == "PERMITTED"
    assert "decision" not in report
    assert report["checks"] == {
        "parsing": "PASS", "version": "PASS", "schema": "PASS",
        "semantics": "PASS", "identifier": "PASS",
        "critical_extensions": "PASS", "signature": "PASS",
        "signing_key_trust": "PASS", "bindings": "PASS",
        "validity": "PASS", "revocation": "PASS",
    }


def test_unsigned_passport_is_structural_but_indeterminate() -> None:
    result, report = run_cli(
        "--kind", "passport", *BUNDLE_ARGS, "--at-time", AT_TIME,
        ROOT / "examples/passports/unsigned-valid.json",
    )
    assert result.returncode != 0
    assert report["structurally_valid"] is True
    assert report["fully_validated"] is False
    assert report["valid"] is False
    assert report["issued_assessment_result"] == "APPROVED"
    assert report["verification_primary_status"] == "VALID"
    assert report["operating_disposition"] == "INDETERMINATE"
    assert "decision" not in report


def test_signed_passport_requires_trusted_key_and_revocation_state() -> None:
    result, report = run_cli("--kind", "passport", "--at-time", AT_TIME, SIGNED)
    assert result.returncode != 0
    assert report["checks"]["signature"] == "NOT_RUN"
    assert any(error["code"] == "TRUSTED_KEY_REQUIRED" for error in report["errors"])

    result, report = run_cli(
        "--kind", "passport", "--trusted-key", KEY, *BUNDLE_ARGS, "--at-time", AT_TIME, SIGNED
    )
    assert result.returncode != 0
    assert report["checks"]["signature"] == "PASS"
    assert report["checks"]["revocation"] == "NOT_RUN"
    assert report["verification_primary_status"] == "REVOCATION_STATUS_UNKNOWN"
    assert report["operating_disposition"] == "NOT_PERMITTED"
    assert "decision" not in report


def test_revoked_passport_is_rejected() -> None:
    result, report = run_cli(
        "--kind", "passport", "--trusted-key", KEY,
        "--revocation-list", REVOCATION, *BUNDLE_ARGS, "--at-time", AT_TIME,
        ROOT / "examples/passports/signed-revoked.json",
    )
    assert result.returncode != 0
    assert report["verification_primary_status"] == "REVOKED"
    assert report["operating_disposition"] == "NOT_PERMITTED"
    assert "decision" not in report
    assert report["checks"]["revocation"] == "REVOKED"


def test_wrong_identifier_and_altered_signature_are_rejected() -> None:
    result, report = run_cli(
        "--kind", "passport", "--at-time", AT_TIME,
        ROOT / "tests/cli-negative/passport-wrong-id.json",
    )
    assert result.returncode != 0
    assert report["checks"]["identifier"] == "FAIL"

    result, report = run_cli(
        "--kind", "passport", "--trusted-key", KEY,
        "--revocation-list", REVOCATION, *BUNDLE_ARGS, "--at-time", AT_TIME,
        ROOT / "tests/cli-negative/passport-altered-signature.json",
    )
    assert result.returncode != 0
    assert report["checks"]["signature"] == "FAIL"


def test_malformed_input_returns_structured_json_without_traceback() -> None:
    for fixture in ["malformed.json", "duplicate-key.json"]:
        result, report = run_cli(
            "--kind", "passport", "--at-time", AT_TIME,
            ROOT / "tests/cli-negative" / fixture,
        )
        assert result.returncode != 0
        assert report["checks"]["parsing"] == "FAIL"
        assert report["checks"]["schema"] == "NOT_RUN"
        assert report["errors"][0]["code"] == "INVALID_JSON"


def test_strict_loader_rejects_all_input_profile_violations() -> None:
    for fixture in [
        "duplicate-key.json", "nonfinite.json", "unsafe-integer.json",
        "top-level-list.json", "invalid-utf8.bin", "malformed.json",
    ]:
        try:
            load_strict(ROOT / "tests/cli-negative" / fixture, require_object=True)
        except StrictJSONError:
            pass
        else:
            raise AssertionError(f"strict loader accepted {fixture}")


def test_schema_failure_stops_dependent_stages(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"schema_version":"0.1.0-alpha.1"}\n', encoding="utf-8")
    result, report = run_cli("--kind", "passport", "--at-time", AT_TIME, invalid)
    assert result.returncode != 0
    assert report["checks"]["schema"] == "FAIL"
    assert report["checks"]["semantics"] == "NOT_RUN"
    assert report["checks"]["identifier"] == "NOT_RUN"


def test_all_unusable_key_states_and_bindings_fail_reference_policy() -> None:
    issuer = "global-ai-governance.test-issuer"
    for name in [
        "revoked", "compromised", "not-yet-valid", "expired", "retired",
        "wrong-issuer", "wrong-kid", "wrong-purpose",
    ]:
        key = load_strict(ROOT / f"tests/cli-negative/keys/{name}.json", require_object=True)
        assert trusted_key_errors(key, expected_issuer=issuer, at_time=AT), name

    result, report = run_cli(
        "--kind", "passport",
        "--trusted-key", ROOT / "tests/cli-negative/keys/revoked.json",
        "--revocation-list", REVOCATION, *BUNDLE_ARGS, "--at-time", AT_TIME, SIGNED,
    )
    assert result.returncode != 0
    assert report["checks"]["signature"] == "PASS"
    assert report["checks"]["signing_key_trust"] == "FAIL"


def test_invalid_evaluation_time_is_structured() -> None:
    result, report = run_cli(
        "--kind", "passport", "--at-time", "2026-02-30T00:00:00Z", SIGNED
    )
    assert result.returncode != 0
    assert report["checks"]["parsing"] == "FAIL"
    assert report["errors"][0]["code"] == "INVALID_EVALUATION_TIME"



def test_three_state_layers_remain_distinct_across_passport_branches() -> None:
    _, signed = run_cli(
        "--kind", "passport", "--trusted-key", KEY,
        "--revocation-list", REVOCATION, *BUNDLE_ARGS, "--at-time", AT_TIME, SIGNED,
    )
    _, unsigned = run_cli(
        "--kind", "passport", *BUNDLE_ARGS, "--at-time", AT_TIME,
        ROOT / "examples/passports/unsigned-valid.json",
    )
    _, revoked = run_cli(
        "--kind", "passport", "--trusted-key", KEY,
        "--revocation-list", REVOCATION, *BUNDLE_ARGS, "--at-time", AT_TIME,
        ROOT / "examples/passports/signed-revoked.json",
    )

    assert signed["issued_assessment_result"] == unsigned["issued_assessment_result"] == revoked["issued_assessment_result"] == "APPROVED"
    assert signed["verification_primary_status"] == unsigned["verification_primary_status"] == "VALID"
    assert revoked["verification_primary_status"] == "REVOKED"
    assert signed["operating_disposition"] == "PERMITTED"
    assert unsigned["operating_disposition"] == "INDETERMINATE"
    assert revoked["operating_disposition"] == "NOT_PERMITTED"
    assert all("decision" not in report for report in (signed, unsigned, revoked))



def test_nontrust_artifact_validation_remains_simple() -> None:
    result, report = run_cli(
        "--kind", "bundle", ROOT / "examples/bundles/valid-bundle-manifest.json"
    )
    assert result.returncode == 0
    assert report["artifact_validation_status"] == "PASS"
    assert report["issued_assessment_result"] is None
    assert report["verification_primary_status"] is None
    assert report["operating_disposition"] is None
    assert "decision" not in report
    assert report["checks"]["identifier"] == "PASS"


TEST_SEED = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")


def _write_json(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def _sign_document(value: dict, *, kind: str) -> dict:
    document = deepcopy(value)
    document.pop("proof", None)
    if kind == "passport":
        document["passport_id"] = domain_id(
            "global-ai-governance.agent-trust-passport.identifier.v1",
            "passport",
            {k: v for k, v in document.items() if k != "passport_id"},
        )
        typ = "atp+jws"
        cty = "application/agent-trust-passport+json"
    elif kind == "revocation":
        for entry in document["entries"]:
            entry["revocation_id"] = domain_id(
                "global-ai-governance.agent-trust-passport.revocation-entry.identifier.v1",
                "entry",
                {k: v for k, v in entry.items() if k != "revocation_id"},
            )
        document["list_id"] = domain_id(
            "global-ai-governance.agent-trust-passport.revocation-list.identifier.v1",
            "list",
            {k: v for k, v in document.items() if k != "list_id"},
        )
        typ = "atp-revocation+jws"
        cty = "application/agent-revocation-list+json"
    else:
        raise AssertionError(kind)
    key = load_strict(KEY, require_object=True)
    header = {"alg": "Ed25519", "cty": cty, "kid": key["kid"], "typ": typ}
    protected = b64e(canonicalize(header))
    payload = b64e(canonicalize(document))
    signature = Ed25519PrivateKey.from_private_bytes(TEST_SEED).sign(
        (protected + "." + payload).encode("ascii")
    )
    document["proof"] = {"jws": protected + ".." + b64e(signature)}
    return document


def test_missing_bound_inputs_fails_closed() -> None:
    result, report = run_cli(
        "--kind", "passport", "--trusted-key", KEY,
        "--revocation-list", REVOCATION, "--at-time", AT_TIME, SIGNED,
    )
    assert result.returncode == 1
    assert report["verification_primary_status"] == "BOUND_INPUTS_UNAVAILABLE"
    assert report["operating_disposition"] == "NOT_PERMITTED"
    assert any(error["code"] == "BOUND_INPUTS_UNAVAILABLE" for error in report["errors"])


def test_bound_file_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    manifest = load_strict(BUNDLE_MANIFEST, require_object=True)
    changed = deepcopy(manifest)
    agent = next(item for item in changed["files"] if item["media_type"] == "application/agent-inventory+json")
    agent["hash"] = "sha256:" + "0" * 64
    changed["bundle_id"] = domain_id(
        "global-ai-governance.agentic-assessment-bundle.identifier.v1",
        "manifest",
        {k: v for k, v in changed.items() if k != "bundle_id"},
    )
    manifest_path = _write_json(tmp_path / "manifest.json", changed)
    passport = load_strict(SIGNED, require_object=True)
    passport["bindings"]["assessment_bundle"] = changed["bundle_id"]
    passport["bindings"]["agent_inventory"] = agent["hash"]
    passport = _sign_document(passport, kind="passport")
    passport_path = _write_json(tmp_path / "passport.json", passport)
    result, report = run_cli(
        "--kind", "passport", "--trusted-key", KEY,
        "--revocation-list", REVOCATION,
        "--bundle-manifest", manifest_path, "--bundle-root", ROOT,
        "--at-time", AT_TIME, passport_path,
    )
    assert result.returncode == 1
    assert report["verification_primary_status"] == "INPUT_MISMATCH"
    assert report["operating_disposition"] == "NOT_PERMITTED"


def test_unknown_critical_extension_is_rejected_even_when_signed(tmp_path: Path) -> None:
    passport = load_strict(SIGNED, require_object=True)
    passport["extensions"] = {"com.example.must-understand": {"policy": "example"}}
    passport["critical_extensions"] = ["com.example.must-understand"]
    passport = _sign_document(passport, kind="passport")
    path = _write_json(tmp_path / "critical.json", passport)
    result, report = run_cli("--kind", "passport", "--at-time", AT_TIME, path)
    assert result.returncode == 1
    assert report["verification_primary_status"] == "UNSUPPORTED_CRITICAL_EXTENSION"
    assert report["operating_disposition"] == "NOT_PERMITTED"
    assert any(error["code"] == "UNSUPPORTED_CRITICAL_EXTENSION" for error in report["errors"])


def test_unsupported_versions_are_distinct_from_invalid_structure(tmp_path: Path) -> None:
    for field, value in [
        ("schema_version", "0.1.0-alpha.2"),
        ("framework.version", "v0.1.0-alpha.2"),
        ("profile.version", "0.1.0-alpha.2"),
    ]:
        passport = load_strict(SIGNED, require_object=True)
        if "." in field:
            parent, child = field.split(".")
            passport[parent][child] = value
        else:
            passport[field] = value
        path = _write_json(tmp_path / (field.replace(".", "-") + ".json"), passport)
        result, report = run_cli("--kind", "passport", "--at-time", AT_TIME, path)
        assert result.returncode == 1
        assert report["verification_primary_status"] == "UNSUPPORTED_VERSION"
        assert report["errors"][0]["code"] == "UNSUPPORTED_VERSION"


def test_contradictory_signed_passport_summaries_are_rejected(tmp_path: Path) -> None:
    condition = {
        "condition_id": "condition-1",
        "control_id": "AID-001",
        "owner": "owner.synthetic",
        "deadline": "2026-08-17T20:00:00Z",
        "required_evidence": ["evidence.synthetic.closure"],
        "temporary_restriction": {"maximum_action_level": 1},
        "closure_rule": {"all_required_evidence_valid": True},
    }
    mutations = {
        "approved-fail": lambda p: p["issued_assessment"]["control_summary"].__setitem__("FAIL", 1),
        "approved-conditions": lambda p: p.__setitem__("conditions", [condition]),
        "approved-level5": lambda p: p["issued_assessment"].__setitem__("maximum_action_level", 5),
        "invalid-evaluated-at": lambda p: p["issued_assessment"].__setitem__("evaluated_at", "2026-02-30T00:00:00Z"),
        "approved-not-evaluated": lambda p: p["issued_assessment"]["control_summary"].__setitem__("NOT_EVALUATED", 1),
        "conditional-empty": lambda p: p["issued_assessment"].__setitem__("result", "APPROVED_WITH_CONDITIONS"),
    }
    for name, mutate in mutations.items():
        passport = load_strict(SIGNED, require_object=True)
        mutate(passport)
        passport = _sign_document(passport, kind="passport")
        path = _write_json(tmp_path / f"{name}.json", passport)
        result, report = run_cli("--kind", "passport", "--at-time", AT_TIME, path)
        assert result.returncode == 1, name
        assert report["checks"]["semantics"] == "FAIL", name
        assert report["operating_disposition"] == "NOT_PERMITTED", name


def test_invalid_revocation_chronology_and_authority_fail_closed(tmp_path: Path) -> None:
    mutations = {
        "chronology": lambda value: value["entries"][0].__setitem__("revoked_at", "2026-07-20T00:00:00Z"),
        "authority": lambda value: value["entries"][0].__setitem__("authority", "untrusted.example.revoker"),
    }
    for name, mutate in mutations.items():
        revocation = load_strict(REVOCATION, require_object=True)
        mutate(revocation)
        revocation = _sign_document(revocation, kind="revocation")
        path = _write_json(tmp_path / f"{name}.json", revocation)
        result, report = run_cli(
            "--kind", "passport", "--trusted-key", KEY,
            "--revocation-list", path, *BUNDLE_ARGS,
            "--at-time", AT_TIME, SIGNED,
        )
        assert result.returncode == 1, name
        assert report["verification_primary_status"] == "REVOCATION_STATUS_UNKNOWN", name
        assert report["operating_disposition"] == "NOT_PERMITTED", name


def test_standalone_trusted_key_rejects_noncanonical_ed25519_x(tmp_path: Path) -> None:
    key = load_strict(KEY, require_object=True)
    original = key["jwk"]["x"]
    key["jwk"]["x"] = original[:-1] + ("B" if original[-1] != "B" else "C")
    key["kid"] = jwk_thumbprint_kid(key["jwk"])
    path = _write_json(tmp_path / "bad-key.json", key)
    result, report = run_cli("--kind", "trusted-key", "--at-time", AT_TIME, path)
    assert result.returncode == 1
    assert report["checks"]["signing_key_trust"] == "FAIL"
    assert any("JWK x is unusable" in error["message"] for error in report["errors"])
