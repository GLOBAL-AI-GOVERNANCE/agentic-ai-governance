# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from tools.build_dist import build

ROOT = Path(__file__).resolve().parents[1]


def test_generated_spec_is_current() -> None:
    target = ROOT / "dist/AGENTIC_AI_GOVERNANCE_SPEC.md"
    content = target.read_text(encoding="utf-8")
    assert content == build(ROOT)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == "90e90b45add031cb03633a6d0706f54fd819558bed9f21cdfe3bec5c89989988"


def test_schema_catalog_is_complete() -> None:
    catalog = json.loads((ROOT / "schemas/schema-catalog.json").read_text(encoding="utf-8"))
    cataloged = {entry["schema_file"] for entry in catalog["entries"]}
    actual = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*.schema.json") if ".git" not in path.parts}
    assert cataloged == actual


def test_release_dependency_pins() -> None:
    requirements = {
        line.strip()
        for line in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert "pytest==9.0.3" in requirements
    assert "cryptography==49.0.0" in requirements
    assert "jsonschema==4.26.0" in requirements


def test_verifier_reports_catalog_failure_without_traceback(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    shutil.copytree(
        ROOT,
        root,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )

    schema_path = root / "schemas/action-authority.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["title"] = "Mutated protected schema"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")

    catalog_path = root / "schemas/schema-catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entry = next(
        item for item in catalog["entries"]
        if item["schema_file"] == "schemas/action-authority.schema.json"
    )
    entry["content_sha256"] = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(root / "tools/verify_repository.py"), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 1
    assert result.stdout.startswith("CONFORMANCE FAILED\n")
    assert "protected schema content changed" in combined
    assert "Traceback" not in combined


def test_changelog_keeps_shipped_alpha1_work_out_of_unreleased() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased, alpha1 = changelog.split("## v0.1.0-alpha.1", maxsplit=1)
    shipped_bullets = [
        "Added semantic evidence admission, profile descriptors, inventory schemas",
        "Added signed adversarial regressions for expired or untrusted evidence",
        "Added pinned `pip-audit` to the connected CI gate",
        "Enforced bidirectional equality between declared MCP inventory servers",
    ]
    for bullet in shipped_bullets:
        assert bullet not in unreleased
        assert bullet in alpha1
