# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.validate_claims_register import (
    load_json_compatible_yaml,
    matched_repository_paths,
    validate_register,
)

ROOT = Path(__file__).resolve().parents[1]


def _claims_schema() -> dict:
    return json.loads((ROOT / "governance/claims-register.schema.json").read_text(encoding="utf-8"))


def _claims() -> dict:
    return load_json_compatible_yaml(ROOT / "governance/claims-register.yaml")


def _repository_copy(
    tmp_path: Path,
    claims: dict | None = None,
    prohibited: dict | None = None,
) -> Path:
    shutil.copytree(
        ROOT,
        tmp_path,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    governance = tmp_path / "governance"
    if claims is not None:
        (governance / "claims-register.yaml").write_text(json.dumps(claims), encoding="utf-8")
    if prohibited is not None:
        (governance / "prohibited-claims.yaml").write_text(
            json.dumps(prohibited), encoding="utf-8"
        )
    return tmp_path


def _schema_errors(document: dict) -> list:
    return list(Draft202012Validator(_claims_schema()).iter_errors(document))


def test_governance_registers_validate() -> None:
    assert validate_register(ROOT) == []


def test_implemented_claims_gate_is_shipped_in_alpha2_and_not_alpha1() -> None:
    claim = next(
        item for item in _claims()["claims"]
        if item["claim_id"] == "AAG-GOV-001"
    )
    assert claim["delivery_status"] == "SHIPPED"
    assert claim["evidence_status"] == "VERIFIED"
    assert claim["verification_method"]
    assert claim["last_verified"] == "2026-08-30"
    assert claim["evidence_refs"]
    assert "v0.1.0-alpha.2" in claim["statement"]
    assert any("not retroactively part of v0.1.0-alpha.1" in item for item in claim["limitations"])
    assert any("Alpha.2" in item or "v0.1.0-alpha.2" in item for item in claim["permitted_wording"])


def test_stateful_revocation_claim_is_shipped_verified_in_alpha2() -> None:
    claim = next(
        item for item in _claims()["claims"]
        if item["claim_id"] == "AAG-RVK-002"
    )
    assert claim["delivery_status"] == "SHIPPED"
    assert claim["evidence_status"] == "VERIFIED"
    assert claim["verification_method"]
    assert claim["last_verified"] == "2026-08-30"
    assert "tests/test_cli.py" in claim["evidence_refs"]
    assert any("v0.1.0-alpha.2" in item for item in claim["evidence_refs"])
    assert any("intact trusted local store" in item for item in claim["limitations"])
    assert any("single-writer reference continuity store" in item for item in claim["limitations"])
    assert any("not part of v0.1.0-alpha.1" in item for item in claim["limitations"])


def test_partial_status_is_rejected() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["evidence_status"] = "PARTIALLY_VERIFIED"
    assert _schema_errors(document)


def test_external_fact_must_omit_delivery_status() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["claim_kind"] = "EXTERNAL_FACT"
    assert _schema_errors(document)


def test_project_claim_requires_delivery_status() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0].pop("delivery_status")
    assert _schema_errors(document)


def test_verified_claim_requires_evidence_reference() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["evidence_refs"] = []
    assert _schema_errors(document)


def test_duplicate_evidence_reference_is_rejected() -> None:
    document = copy.deepcopy(_claims())
    reference = document["claims"][0]["evidence_refs"][0]
    document["claims"][0]["evidence_refs"] = [reference, reference]
    assert _schema_errors(document)


def test_empty_evidence_reference_is_rejected() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["evidence_refs"] = [""]
    assert _schema_errors(document)


def test_verified_claim_requires_verification_method() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0].pop("verification_method")
    assert _schema_errors(document)


def test_verified_claim_requires_verification_date() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0].pop("last_verified")
    assert _schema_errors(document)


def test_project_claim_requires_supporting_artifact() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["supporting_artifacts"] = []
    assert _schema_errors(document)


def test_duplicate_supporting_artifact_is_rejected() -> None:
    document = copy.deepcopy(_claims())
    artifact = document["claims"][0]["supporting_artifacts"][0]
    document["claims"][0]["supporting_artifacts"] = [artifact, artifact]
    assert _schema_errors(document)


def test_empty_supporting_artifact_is_rejected() -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["supporting_artifacts"] = [""]
    assert _schema_errors(document)


def test_claim_ids_are_unique(tmp_path: Path) -> None:
    document = copy.deepcopy(_claims())
    document["claims"].append(copy.deepcopy(document["claims"][0]))
    root = _repository_copy(tmp_path, claims=document)
    assert "duplicate claim_id" in "\n".join(validate_register(root))


def test_missing_supporting_artifact_is_rejected(tmp_path: Path) -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["supporting_artifacts"] = ["DOES_NOT_EXIST.md"]
    root = _repository_copy(tmp_path, claims=document)
    assert "supporting_artifact 'DOES_NOT_EXIST.md' does not exist" in "\n".join(
        validate_register(root)
    )


def test_escaping_supporting_artifact_is_rejected(tmp_path: Path) -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["supporting_artifacts"] = ["../outside.md"]
    root = _repository_copy(tmp_path, claims=document)
    assert "must remain inside the repository" in "\n".join(validate_register(root))


def test_missing_local_evidence_reference_is_rejected(tmp_path: Path) -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["evidence_refs"] = ["DOES_NOT_EXIST-EVIDENCE.md"]
    root = _repository_copy(tmp_path, claims=document)
    assert "evidence_ref 'DOES_NOT_EXIST-EVIDENCE.md' does not exist" in "\n".join(
        validate_register(root)
    )


def test_malformed_remote_evidence_reference_is_rejected(tmp_path: Path) -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["evidence_refs"] = ["https:///missing-host"]
    root = _repository_copy(tmp_path, claims=document)
    assert "must include a network location" in "\n".join(validate_register(root))


def test_unsupported_evidence_scheme_is_rejected(tmp_path: Path) -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["evidence_refs"] = ["file:///tmp/evidence"]
    root = _repository_copy(tmp_path, claims=document)
    assert "unsupported URI scheme" in "\n".join(validate_register(root))


def test_local_evidence_fragment_is_explicitly_rejected(tmp_path: Path) -> None:
    document = copy.deepcopy(_claims())
    document["claims"][0]["evidence_refs"] = ["README.md#"]
    root = _repository_copy(tmp_path, claims=document)
    assert "local evidence fragments are not supported" in "\n".join(validate_register(root))


def test_repository_prohibited_wording_is_rejected(tmp_path: Path) -> None:
    prohibited = load_json_compatible_yaml(ROOT / "governance/prohibited-claims.yaml")
    prohibited["claims"] = [copy.deepcopy(prohibited["claims"][0])]
    prohibited["claims"][0]["repository_globs"] = ["README.md"]
    prohibited["claims"][0]["repository_exclusions"] = []
    prohibited["claims"][0]["external_surfaces"] = ["website"]
    root = _repository_copy(tmp_path, prohibited=prohibited)
    (root / "README.md").write_text("This project is INDEPENDENTLY CERTIFIED.", encoding="utf-8")
    errors = validate_register(root)
    assert any("prohibited wording" in error and "README.md" in error for error in errors)


@pytest.mark.parametrize(
    ("pattern", "relative_path"),
    [
        ("governance/**/*.md", "governance/PROGRAM_BASELINE.md"),
        ("decisions/**/*.md", "decisions/DR-006-continuous-vv-and-program-sequencing.md"),
        ("requirements/**/*.md", "requirements/deferred-requirements.md"),
        ("spec/**/*.md", "spec/07-revocation.md"),
        ("profiles/**/*.json", "profiles/mcp-governance-profile.json"),
        ("profiles/**/*.md", "profiles/mcp-governance-profile.md"),
        (".github/**/*.md", ".github/pull_request_template.md"),
        (".github/**/*.yml", ".github/dependabot.yml"),
        ("examples/**/*.md", "examples/README.md"),
        ("examples/**/*.md", "examples/quickstart/README.md"),
    ],
)
def test_recursive_governed_surfaces_include_direct_files(pattern: str, relative_path: str) -> None:
    assert relative_path in matched_repository_paths(ROOT, [pattern])


def test_every_active_repository_glob_matches_a_real_file() -> None:
    prohibited = load_json_compatible_yaml(ROOT / "governance/prohibited-claims.yaml")
    for rule in prohibited["claims"]:
        if rule["enforcement"] not in {"REPOSITORY_VERIFICATION", "BOTH"}:
            continue
        for pattern in rule["repository_globs"]:
            assert matched_repository_paths(ROOT, [pattern]), (rule["claim_id"], pattern)


@pytest.mark.parametrize(
    "relative_path",
    [
        "governance/PROGRAM_BASELINE.md",
        "decisions/DR-006-continuous-vv-and-program-sequencing.md",
        "requirements/deferred-requirements.md",
        "spec/07-revocation.md",
        "profiles/mcp-governance-profile.json",
        ".github/pull_request_template.md",
        ".github/dependabot.yml",
        "examples/README.md",
        "examples/quickstart/README.md",
    ],
)
def test_recursive_governed_surface_mutation_is_rejected(
    tmp_path: Path, relative_path: str
) -> None:
    root = _repository_copy(tmp_path)
    target = root / relative_path
    target.write_text(
        target.read_text(encoding="utf-8")
        + "\nThis project is independently certified.\n",
        encoding="utf-8",
    )
    errors = validate_register(root)
    assert any(relative_path in error and "prohibited wording" in error for error in errors)


def test_permitted_alternative_is_accepted(tmp_path: Path) -> None:
    prohibited = load_json_compatible_yaml(ROOT / "governance/prohibited-claims.yaml")
    prohibited["claims"] = [copy.deepcopy(prohibited["claims"][0])]
    prohibited["claims"][0]["repository_globs"] = ["README.md"]
    prohibited["claims"][0]["repository_exclusions"] = []
    prohibited["claims"][0]["external_surfaces"] = ["website"]
    root = _repository_copy(tmp_path, prohibited=prohibited)
    (root / "README.md").write_text(
        prohibited["claims"][0]["permitted_alternative"],
        encoding="utf-8",
    )
    assert validate_register(root) == []


def test_prohibited_register_is_excluded_from_scanning() -> None:
    assert validate_register(ROOT) == []
