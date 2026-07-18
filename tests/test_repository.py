# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

from tools.build_dist import build

ROOT = Path(__file__).resolve().parents[1]


def test_generated_spec_is_current() -> None:
    target = ROOT / "dist/AGENTIC_AI_GOVERNANCE_SPEC.md"
    assert target.read_text(encoding="utf-8") == build(ROOT)


def test_release_dependency_pins() -> None:
    requirements = {
        line.strip()
        for line in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert "pytest==9.0.3" in requirements
    assert "cryptography==49.0.0" in requirements
    assert "jsonschema==4.26.0" in requirements
