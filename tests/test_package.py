# SPDX-License-Identifier: Apache-2.0
"""Installable Passport validator: Python API, console script, and wheel contents."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from agentic_ai_governance import __version__, reference_root, validate_example, validate_passport
from agentic_ai_governance.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_reference_root_is_checkout_when_not_installed():
    assert reference_root() == ROOT


def test_unrevoked_example_passes():
    result = validate_example("signed-unrevoked")
    assert result.exit_code == 0
    assert result.passed
    assert result.report["artifact_validation_status"] == "PASS"
    assert result.report["checks"]["revocation"] == "PASS"


def test_revoked_example_fails_closed():
    result = validate_example("signed-revoked")
    assert result.exit_code != 0
    assert not result.passed
    assert result.report["verification_primary_status"] == "REVOKED"


def test_api_matches_reference_cli_output():
    args = dict(
        trusted_key=ROOT / "examples/trusted-keys/test-ed25519-key.json",
        revocation_list=ROOT / "examples/revocation/valid-revocation-list.json",
        bundle_manifest=ROOT / "examples/bundles/valid-bundle-manifest.json",
        bundle_root=ROOT,
        at_time="2026-07-18T12:00:00Z",
    )
    passport = ROOT / "examples/passports/signed-unrevoked.json"
    api = validate_passport(passport, **args)
    direct = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools/validate_artifact.py"), "--kind", "passport",
         "--trusted-key", str(args["trusted_key"]), "--bundle-manifest", str(args["bundle_manifest"]),
         "--bundle-root", str(ROOT), "--revocation-list", str(args["revocation_list"]),
         "--at-time", args["at_time"], str(passport)],
        capture_output=True, text=True, check=False,
    )
    assert api.exit_code == direct.returncode
    assert api.report == json.loads(direct.stdout)


def test_unknown_example_rejected():
    with pytest.raises(ValueError):
        validate_example("not-an-example")


def test_cli_example_and_boundary(capsys):
    assert main(["--example", "signed-unrevoked"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["artifact_validation_status"] == "PASS"
    assert "Verification is not authorization" in captured.err


def test_cli_requires_inputs(capsys):
    with pytest.raises(SystemExit) as exc:
        main([str(ROOT / "examples/passports/signed-unrevoked.json")])
    assert exc.value.code == 2
    assert "--trusted-key" in capsys.readouterr().err


def test_cli_rejects_file_and_example_together():
    with pytest.raises(SystemExit):
        main(["--example", "signed-unrevoked", "passport.json"])


def test_version_matches_pyproject():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{__version__}"' in text


@pytest.mark.skipif(importlib.util.find_spec("setuptools") is None, reason="setuptools not installed")
def test_wheel_carries_reference_validator(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "build", "*.egg-info", "__pycache__", ".venv"))
    subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "-q", "-w", str(tmp_path), str(source)],
        check=True,
    )
    wheel = next(tmp_path.glob("agentic_ai_governance-*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        archive.extractall(tmp_path / "site")
    for required in (
        "agentic_ai_governance/cli.py",
        "agentic_ai_governance/_reference/tools/validate_artifact.py",
        "agentic_ai_governance/_reference/governance/claims-register.schema.json",
        "agentic_ai_governance/_reference/profiles/mcp-governance-profile.json",
        "agentic_ai_governance/_reference/examples/passports/signed-unrevoked.json",
        "agentic_ai_governance/_reference/LICENSE",
    ):
        assert required in names
    assert not any(name.endswith(".pyc") for name in names)
    code = (
        "import json, agentic_ai_governance as a; r = a.validate_example('signed-unrevoked');"
        "print(json.dumps([str(a.reference_root()), r.passed]))"
    )
    out = subprocess.run([sys.executable, "-B", "-c", code], cwd=tmp_path, capture_output=True, text=True,
                         env={"PYTHONPATH": str(tmp_path / "site"), "PATH": ""}, check=True)
    root, passed = json.loads(out.stdout)
    assert root.endswith("agentic_ai_governance/_reference")
    assert passed is True
