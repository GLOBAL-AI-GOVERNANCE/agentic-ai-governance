# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Callable

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.binding_verification import verify_passport_bindings
from tools.canonical_json import canonicalize
from tools.crypto import b64e, verify_jws
from tools.semantic_rules import parse_time
from tools.strict_json import load_strict
from tools.verify_repository import domain_id, registry

ROOT = Path(__file__).resolve().parents[1]
AT_TIME = "2026-07-18T12:00:00Z"
AT = parse_time(AT_TIME)
TEST_SEED = bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _jcs_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(canonicalize(load_strict(path, require_object=True))).hexdigest()


def _exact_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence_artifact_hash(value: dict) -> str:
    return domain_id(
        "global-ai-governance.data-authority-evidence.artifact.v1",
        "evidence",
        {key: item for key, item in value.items() if key != "artifact_hash"},
    )


def _sign_passport(value: dict) -> dict:
    document = deepcopy(value)
    document.pop("proof", None)
    document["passport_id"] = domain_id(
        "global-ai-governance.agent-trust-passport.identifier.v1",
        "passport",
        {key: item for key, item in document.items() if key != "passport_id"},
    )
    key = load_strict(ROOT / "examples/trusted-keys/test-ed25519-key.json", require_object=True)
    header = {
        "alg": "Ed25519",
        "cty": "application/agent-trust-passport+json",
        "kid": key["kid"],
        "typ": "atp+jws",
    }
    protected = b64e(canonicalize(header))
    payload = b64e(canonicalize(document))
    signature = Ed25519PrivateKey.from_private_bytes(TEST_SEED).sign(
        (protected + "." + payload).encode("ascii")
    )
    document["proof"] = {"jws": protected + ".." + b64e(signature)}
    assert not verify_jws(
        document,
        key,
        typ="atp+jws",
        cty="application/agent-trust-passport+json",
    )
    return document


Mutator = Callable[[dict[str, dict], dict], None]


def _case(tmp_path: Path, mutate: Mutator, *, sync_profile_hash: bool = True) -> tuple[str, list[str]]:
    shutil.copytree(ROOT / "examples", tmp_path / "examples")
    shutil.copytree(ROOT / "profiles", tmp_path / "profiles")

    paths = {
        "assessment": tmp_path / "examples/assessments/approved-readonly.json",
        "graph": tmp_path / "examples/action-authority/readonly-graph.json",
        "evidence": tmp_path / "examples/data-authority/synthetic-evidence.json",
        "agent": tmp_path / "examples/inventories/agent.json",
        "mcp": tmp_path / "examples/inventories/mcp.json",
        "tools": tmp_path / "examples/inventories/tools.json",
        "descriptor": tmp_path / "profiles/mcp-governance-profile.json",
        "profile_md": tmp_path / "profiles/mcp-governance-profile.md",
    }
    values = {
        name: load_strict(path, require_object=True)
        for name, path in paths.items()
        if path.suffix == ".json"
    }
    passport = load_strict(ROOT / "examples/passports/signed-unrevoked.json", require_object=True)

    mutate(values, passport)

    values["evidence"]["artifact_hash"] = _evidence_artifact_hash(values["evidence"])
    values["assessment"]["assessment_id"] = domain_id(
        "global-ai-governance.agentic-assessment.identifier.v1",
        "assessment",
        {key: item for key, item in values["assessment"].items() if key != "assessment_id"},
    )

    for name, value in values.items():
        _write(paths[name], value)

    if sync_profile_hash:
        values["descriptor"]["control_profile"]["hash"] = _exact_hash(paths["profile_md"])
        _write(paths["descriptor"], values["descriptor"])

    base_manifest = load_strict(ROOT / "examples/bundles/valid-bundle-manifest.json", require_object=True)
    entries = []
    for original in base_manifest["files"]:
        path = tmp_path / original["path"]
        current = deepcopy(original)
        current["size_bytes"] = path.stat().st_size
        current["hash"] = _jcs_hash(path) if current["canonicalization"] == "JCS" else _exact_hash(path)
        entries.append(current)
    manifest = {"schema_version": "0.1.0-alpha.1", "bundle_id": "", "files": entries}
    manifest["bundle_id"] = domain_id(
        "global-ai-governance.agentic-assessment-bundle.identifier.v1",
        "manifest",
        {key: item for key, item in manifest.items() if key != "bundle_id"},
    )
    manifest_path = tmp_path / "examples/bundles/valid-bundle-manifest.json"
    _write(manifest_path, manifest)

    by_media = {item["media_type"]: item for item in entries}
    assessment = values["assessment"]
    issued = passport["issued_assessment"]
    issued.update(
        {
            "assessment_id": assessment["assessment_id"],
            "result": assessment["result"],
            "evaluated_at": assessment["evaluated_at"],
            "data_authority_status": assessment["data_authority_status"],
            "maximum_action_level": assessment["maximum_action_level"],
        }
    )
    counts = {name: 0 for name in ("PASS", "FAIL", "NOT_APPLICABLE", "NOT_EVALUATED", "ERROR")}
    for control in assessment["control_results"]:
        counts[control["outcome"]] += 1
    issued["control_summary"] = counts
    passport["conditions"] = deepcopy(assessment["conditions"])

    bindings = passport["bindings"]
    bindings.update(
        {
            "assessment_bundle": manifest["bundle_id"],
            "action_authority_graph": by_media["application/agentic-ai-action-authority+json"]["hash"],
            "agent_inventory": by_media["application/agent-inventory+json"]["hash"],
            "mcp_inventory": by_media["application/mcp-inventory+json"]["hash"],
            "tool_inventory": by_media["application/tool-inventory+json"]["hash"],
            "control_profile": by_media["application/agentic-ai-control-profile+markdown"]["hash"],
            "control_profile_descriptor": by_media["application/agentic-ai-control-profile-descriptor+json"]["hash"],
            "data_authority_evidence": [by_media["application/agentic-ai-data-authority+json"]["hash"]],
        }
    )
    descriptor = values["descriptor"]
    bindings["evaluator_id"] = descriptor["evaluator"]["id"]
    bindings["evaluator_version"] = descriptor["evaluator"]["version"]
    bindings["assessment_policy_id"] = descriptor["assessment_policy"]["id"]
    bindings["assessment_policy_version"] = descriptor["assessment_policy"]["version"]
    passport["profile"] = {
        "id": descriptor["profile_id"],
        "version": descriptor["profile_version"],
    }

    # A mutator may intentionally replace the passport projection after the bound assessment is synchronized.
    late = passport.pop("_late_mutation", None)
    if callable(late):
        late(passport)

    passport = _sign_passport(passport)
    return verify_passport_bindings(
        passport,
        manifest_path=manifest_path,
        bundle_root=tmp_path,
        repository_root=ROOT,
        schema_store=registry(ROOT),
        at_time=AT,
    )


def test_data_authority_evidence_is_validated_not_only_hashed(tmp_path: Path) -> None:
    cases = {
        "expired": lambda values, _: values["evidence"]["validity"].update(
            {"not_before": "2026-07-01T00:00:00Z", "expires_at": "2026-07-10T00:00:00Z"}
        ),
        "invalid-interval": lambda values, _: values["evidence"]["validity"].update(
            {"not_before": "2026-12-31T00:00:00Z", "expires_at": "2026-07-01T00:00:00Z"}
        ),
        "scope-mismatch": lambda values, _: values["agent"]["data_use"]["purposes"].__setitem__(
            0, "production-use"
        ),
    }
    for name, mutate in cases.items():
        status, errors = _case(tmp_path / name, mutate)
        assert status == "DATA_AUTHORITY_INVALID", (name, status, errors)


def test_untrusted_or_unsupported_data_authority_is_unknown(tmp_path: Path) -> None:
    cases = {
        "issuer": lambda values, _: values["evidence"].__setitem__("issuer_id", "untrusted.example"),
        "scheme": lambda values, _: values["evidence"].__setitem__("scheme", "unrecognized.example"),
    }
    for name, mutate in cases.items():
        status, errors = _case(tmp_path / name, mutate)
        assert status == "DATA_AUTHORITY_UNKNOWN", (name, status, errors)


def test_complete_conditions_are_reconciled(tmp_path: Path) -> None:
    condition = {
        "condition_id": "condition-assessment",
        "control_id": "AID-001",
        "owner": "owner.assessment",
        "deadline": "2026-08-17T20:00:00Z",
        "required_evidence": ["evidence.data-authority.synthetic"],
        "temporary_restriction": {"maximum_action_level": 1},
        "closure_rule": {"all_required_evidence_valid": True},
    }
    other = deepcopy(condition)
    other.update({"condition_id": "condition-passport", "owner": "owner.passport"})

    def mutate(values: dict[str, dict], passport: dict) -> None:
        values["assessment"]["result"] = "APPROVED_WITH_CONDITIONS"
        values["assessment"]["conditions"] = [condition]
        passport["_late_mutation"] = lambda value: value.__setitem__("conditions", [other])

    status, errors = _case(tmp_path, mutate)
    assert status == "INPUT_MISMATCH", errors
    assert any("conditions" in message for message in errors)


def test_every_assessment_evidence_reference_resolves(tmp_path: Path) -> None:
    def mutate(values: dict[str, dict], _: dict) -> None:
        values["assessment"]["control_results"][0]["evidence_refs"] = ["evidence.missing"]

    status, errors = _case(tmp_path, mutate)
    assert status == "INPUT_MISMATCH", errors
    assert any("not admitted" in message for message in errors)


def test_profile_evaluator_and_policy_are_support_validated(tmp_path: Path) -> None:
    cases = {
        "profile": (
            "UNSUPPORTED_PROFILE",
            lambda values, _: values["descriptor"].__setitem__("profile_id", "com.example.unknown-profile"),
        ),
        "evaluator": (
            "UNSUPPORTED_PROFILE",
            lambda values, _: values["descriptor"]["evaluator"].update(
                {"id": "com.example.evaluator", "version": "evaluator-9.9.9"}
            ),
        ),
        "policy": (
            "UNSUPPORTED_PROFILE",
            lambda values, _: values["descriptor"]["assessment_policy"].update(
                {"id": "com.example.policy", "version": "9.9.9"}
            ),
        ),
    }
    for name, (expected, mutate) in cases.items():
        status, errors = _case(tmp_path / name, mutate)
        assert status == expected, (name, status, errors)


def test_profile_content_hash_is_semantically_bound(tmp_path: Path) -> None:
    def mutate(_: dict[str, dict], __: dict) -> None:
        path = tmp_path / "profiles/mcp-governance-profile.md"
        path.write_text(path.read_text(encoding="utf-8").replace("0.1.0-alpha.1", "9.9.9", 1), encoding="utf-8")

    status, errors = _case(tmp_path, mutate, sync_profile_hash=False)
    assert status == "UNSUPPORTED_PROFILE", errors
    assert any("pinned" in message or "profile" in message for message in errors)


def test_action_authority_and_inventory_cross_checks_fail_closed(tmp_path: Path) -> None:
    def destructive(values: dict[str, dict], _: dict) -> None:
        values["graph"]["dimensions"]["self_modification"] = True
        values["graph"]["computed_level"] = 5
        values["graph"]["nodes"][1]["base_level"] = 5
        values["tools"]["tools"][0]["action_level"] = 5

    status, errors = _case(tmp_path / "destructive", destructive)
    assert status == "INPUT_MISMATCH", errors
    assert any("action-authority" in message or "Level 5" in message for message in errors)

    status, errors = _case(
        tmp_path / "other-agent",
        lambda values, _: values["agent"].__setitem__("agent_id", "agent.other"),
    )
    assert status == "INPUT_MISMATCH", errors
    assert any("agent_id" in message for message in errors)

def test_active_condition_restriction_caps_effective_authority(tmp_path: Path) -> None:
    condition = {
        "condition_id": "condition.temporary-level-one",
        "control_id": "AID-001",
        "owner": "owner.synthetic",
        "deadline": "2026-08-17T20:00:00Z",
        "required_evidence": ["evidence.data-authority.synthetic"],
        "temporary_restriction": {"maximum_action_level": 1},
        "closure_rule": {"all_required_evidence_valid": True},
    }

    def mutate(values: dict[str, dict], _: dict) -> None:
        values["assessment"]["result"] = "APPROVED_WITH_CONDITIONS"
        values["assessment"]["requested_action_level"] = 4
        values["assessment"]["maximum_action_level"] = 4
        values["assessment"]["conditions"] = [condition]
        values["graph"]["requested_level"] = 4
        values["graph"]["computed_level"] = 4
        values["graph"]["nodes"][0]["base_level"] = 4

    status, errors = _case(tmp_path, mutate)
    assert status == "INPUT_MISMATCH", errors
    assert any("effective maximum" in message for message in errors)


def test_canonical_profile_policy_cannot_be_redefined_by_bundle(tmp_path: Path) -> None:
    cases = {
        "issuer": lambda values, _: (
            values["descriptor"].__setitem__("trusted_data_authority_issuers", ["untrusted.example"]),
            values["evidence"].__setitem__("issuer_id", "untrusted.example"),
        ),
        "controls": lambda values, _: (
            values["descriptor"].__setitem__("supported_control_ids", ["XYZ-999"]),
            values["assessment"]["control_results"][0].__setitem__("control_id", "XYZ-999"),
        ),
        "signature-policy": lambda values, _: values["descriptor"]["supported_data_authority_schemes"][0].__setitem__(
            "requires_signature", True
        ),
    }
    for name, mutate in cases.items():
        status, errors = _case(tmp_path / name, mutate)
        assert status == "UNSUPPORTED_PROFILE", (name, status, errors)
        assert any("pinned" in message or "profile" in message for message in errors)


def test_evidence_must_be_valid_when_assessment_was_evaluated(tmp_path: Path) -> None:
    def mutate(values: dict[str, dict], _: dict) -> None:
        values["evidence"]["validity"].update(
            {"not_before": "2026-07-18T00:00:00Z", "expires_at": "2026-12-31T00:00:00Z"}
        )

    status, errors = _case(tmp_path, mutate)
    assert status == "DATA_AUTHORITY_INVALID", errors
    assert any("assessment was evaluated" in message for message in errors)


def test_agent_capabilities_map_to_minimum_authority(tmp_path: Path) -> None:
    def mutate(values: dict[str, dict], _: dict) -> None:
        values["agent"]["declared_capabilities"] = ["execute:destructive"]

    status, errors = _case(tmp_path, mutate)
    assert status == "INPUT_MISMATCH", errors
    assert any("agent capabilities" in message for message in errors)


def test_tool_effects_map_to_minimum_authority(tmp_path: Path) -> None:
    def mutate(values: dict[str, dict], _: dict) -> None:
        values["tools"]["tools"][0]["effects"] = ["self-modification"]
        values["tools"]["tools"][0]["action_level"] = 1

    status, errors = _case(tmp_path, mutate)
    assert status == "INPUT_MISMATCH", errors
    assert any("effects" in message for message in errors)


def test_mcp_servers_and_scopes_map_to_graph_authority(tmp_path: Path) -> None:
    def high_scope(values: dict[str, dict], _: dict) -> None:
        values["mcp"]["servers"][0]["declared_scope"] = ["identity-admin:write"]

    status, errors = _case(tmp_path / "scope", high_scope)
    assert status == "INPUT_MISMATCH", errors
    assert any("MCP" in message and "scope" in message for message in errors)

    def missing_server(values: dict[str, dict], _: dict) -> None:
        values["mcp"]["servers"][0]["server_id"] = "mcp.synthetic.unrepresented"

    status, errors = _case(tmp_path / "server", missing_server)
    assert status == "INPUT_MISMATCH", errors
    assert any("MCP_SERVER" in message for message in errors)


def test_undeclared_mcp_server_in_action_graph_fails_closed(tmp_path: Path) -> None:
    def mutate(values: dict[str, dict], _: dict) -> None:
        values["graph"]["nodes"].append(
            {
                "node_id": "mcp.synthetic.undeclared",
                "node_type": "MCP_SERVER",
                "base_level": 1,
            }
        )
        values["graph"]["edges"].append(
            {
                "from": "agent.synthetic.quickstart",
                "to": "mcp.synthetic.undeclared",
                "edge_type": "INVOKES",
            }
        )

    status, errors = _case(tmp_path, mutate)
    assert status == "INPUT_MISMATCH", errors
    assert any(
        "MCP servers absent from inventory" in message
        and "mcp.synthetic.undeclared" in message
        for message in errors
    )


def test_graph_edge_semantics_affect_authority(tmp_path: Path) -> None:
    def mutate(values: dict[str, dict], _: dict) -> None:
        values["graph"]["edges"][0]["edge_type"] = "PUBLISHES"
        values["graph"]["dimensions"]["external_publication"] = False
        values["graph"]["computed_level"] = 2

    status, errors = _case(tmp_path, mutate)
    assert status == "BOUND_INPUTS_INCOMPLETE", errors
    assert any("PUBLISHES" in message and "external_publication" in message for message in errors)



def test_known_profile_identity_cannot_redefine_canonical_document(tmp_path: Path) -> None:
    def mutate(_: dict[str, dict], __: dict) -> None:
        path = tmp_path / "profiles/mcp-governance-profile.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nUnrestricted destructive production actions are permitted.\n",
            encoding="utf-8",
        )

    status, errors = _case(tmp_path, mutate)
    assert status == "UNSUPPORTED_PROFILE", errors
    assert any("pinned document hash" in message for message in errors)


def test_unknown_inventory_semantics_fail_schema_before_permission(tmp_path: Path) -> None:
    cases = {
        "capability": lambda values, _: values["agent"].__setitem__(
            "declared_capabilities", ["unknown:capability"]
        ),
        "scope": lambda values, _: values["mcp"]["servers"][0].__setitem__(
            "declared_scope", ["unknown:scope"]
        ),
        "effect": lambda values, _: values["tools"]["tools"][0].__setitem__(
            "effects", ["delete-all-data"]
        ),
    }
    for name, mutate in cases.items():
        status, errors = _case(tmp_path / name, mutate)
        assert status == "BOUND_INPUTS_INCOMPLETE", (name, status, errors)
        assert any("schema" in message for message in errors)
