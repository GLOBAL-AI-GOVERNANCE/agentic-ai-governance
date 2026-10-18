# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "conformance/independent-verifier"


def test_neutral_manifest_is_complete_and_digest_pinned() -> None:
    manifest = json.loads((KIT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["controlling_commit"] == "e951798d64e247612f625bf50f23b10a0e30992e"
    assert manifest["controlling_tree"] == "5e035f538bf427f619e5055499ca22abe09ac653"
    assert manifest["independent_verification_established"] is False
    assert manifest["status"] == "NEUTRAL_REPRODUCTION_MATERIAL"
    records = manifest["normative_artifacts"] + manifest["vectors"]
    assert records
    for record in records:
        path = ROOT / record["path"]
        assert path.is_file(), record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]


def test_templates_cannot_be_mistaken_for_completed_evidence() -> None:
    receipt = json.loads((KIT / "INDEPENDENT_RECEIPT_TEMPLATE.json").read_text(encoding="utf-8"))
    assert receipt["result"] == "NOT_RUN"
    assert receipt["control_boundary"]["separate_from_project"] is False
    assert receipt["attestation"]["project_decision_logic_reused"] is None
    readme = (KIT / "README.md").read_text(encoding="utf-8")
    assert "does not establish independent maintenance" in readme
    assert "Project-authored or otherwise same-control-boundary verification is not independent" in readme


PASSPORT_VECTOR_PREFIX = "examples/passports/"
REQUIRED_CONTEXT_INPUTS = ("trusted_key", "revocation_list", "bundle_manifest")
FRESH_STORE = "FRESH_TRUSTED_STORE_NO_PREVIOUSLY_ACCEPTED_STATE"


def _instant(value: object) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"not a UTC RFC 3339 instant: {value!r}")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _within(at: datetime, start: object, end: object) -> bool:
    return _instant(start) <= at < _instant(end)


def evaluation_context_errors(manifest: dict, root: Path) -> list[str]:
    errors: list[str] = []
    contexts = manifest.get("evaluation_contexts")
    if not isinstance(contexts, dict) or not contexts:
        return ["manifest declares no evaluation_contexts"]
    passports = [v for v in manifest.get("vectors", []) if v.get("path", "").startswith(PASSPORT_VECTOR_PREFIX)]
    if not passports:
        errors.append("no time-sensitive passport vectors found")
    for vector in passports:
        name = vector.get("evaluation_context")
        context = contexts.get(name) if isinstance(name, str) else None
        if not isinstance(context, dict):
            errors.append(f"{vector['path']}: missing or unknown evaluation_context")
            continue
        try:
            at = _instant(context.get("at_time"))
        except (TypeError, ValueError) as exc:
            errors.append(f"{name}: invalid at_time: {exc}")
            continue
        if context.get("bundle_root") != ".":
            errors.append(f"{name}: bundle_root must be the repository root '.'")
        if context.get("revocation_state") != "STATELESS":
            errors.append(f"{name}: revocation_state assumption must be declared STATELESS")
        inputs = context.get("inputs")
        if not isinstance(inputs, dict):
            errors.append(f"{name}: missing inputs")
            continue
        loaded: dict[str, dict] = {}
        for key in REQUIRED_CONTEXT_INPUTS:
            record = inputs.get(key)
            if not isinstance(record, dict) or not record.get("path") or not record.get("sha256"):
                errors.append(f"{name}: incomplete input {key}")
                continue
            path = root / record["path"]
            if not path.is_file():
                errors.append(f"{name}: input {key} missing at {record['path']}")
                continue
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != record["sha256"]:
                errors.append(f"{name}: input {key} digest mismatch")
                continue
            loaded[key] = json.loads(data)
        key_doc = loaded.get("trusted_key")
        if key_doc is not None:
            if key_doc.get("status") != "ACTIVE" or not _within(at, key_doc.get("not_before"), key_doc.get("expires_at")):
                errors.append(f"{name}: trusted key not valid at at_time")
        revocation = loaded.get("revocation_list")
        if revocation is not None and not _within(at, revocation.get("issued_at"), revocation.get("next_update")):
            errors.append(f"{name}: revocation list not fresh at at_time")
        passport = json.loads((root / vector["path"]).read_bytes())
        validity = passport.get("validity", {})
        if not _within(at, validity.get("not_before"), validity.get("expires_at")):
            errors.append(f"{vector['path']}: at_time outside passport validity")
    return errors


def _manifest() -> dict:
    return json.loads((KIT / "manifest.json").read_text(encoding="utf-8"))


def test_passport_vectors_pin_a_complete_valid_evaluation_context() -> None:
    assert evaluation_context_errors(_manifest(), ROOT) == []


def test_initializable_continuity_declares_fresh_store_assumption() -> None:
    manifest = _manifest()
    assert manifest["stateful_revocation_expectations"]["initializable_continuity_assumption"] == FRESH_STORE
    initializable = [v for v in manifest["vectors"] if v.get("expected", {}).get("continuity") == "INITIALIZABLE"]
    assert initializable
    assert all(v.get("continuity_store_assumption") == FRESH_STORE for v in initializable)


def test_receipt_template_captures_unfilled_evaluation_context() -> None:
    receipt = json.loads((KIT / "INDEPENDENT_RECEIPT_TEMPLATE.json").read_text(encoding="utf-8"))
    assert "evaluation_time" in receipt and receipt["evaluation_time"] is None
    assert receipt["executed_at_utc"] == "REQUIRED"
    context = receipt["evaluation_context"]
    assert set(context) >= {"name", "manifest_reference", "inputs_verified"}
    assert all(value is None for value in context.values())
    readme = (KIT / "README.md").read_text(encoding="utf-8")
    assert "2026-07-18T12:00:00Z" in readme
    assert "does not substitute for the pinned evaluation time" in readme


def _first_context(manifest: dict) -> dict:
    return next(iter(manifest["evaluation_contexts"].values()))


def test_guard_missing_evaluation_time_fails() -> None:
    manifest = copy.deepcopy(_manifest())
    del _first_context(manifest)["at_time"]
    assert any("invalid at_time" in error for error in evaluation_context_errors(manifest, ROOT))


def test_guard_missing_context_reference_fails() -> None:
    manifest = copy.deepcopy(_manifest())
    for vector in manifest["vectors"]:
        vector.pop("evaluation_context", None)
    assert any("missing or unknown evaluation_context" in error for error in evaluation_context_errors(manifest, ROOT))


def test_guard_time_outside_validity_or_freshness_fails() -> None:
    for at_time in ("2026-10-18T00:00:00Z", "2026-07-17T19:59:59Z", "2026-07-19T00:00:00Z"):
        manifest = copy.deepcopy(_manifest())
        _first_context(manifest)["at_time"] = at_time
        errors = evaluation_context_errors(manifest, ROOT)
        assert errors, at_time


def test_guard_wrong_bound_input_digest_fails() -> None:
    for key in REQUIRED_CONTEXT_INPUTS:
        manifest = copy.deepcopy(_manifest())
        _first_context(manifest)["inputs"][key]["sha256"] = "0" * 64
        assert f"input {key} digest mismatch" in " ".join(evaluation_context_errors(manifest, ROOT))


def test_guard_tampered_bound_input_bytes_fail(tmp_path: Path) -> None:
    manifest = _manifest()
    for relative in {v["path"] for v in manifest["vectors"]} | {
        r["path"] for r in _first_context(manifest)["inputs"].values()
    }:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    assert evaluation_context_errors(manifest, tmp_path) == []
    key_path = tmp_path / _first_context(manifest)["inputs"]["trusted_key"]["path"]
    key_path.write_bytes(key_path.read_bytes() + b"\n")
    assert "input trusted_key digest mismatch" in " ".join(evaluation_context_errors(manifest, tmp_path))
