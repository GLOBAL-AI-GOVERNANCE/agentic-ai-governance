# SPDX-License-Identifier: Apache-2.0
"""Passport issuance from a policy file: every passport VALID, revocation and refresh re-sign the list."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import issue_passports as issuer

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "examples/fleet-issuance/fleet-policy.json").read_text(encoding="utf-8"))
AT = issuer.parse("2026-07-18T12:00:00Z")


def _status(out: Path, agent_id: str, at=AT) -> dict:
    folder = out / "agents" / agent_id
    return issuer.validate(folder / "passport.json", out / "trusted-key.json", out / "revocation-list.json",
                           folder / "bundle-manifest.json", folder / "bundle", at)


def test_policy_issues_valid_passports_and_bindings(tmp_path: Path) -> None:
    fleet = issuer.issue_fleet(POLICY, tmp_path, at=AT)
    assert [a["verification_primary_status"] for a in fleet["agents"]] == ["VALID"] * 3
    assert (tmp_path / "signing-key.json").stat().st_mode & 0o077 == 0
    binding = json.loads((tmp_path / "agents/agent.example.writer/sub-agent-binding.json").read_text())
    lead = json.loads((tmp_path / "agents/agent.example.lead/passport.json").read_text())
    assert binding["parent_passport_id"] == lead["passport_id"] and binding["delegation_depth"] == 1
    assert "d" not in json.loads((tmp_path / "trusted-key.json").read_text())["jwk"]


def test_revoke_makes_only_that_passport_fail(tmp_path: Path) -> None:
    fleet = issuer.issue_fleet(POLICY, tmp_path, at=AT)
    target = next(a for a in fleet["agents"] if a["agent_id"] == "agent.example.researcher")
    first = json.loads((tmp_path / "revocation-list.json").read_text())
    issuer.revoke(tmp_path, target["passport_id"], at=AT)
    second = json.loads((tmp_path / "revocation-list.json").read_text())
    assert second["sequence_number"] == first["sequence_number"] + 1
    assert second["previous_list_hash"] == first["list_id"]
    assert _status(tmp_path, "agent.example.researcher")["verification_primary_status"] == "REVOKED"
    assert _status(tmp_path, "agent.example.writer")["verification_primary_status"] == "VALID"


def test_refresh_keeps_passports_valid_later(tmp_path: Path) -> None:
    issuer.issue_fleet(POLICY, tmp_path, at=AT)
    later = issuer.parse("2026-07-20T12:00:00Z")
    assert _status(tmp_path, "agent.example.lead", later)["verification_primary_status"] != "VALID"
    issuer.refresh(tmp_path, at=later)
    assert _status(tmp_path, "agent.example.lead", later)["verification_primary_status"] == "VALID"


@pytest.mark.parametrize("change, message", [
    (lambda p: p["agents"][0].update(maximum_action_level=5), "Level 5 is never issued"),
    (lambda p: p["agents"][0]["action_terms"].append("spend_funds"), "action_terms"),
    (lambda p: p["agents"][1].update(parent="agent.example.writer", action_terms=[]), "level exceeds parent"),
    (lambda p: p["agents"][1]["action_terms"].append("install_tool"), "action terms exceed parent"),
])
def test_policy_rejects_escalation(change, message) -> None:
    policy = copy.deepcopy(POLICY)
    change(policy)
    with pytest.raises(issuer.IssuanceError, match=message):
        issuer.load_policy(policy)


def test_cli_issue_exit_zero(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, str(ROOT / "tools/issue_passports.py"), "issue",
                             str(ROOT / "examples/fleet-issuance/fleet-policy.json"), "--out", str(tmp_path / "f"),
                             "--at-time", "2026-07-18T12:00:00Z"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert {a["verification_primary_status"] for a in json.loads(result.stdout)["agents"]} == {"VALID"}
