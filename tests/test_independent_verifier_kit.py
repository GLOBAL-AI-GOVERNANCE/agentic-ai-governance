# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
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
    assert "Project-authored or Codex-authored verification is not independent" in readme
