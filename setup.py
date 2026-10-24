# SPDX-License-Identifier: Apache-2.0
"""Copies the reference validator and its data into the wheel under agentic_ai_governance/_reference."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

ROOT = Path(__file__).resolve().parent
REFERENCE_TREES = ("tools", "schemas", "profiles", "examples")
REFERENCE_GLOBS = (("governance", "*.schema.json"),)
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", "test_*.py")


class BuildWithReference(build_py):
    def run(self) -> None:
        super().run()
        target = Path(self.build_lib) / "agentic_ai_governance" / "_reference"
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        for name in REFERENCE_TREES:
            shutil.copytree(ROOT / name, target / name, ignore=SKIP)
        for folder, pattern in REFERENCE_GLOBS:
            (target / folder).mkdir(parents=True, exist_ok=True)
            for path in sorted((ROOT / folder).glob(pattern)):
                shutil.copy2(path, target / folder / path.name)
        for name in ("LICENSE", "NOTICE", "LICENSE_POLICY.md"):
            shutil.copy2(ROOT / name, target / name)
        shutil.copytree(ROOT / "LICENSES", target / "LICENSES")


# Build outside the checkout so a local install never leaves schema copies inside the repository tree.
setup(
    cmdclass={"build_py": BuildWithReference},
    options={"build": {"build_base": tempfile.mkdtemp(prefix="agentic-ai-governance-build-")}},
)
