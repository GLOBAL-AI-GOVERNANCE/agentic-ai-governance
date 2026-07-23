# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from tools.public_release_scrub import (
    SCRUB_POLICY_VERSION,
    canonical_identity_errors,
    classify_tracked_files,
    private_denylist_errors,
    validate_public_release_scrub,
)

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_PRIVATE_ALIAS = "-".join(["SYNTHETIC", "INTERNAL", "VENTURE", "ALIAS", "9F4C"])


def _repository_copy(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    shutil.copytree(
        ROOT,
        root,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"),
    )
    return root


def _external_denylist(tmp_path: Path) -> Path:
    path = tmp_path / "private-release-denylist.txt"
    path.write_text(SYNTHETIC_PRIVATE_ALIAS + "\n", encoding="utf-8")
    return path


def _append_alias(path: Path) -> None:
    path.write_text(
        path.read_text(encoding="utf-8") + f"\n{SYNTHETIC_PRIVATE_ALIAS}\n",
        encoding="utf-8",
    )


def test_canonical_public_identity_is_accepted() -> None:
    assert canonical_identity_errors(ROOT) == []


def test_private_alias_in_direct_public_file_is_rejected(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = _external_denylist(tmp_path)
    _append_alias(root / "README.md")
    assert private_denylist_errors(root, denylist) == [
        "private denylist match found in README.md"
    ]


def test_private_alias_in_nested_public_file_is_rejected(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = _external_denylist(tmp_path)
    nested = root / "governance" / "nested" / "identity.md"
    nested.parent.mkdir(parents=True)
    nested.write_text(SYNTHETIC_PRIVATE_ALIAS + "\n", encoding="utf-8")
    assert private_denylist_errors(root, denylist) == [
        "private denylist match found in governance/nested/identity.md"
    ]


def test_extensionless_notice_is_scanned(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = _external_denylist(tmp_path)
    _append_alias(root / "NOTICE")
    assert private_denylist_errors(root, denylist) == [
        "private denylist match found in NOTICE"
    ]


def test_dotfile_is_scanned(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = _external_denylist(tmp_path)
    _append_alias(root / ".gitattributes")
    assert private_denylist_errors(root, denylist) == [
        "private denylist match found in .gitattributes"
    ]


def test_generated_distribution_is_scanned(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = _external_denylist(tmp_path)
    _append_alias(root / "dist" / "AGENTIC_AI_GOVERNANCE_SPEC.md")
    assert private_denylist_errors(root, denylist) == [
        "private denylist match found in dist/AGENTIC_AI_GOVERNANCE_SPEC.md"
    ]


def test_unknown_text_suffix_is_scanned(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = _external_denylist(tmp_path)
    unknown = root / "public-surface.customtext"
    unknown.write_text(SYNTHETIC_PRIVATE_ALIAS + "\n", encoding="utf-8")
    assert private_denylist_errors(root, denylist) == [
        "private denylist match found in public-surface.customtext"
    ]


def test_non_utf8_binary_is_excluded(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    binary = root / "tests" / "synthetic-private-alias.bin"
    binary.write_bytes(SYNTHETIC_PRIVATE_ALIAS.encode("utf-8") + b"\xff")
    text_files, non_utf8_files = classify_tracked_files(root)
    assert binary not in text_files
    assert binary in non_utf8_files


def test_every_tracked_utf8_file_is_selected() -> None:
    text_files, non_utf8_files = classify_tracked_files(ROOT)
    selected = {path.relative_to(ROOT).as_posix() for path in text_files}
    excluded = {path.relative_to(ROOT).as_posix() for path in non_utf8_files}
    for relative in subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines():
        path = ROOT / relative
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            assert relative in excluded
        else:
            assert relative in selected
    assert selected.isdisjoint(excluded)


def test_bounded_external_organization_reference_is_accepted(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = _external_denylist(tmp_path)
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8")
        + "\nExternal standards organizations may be cited with bounded context.\n",
        encoding="utf-8",
    )
    assert validate_public_release_scrub(root, denylist) == []


def test_private_denylist_must_remain_outside_repository(tmp_path: Path) -> None:
    root = _repository_copy(tmp_path)
    denylist = root / "private-release-denylist.txt"
    denylist.write_text(SYNTHETIC_PRIVATE_ALIAS + "\n", encoding="utf-8")
    assert private_denylist_errors(root, denylist) == [
        "private denylist must remain outside the public repository"
    ]


def test_public_output_omits_private_denylist_count_and_digest(tmp_path: Path) -> None:
    denylist = _external_denylist(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/public_release_scrub.py"),
            str(ROOT),
            "--denylist",
            str(denylist),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert f"scrub_policy_version: {SCRUB_POLICY_VERSION}" in result.stdout
    assert "tracked_utf8_text_files_scanned:" in result.stdout
    assert "tracked_non_utf8_files_excluded:" in result.stdout
    assert "private_evidence_retained: YES" in result.stdout
    assert "private_denylist_terms" not in result.stdout
    assert "private_denylist_sha256" not in result.stdout
    assert SYNTHETIC_PRIVATE_ALIAS not in result.stdout
