# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from tools.schema_catalog import catalog_schema_paths

ROOT = Path(__file__).resolve().parents[1]


def _copy_catalog_tree(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "schemas", tmp_path / "schemas")
    (tmp_path / "governance").mkdir()
    for name in ["claims-register.schema.json", "prohibited-claims.schema.json"]:
        shutil.copy2(ROOT / "governance" / name, tmp_path / "governance" / name)
    return tmp_path


def _catalog(root: Path) -> dict:
    return json.loads((root / "schemas/schema-catalog.json").read_text(encoding="utf-8"))


def _write_catalog(root: Path, catalog: dict) -> None:
    (root / "schemas/schema-catalog.json").write_text(
        json.dumps(catalog, indent=2) + "\n",
        encoding="utf-8",
    )


def _raw_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _refresh_catalog_digest(root: Path, relative_path: str) -> None:
    catalog = _catalog(root)
    target = next(entry for entry in catalog["entries"] if entry["schema_file"] == relative_path)
    target["content_sha256"] = _raw_digest(root / relative_path)
    _write_catalog(root, catalog)


def _add_unprotected_schema(root: Path, filename: str, schema: dict) -> str:
    relative = f"schemas/{filename}"
    path = root / relative
    path.write_text(json.dumps(schema), encoding="utf-8")
    catalog = _catalog(root)
    catalog["entries"].append(
        {
            "schema_file": relative,
            "schema_id": schema["$id"],
            "artifact_kind": "GOVERNANCE_SCHEMA",
            "artifact_version": "1.0.0",
            "id_strategy": "URN",
            "status": "ACTIVE",
            "introduced_in": "TEST",
            "supersedes": None,
            "content_sha256": _raw_digest(path),
            "license": "Apache-2.0",
        }
    )
    _write_catalog(root, catalog)
    return relative


def test_schema_catalog_and_all_references_resolve() -> None:
    assert len(catalog_schema_paths(ROOT)) == 17


def test_uncataloged_schema_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    source = root / "schemas/common.schema.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    document["$id"] = "urn:example:uncataloged:1.0.0"
    (root / "schemas/uncataloged.schema.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match="uncataloged"):
        catalog_schema_paths(root)


def test_duplicate_schema_file_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    duplicate = copy.deepcopy(catalog["entries"][0])
    duplicate["schema_id"] = "urn:example:duplicate-file:1.0.0"
    catalog["entries"].append(duplicate)
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="duplicate schema_file"):
        catalog_schema_paths(root)


def test_duplicate_schema_id_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    duplicate = copy.deepcopy(catalog["entries"][0])
    duplicate["schema_file"] = "schemas/duplicate.schema.json"
    source = root / catalog["entries"][0]["schema_file"]
    shutil.copy2(source, root / duplicate["schema_file"])
    duplicate["content_sha256"] = _raw_digest(root / duplicate["schema_file"])
    catalog["entries"].append(duplicate)
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="duplicate schema_id"):
        catalog_schema_paths(root)


def test_modified_alpha1_identifier_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    target = next(
        entry for entry in catalog["entries"]
        if entry["schema_file"] == "schemas/action-authority.schema.json"
    )
    target["schema_id"] = "urn:example:changed-alpha1:1.0.0"
    schema_path = root / target["schema_file"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = target["schema_id"]
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    target["content_sha256"] = _raw_digest(schema_path)
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="protected schema identifier changed"):
        catalog_schema_paths(root)


def test_alpha1_schema_content_change_is_rejected_even_if_catalog_digest_updated(
    tmp_path: Path,
) -> None:
    root = _copy_catalog_tree(tmp_path)
    relative = "schemas/action-authority.schema.json"
    path = root / relative
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema["title"] = "Mutated Alpha.1 title"
    path.write_text(json.dumps(schema), encoding="utf-8")
    _refresh_catalog_digest(root, relative)
    with pytest.raises(ValueError, match="protected schema content changed"):
        catalog_schema_paths(root)


def test_governance_schema_change_without_new_digest_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    path = root / "governance/claims-register.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema["title"] = "Changed governance schema"
    path.write_text(json.dumps(schema), encoding="utf-8")
    with pytest.raises(ValueError, match="schema content digest mismatch"):
        catalog_schema_paths(root)


def test_catalog_digest_mismatch_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    catalog["entries"][0]["content_sha256"] = "0" * 64
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="schema content digest mismatch"):
        catalog_schema_paths(root)


def test_missing_catalog_digest_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    catalog["entries"][0].pop("content_sha256")
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="schema catalog validation failed"):
        catalog_schema_paths(root)


def test_malformed_catalog_digest_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    catalog["entries"][0]["content_sha256"] = "not-a-sha256"
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="schema catalog validation failed"):
        catalog_schema_paths(root)


def test_digest_copied_from_another_schema_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    catalog["entries"][0]["content_sha256"] = catalog["entries"][1]["content_sha256"]
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="schema content digest mismatch"):
        catalog_schema_paths(root)


def test_missing_cataloged_file_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    (root / "schemas/tool-inventory.schema.json").unlink()
    with pytest.raises(ValueError, match="cataloged schema missing"):
        catalog_schema_paths(root)


def test_invalid_catalog_root_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    catalog["catalog_id"] = "urn:example:wrong-catalog:1.0.0"
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="schema catalog validation failed"):
        catalog_schema_paths(root)


def test_unresolved_local_ref_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:example:test-local-ref:1.0.0",
        "type": "object",
        "$defs": {"known": {"type": "string"}},
        "properties": {"broken": {"$ref": "#/$defs/does-not-exist"}},
    }
    _add_unprotected_schema(root, "test-local-ref.schema.json", schema)
    with pytest.raises(ValueError, match=r"unresolved \$ref"):
        catalog_schema_paths(root)


def test_unresolved_cross_schema_ref_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:example:test-cross-ref:1.0.0",
        "type": "object",
        "properties": {"broken": {"$ref": "missing.schema.json#/$defs/id"}},
    }
    _add_unprotected_schema(root, "test-cross-ref.schema.json", schema)
    with pytest.raises(ValueError, match=r"unresolved \$ref"):
        catalog_schema_paths(root)


def test_silent_removal_of_active_schema_is_rejected(tmp_path: Path) -> None:
    root = _copy_catalog_tree(tmp_path)
    catalog = _catalog(root)
    catalog["entries"] = [
        entry for entry in catalog["entries"]
        if entry["schema_file"] != "schemas/trusted-key.schema.json"
    ]
    (root / "schemas/trusted-key.schema.json").unlink()
    _write_catalog(root, catalog)
    with pytest.raises(ValueError, match="protected active schema removed"):
        catalog_schema_paths(root)


def test_cataloged_schemas_have_in_band_spdx_identifiers() -> None:
    catalog = _catalog(ROOT)
    for entry in catalog["entries"]:
        schema = json.loads((ROOT / entry["schema_file"]).read_text(encoding="utf-8"))
        assert schema.get("$comment") == f"SPDX-License-Identifier: {entry['license']}"


def test_schema_catalog_record_has_in_band_spdx_identifier() -> None:
    catalog = _catalog(ROOT)
    assert catalog.get("$comment") == "SPDX-License-Identifier: Apache-2.0"
