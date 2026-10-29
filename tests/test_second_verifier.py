# SPDX-License-Identifier: Apache-2.0
"""Tests for the second passport verifier (separate from the reference)."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SECOND = ROOT / "second_verifier"


def _imports_of(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_second_verifier_does_not_import_reference_modules() -> None:
    forbidden = {"tools", "agentic_ai_governance"}
    for path in SECOND.rglob("*.py"):
        imported = _imports_of(path)
        assert forbidden.isdisjoint(imported), f"{path} imports {imported & forbidden}"


def test_second_verifier_agrees_with_reference_on_examples() -> None:
    from agentic_ai_governance import validate_example
    from second_verifier import verify_passport

    cases = {
        "signed-unrevoked": "VALID",
        "signed-revoked": "REVOKED",
    }
    for name, expected in cases.items():
        reference = validate_example(name)
        assert reference.report["verification_primary_status"] == expected
        second = verify_passport(
            ROOT / f"examples/passports/{name}.json",
            trusted_key=ROOT / "examples/trusted-keys/test-ed25519-key.json",
            bundle_manifest=ROOT / "examples/bundles/valid-bundle-manifest.json",
            bundle_root=ROOT,
            revocation_list=ROOT / "examples/revocation/valid-revocation-list.json",
            at_time="2026-07-18T12:00:00Z",
        )
        assert second.primary_status == expected
        assert second.authority_effect == "NONE"
        assert second.as_dict()["verifier"] == "second_verifier"


def test_second_verifier_cli_exits_nonzero_when_revoked() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "second_verifier",
            str(ROOT / "examples/passports/signed-revoked.json"),
            "--trusted-key",
            str(ROOT / "examples/trusted-keys/test-ed25519-key.json"),
            "--bundle-manifest",
            str(ROOT / "examples/bundles/valid-bundle-manifest.json"),
            "--bundle-root",
            str(ROOT),
            "--revocation-list",
            str(ROOT / "examples/revocation/valid-revocation-list.json"),
            "--at-time",
            "2026-07-18T12:00:00Z",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    assert '"primary_status": "REVOKED"' in completed.stdout


def test_lead_agent_and_fleet_controls_are_operational() -> None:
    demo = subprocess.run(
        [sys.executable, "examples/lead-agent/lead_agent.py", "demo"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert demo.returncode == 0, demo.stderr[-2000:] + demo.stdout[-2000:]
    assert "fleet" in demo.stdout.lower() or "audit" in demo.stdout.lower() or "pass" in demo.stdout.lower()

    fleet = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_fleet_controls.py", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert fleet.returncode == 0, fleet.stdout + fleet.stderr
