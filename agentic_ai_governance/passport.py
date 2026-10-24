# SPDX-License-Identifier: Apache-2.0
"""Python API around ``tools/validate_artifact.py --kind passport``.

The reference validator runs in a separate interpreter process so that its
``tools`` package never shadows a module of the same name in the caller.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_PACKAGE_DIR = Path(__file__).resolve().parent

EXAMPLES = {
    "signed-unrevoked": "examples/passports/signed-unrevoked.json",
    "signed-revoked": "examples/passports/signed-revoked.json",
}
EXAMPLE_TRUSTED_KEY = "examples/trusted-keys/test-ed25519-key.json"
EXAMPLE_REVOCATION_LIST = "examples/revocation/valid-revocation-list.json"
EXAMPLE_BUNDLE_MANIFEST = "examples/bundles/valid-bundle-manifest.json"
EXAMPLE_AT_TIME = "2026-07-18T12:00:00Z"


@dataclass(frozen=True)
class PassportValidation:
    """Validator report plus its exit code. ``report`` is the validator JSON, unchanged."""

    exit_code: int
    report: dict[str, Any]

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and self.report.get("artifact_validation_status") == "PASS"


def reference_root() -> Path:
    """Directory holding ``tools/``, ``schemas/``, ``governance/``, ``profiles/``, and ``examples/``.

    Installed wheels carry a copy under ``agentic_ai_governance/_reference``.
    A source checkout uses the repository root.
    """
    for candidate in (_PACKAGE_DIR / "_reference", _PACKAGE_DIR.parent):
        if (candidate / "tools" / "validate_artifact.py").is_file() and (candidate / "schemas").is_dir():
            return candidate
    raise RuntimeError("Agentic AI Governance reference validator files were not found.")


def _run(arguments: list[str]) -> PassportValidation:
    script = reference_root() / "tools" / "validate_artifact.py"
    completed = subprocess.run(
        [sys.executable, "-B", str(script), "--kind", "passport", *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"reference validator returned no JSON report (exit {completed.returncode}): "
            f"{completed.stderr.strip()[:500]}"
        ) from exc
    return PassportValidation(exit_code=completed.returncode, report=report)


def validate_passport(
    passport: str | Path,
    *,
    trusted_key: str | Path,
    bundle_manifest: str | Path,
    bundle_root: str | Path,
    revocation_list: str | Path | None = None,
    revocation_state: str | Path | None = None,
    initialize_revocation_state: bool = False,
    at_time: str | None = None,
) -> PassportValidation:
    """Validate a passport file with the same checks as ``tools/validate_artifact.py``."""
    arguments = [
        "--trusted-key", str(trusted_key),
        "--bundle-manifest", str(bundle_manifest),
        "--bundle-root", str(bundle_root),
    ]
    if revocation_list is not None:
        arguments += ["--revocation-list", str(revocation_list)]
    if revocation_state is not None:
        arguments += ["--revocation-state", str(revocation_state)]
    if initialize_revocation_state:
        arguments.append("--initialize-revocation-state")
    if at_time is not None:
        arguments += ["--at-time", at_time]
    arguments.append(str(passport))
    return _run(arguments)


def validate_example(name: str = "signed-unrevoked") -> PassportValidation:
    """Validate one of the bundled synthetic example passports at the fixed example time."""
    if name not in EXAMPLES:
        raise ValueError(f"unknown example {name!r}; choose one of {sorted(EXAMPLES)}")
    root = reference_root()
    return validate_passport(
        root / EXAMPLES[name],
        trusted_key=root / EXAMPLE_TRUSTED_KEY,
        revocation_list=root / EXAMPLE_REVOCATION_LIST,
        bundle_manifest=root / EXAMPLE_BUNDLE_MANIFEST,
        bundle_root=root,
        at_time=EXAMPLE_AT_TIME,
    )
