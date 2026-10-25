#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Issue signed Agent Trust Passports for an agent fleet from a policy file, with no manual step.

The operator's automation runs this. It reads a fleet policy (agents, tools, Action Levels,
parent links), then writes, for every agent:

- a canonical assessment bundle under the Alpha.1 reference profile (inventories, action-authority
  graph, assessment, synthetic data-authority evidence, bundle manifest);
- a passport signed with the operator's Ed25519 key;
- for an agent with a parent, a sub-agent passport binding for Agent Fleet Controls.

It also writes the trusted-key record and a signed cumulative revocation list, then validates
every passport with the reference validator at the issue time. Exit 0 only when all are VALID.

Scope, stated plainly: the Alpha.1 reference profile is non-production (production_use false),
and its data-authority adapter is synthetic. A passport issued here is VALID under that profile;
it is not a certification, and verification is not authorization (authority_effect NONE).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tools.canonical_json import canonicalize
from tools.crypto import b64d, b64e, jwk_thumbprint_kid
from tools.fleet_controls import binding_id as fleet_binding_id
from tools.reference_policy import (
    AGENT_CAPABILITY_MIN_LEVEL,
    CURRENT_ASSESSMENT_POLICY_ID,
    CURRENT_ASSESSMENT_POLICY_VERSION,
    CURRENT_EVALUATOR_ID,
    CURRENT_EVALUATOR_VERSION,
    CURRENT_FRAMEWORK_ID,
    CURRENT_FRAMEWORK_VERSION,
    CURRENT_PROFILE_ID,
    CURRENT_PROFILE_VERSION,
    CURRENT_SCHEMA_VERSION,
    TOOL_EFFECT_MIN_LEVEL,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY_KIND = "global-ai-governance.fleet-issuance-policy"
POLICY_VERSION = "0.1.0"
FLEET_VERSION = "0.1.0-alpha.4"
ACTION_TERMS = ("install_tool", "network_call", "provision_compute", "spawn_agent", "spend_funds")
DEFAULT_EFFECT = {0: "read-only", 1: "read-only", 2: "draft-internal-content", 3: "execute-code", 4: "publish-externally"}
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MEDIA = {
    "graph": "application/agentic-ai-action-authority+json",
    "assessment": "application/agentic-ai-assessment+json",
    "evidence": "application/agentic-ai-data-authority+json",
    "agent": "application/agent-inventory+json",
    "mcp": "application/mcp-inventory+json",
    "tools": "application/tool-inventory+json",
    "descriptor": "application/agentic-ai-control-profile-descriptor+json",
    "profile": "application/agentic-ai-control-profile+markdown",
}


class IssuanceError(ValueError):
    """The fleet policy cannot be issued as written."""


# --------------------------------------------------------------------------- helpers
def fmt(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime(TIME_FORMAT)


def parse(value: str) -> datetime:
    return datetime.strptime(value, TIME_FORMAT).replace(tzinfo=timezone.utc)


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def domain_id(domain: str, label: str, value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize({"domain": domain, label: value})).hexdigest()


def jcs_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize(value)).hexdigest()


def write_json(path: Path, value: Any, *, private: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if private:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
    else:
        path.write_text(data, encoding="utf-8")
    return path


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- keys and signing
def generate_signing_key(issuer_id: str) -> dict[str, Any]:
    private = Ed25519PrivateKey.generate()
    seed = private.private_bytes_raw()
    x = b64e(private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))
    jwk = {"kty": "OKP", "crv": "Ed25519", "x": x}
    return {"issuer_id": issuer_id, "kid": jwk_thumbprint_kid(jwk), "jwk": {**jwk, "d": b64e(seed)}}


def _private_key(signing_key: dict[str, Any]) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(b64d(signing_key["jwk"]["d"]))


def trusted_key_record(signing_key: dict[str, Any], not_before: datetime, expires_at: datetime) -> dict[str, Any]:
    jwk = signing_key["jwk"]
    return {
        "issuer_id": signing_key["issuer_id"],
        "kid": signing_key["kid"],
        "jwk": {"kty": "OKP", "crv": "Ed25519", "x": jwk["x"], "alg": "Ed25519", "use": "sig", "key_ops": ["verify"]},
        "not_before": fmt(not_before),
        "expires_at": fmt(expires_at),
        "status": "ACTIVE",
        "allowed_algorithms": ["Ed25519"],
    }


def sign_document(document: dict[str, Any], signing_key: dict[str, Any], *, typ: str, cty: str) -> dict[str, Any]:
    value = {key: item for key, item in document.items() if key != "proof"}
    header = {"alg": "Ed25519", "cty": cty, "kid": signing_key["kid"], "typ": typ}
    protected = b64e(canonicalize(header))
    payload = b64e(canonicalize(value))
    signature = _private_key(signing_key).sign((protected + "." + payload).encode("ascii"))
    value["proof"] = {"jws": protected + ".." + b64e(signature)}
    return value


# --------------------------------------------------------------------------- policy
def load_policy(policy: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, dict) or policy.get("policy_kind") != POLICY_KIND:
        raise IssuanceError(f"policy_kind must be {POLICY_KIND!r}")
    issuer = policy.get("issuer_id")
    if not isinstance(issuer, str) or not issuer:
        raise IssuanceError("issuer_id is required")
    agents = policy.get("agents")
    if not isinstance(agents, list) or not agents:
        raise IssuanceError("agents must be a non-empty list")
    by_id: dict[str, dict[str, Any]] = {}
    for raw in agents:
        agent = deepcopy(raw)
        agent_id = agent.get("agent_id")
        if not isinstance(agent_id, str) or agent_id in by_id:
            raise IssuanceError(f"agent_id missing or duplicated: {agent_id!r}")
        level = agent.get("maximum_action_level")
        if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 4:
            raise IssuanceError(f"{agent_id}: maximum_action_level must be 1-4 (Level 5 is never issued)")
        terms = agent.setdefault("action_terms", [])
        if not set(terms) <= set(ACTION_TERMS) or "spend_funds" in terms:
            raise IssuanceError(f"{agent_id}: action_terms must come from {ACTION_TERMS[:-1]}")
        if terms and level < 4:
            raise IssuanceError(f"{agent_id}: fleet action terms need maximum_action_level 4")
        if agent.get("delegates") and level < 3:
            raise IssuanceError(f"{agent_id}: an agent that delegates needs maximum_action_level 3 or more")
        tools = agent.setdefault("tools", [])
        for tool in tools:
            tool_level = tool.get("action_level")
            if not isinstance(tool_level, int) or not 0 <= tool_level <= level:
                raise IssuanceError(f"{agent_id}: tool {tool.get('tool_id')!r} level must be 0..{level}")
            tool.setdefault("effects", [DEFAULT_EFFECT[tool_level]])
            if any(TOOL_EFFECT_MIN_LEVEL.get(e, 9) > tool_level for e in tool["effects"]):
                raise IssuanceError(f"{agent_id}: tool {tool['tool_id']!r} effects need a higher level")
        caps = agent.setdefault("capabilities", ["read:approved-public-information"])
        if any(AGENT_CAPABILITY_MIN_LEVEL.get(c, 9) > level for c in caps):
            raise IssuanceError(f"{agent_id}: capabilities need a higher level")
        by_id[agent_id] = agent
    for agent in by_id.values():
        parent = agent.get("parent")
        if parent is None:
            continue
        if parent not in by_id:
            raise IssuanceError(f"{agent['agent_id']}: parent {parent!r} is not in the policy")
        p = by_id[parent]
        if agent["maximum_action_level"] > p["maximum_action_level"]:
            raise IssuanceError(f"{agent['agent_id']}: level exceeds parent {parent}")
        if not set(agent["action_terms"]) <= set(p["action_terms"]):
            raise IssuanceError(f"{agent['agent_id']}: action terms exceed parent {parent}")
    return {**policy, "agents": list(by_id.values())}


def depth_of(agent_id: str, by_id: dict[str, dict[str, Any]]) -> int:
    depth, seen, current = 0, set(), by_id[agent_id]
    while current.get("parent"):
        if current["agent_id"] in seen:
            raise IssuanceError("parent links form a cycle")
        seen.add(current["agent_id"])
        current = by_id[current["parent"]]
        depth += 1
    return depth


# --------------------------------------------------------------------------- bundle and passport
def _bundle_files(agent: dict[str, Any], issuer_id: str, at: datetime, not_before: datetime,
                  expires_at: datetime) -> dict[str, Any]:
    agent_id, level = agent["agent_id"], agent["maximum_action_level"]
    tools = sorted(agent["tools"], key=lambda t: t["tool_id"])
    server_id = agent.get("mcp_server_id", "mcp." + agent_id + ".tools")
    data_use = {"data_classes": ["SYNTHETIC"], "purposes": ["conformance-testing"],
                "systems": ["synthetic.fixture"], "jurisdictions": ["TEST"]}
    agent_inv = {"schema_version": CURRENT_SCHEMA_VERSION, "inventory_type": "agent", "agent_id": agent_id,
                 "declared_capabilities": sorted(agent["capabilities"]), "production_use": False, "data_use": data_use}
    mcp_inv = {"schema_version": CURRENT_SCHEMA_VERSION, "inventory_type": "mcp", "agent_id": agent_id,
               "servers": [{"server_id": server_id, "transport": "stdio", "declared_scope": ["public-information:read"]}],
               "production_use": False}
    tool_inv = {"schema_version": CURRENT_SCHEMA_VERSION, "inventory_type": "tool", "agent_id": agent_id,
                "tools": [{"tool_id": t["tool_id"], "action_level": t["action_level"], "effects": t["effects"]}
                          for t in tools], "production_use": False}
    nodes = [{"node_id": agent_id, "node_type": "AGENT", "base_level": level},
             {"node_id": server_id, "node_type": "MCP_SERVER", "base_level": 1}]
    edges = [{"from": agent_id, "to": server_id, "edge_type": "INVOKES"}]
    for tool in tools:
        nodes.append({"node_id": tool["tool_id"], "node_type": "TOOL", "base_level": tool["action_level"]})
        edges.append({"from": server_id, "to": tool["tool_id"], "edge_type": "INVOKES"})
    dimensions = {"delegation": bool(agent.get("delegates")), "unattended": False, "code_execution": False,
                  "credential_change": False, "identity_change": False, "external_publication": False,
                  "data_movement": False, "self_modification": False, "reversibility": "FULL", "blast_radius": "LOCAL"}
    graph = {"schema_version": CURRENT_SCHEMA_VERSION, "agent_id": agent_id, "requested_level": level,
             "computed_level": level, "dimensions": dimensions, "nodes": nodes, "edges": edges}
    evidence_id = "evidence.data-authority.synthetic"
    evidence = {"evidence_id": evidence_id, "evidence_type": "data_authority",
                "scheme": "global-ai-governance.synthetic-authority", "scheme_version": "0.1.0",
                "issuer_id": "global-ai-governance.test-issuer", "artifact_hash": "",
                "scope": {**deepcopy(data_use), "prohibited_uses": ["production-use"]},
                "validity": {"not_before": fmt(not_before), "expires_at": fmt(expires_at)},
                "subject": {"agent_id": agent_id}}
    evidence["artifact_hash"] = domain_id("global-ai-governance.data-authority-evidence.artifact.v1", "evidence",
                                          {k: v for k, v in evidence.items() if k != "artifact_hash"})
    assessment = {"schema_version": CURRENT_SCHEMA_VERSION, "assessment_id": "", "evaluated_at": fmt(at),
                  "data_authority_status": "VERIFIED", "result": "APPROVED",
                  "assurance": {"evidence_basis": "DECLARED", "validation_method": "STRUCTURAL",
                                "attestation_status": "NONE"},
                  "requested_action_level": level, "maximum_action_level": level,
                  "control_results": [{"control_id": "AID-001", "outcome": "PASS", "applicable": True,
                                       "evidence_refs": [evidence_id], "findings": []}],
                  "conditions": []}
    assessment["assessment_id"] = domain_id("global-ai-governance.agentic-assessment.identifier.v1", "assessment",
                                            {k: v for k, v in assessment.items() if k != "assessment_id"})
    return {"graph": graph, "assessment": assessment, "evidence": evidence, "agent": agent_inv,
            "mcp": mcp_inv, "tools": tool_inv}


BUNDLE_PATHS = {
    "graph": "action-authority.json", "assessment": "assessment.json", "evidence": "data-authority.json",
    "agent": "inventories/agent.json", "mcp": "inventories/mcp.json", "tools": "inventories/tools.json",
    "descriptor": "profiles/mcp-governance-profile.json", "profile": "profiles/mcp-governance-profile.md",
}


def write_bundle(agent: dict[str, Any], bundle_root: Path, issuer_id: str, at: datetime, not_before: datetime,
                 expires_at: datetime) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    values = _bundle_files(agent, issuer_id, at, not_before, expires_at)
    for name, value in values.items():
        write_json(bundle_root / BUNDLE_PATHS[name], value)
    (bundle_root / "profiles").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "profiles/mcp-governance-profile.json", bundle_root / BUNDLE_PATHS["descriptor"])
    shutil.copyfile(ROOT / "profiles/mcp-governance-profile.md", bundle_root / BUNDLE_PATHS["profile"])
    entries = []
    for name in sorted(BUNDLE_PATHS, key=lambda n: BUNDLE_PATHS[n]):
        path = bundle_root / BUNDLE_PATHS[name]
        exact = name == "profile"
        digest = ("sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()) if exact else jcs_hash(read_json(path))
        entries.append({"path": BUNDLE_PATHS[name], "media_type": MEDIA[name], "size_bytes": path.stat().st_size,
                        "hash": digest, "canonicalization": "EXACT_BYTES" if exact else "JCS"})
    manifest = {"schema_version": CURRENT_SCHEMA_VERSION, "bundle_id": "", "files": entries}
    manifest["bundle_id"] = domain_id("global-ai-governance.agentic-assessment-bundle.identifier.v1", "manifest",
                                      {k: v for k, v in manifest.items() if k != "bundle_id"})
    descriptor = read_json(bundle_root / BUNDLE_PATHS["descriptor"])
    return values, manifest, descriptor


def build_passport(agent: dict[str, Any], issuer_id: str, values: dict[str, Any], manifest: dict[str, Any],
                   descriptor: dict[str, Any], not_before: datetime, expires_at: datetime,
                   signing_key: dict[str, Any]) -> dict[str, Any]:
    by_media = {item["media_type"]: item["hash"] for item in manifest["files"]}
    assessment = values["assessment"]
    counts = {name: 0 for name in ("PASS", "FAIL", "NOT_APPLICABLE", "NOT_EVALUATED", "ERROR")}
    for control in assessment["control_results"]:
        counts[control["outcome"]] += 1
    passport = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "framework": {"id": CURRENT_FRAMEWORK_ID, "version": CURRENT_FRAMEWORK_VERSION},
        "profile": {"id": descriptor.get("profile_id", CURRENT_PROFILE_ID),
                    "version": descriptor.get("profile_version", CURRENT_PROFILE_VERSION)},
        "passport_id": "",
        "issuer": {"issuer_id": issuer_id},
        "subject": {"agent_id": agent["agent_id"], "display_name": agent.get("display_name", agent["agent_id"])},
        "issued_assessment": {
            "result": assessment["result"], "evaluated_at": assessment["evaluated_at"], "control_summary": counts,
            "maximum_action_level": assessment["maximum_action_level"], "assessment_id": assessment["assessment_id"],
            "data_authority_status": assessment["data_authority_status"],
        },
        "assurance": {"evidence_basis": "DECLARED", "validation_method": "STRUCTURAL",
                      "attestation_status": "ISSUER_SIGNED"},
        "bindings": {
            "assessment_bundle": manifest["bundle_id"],
            "agent_inventory": by_media[MEDIA["agent"]],
            "mcp_inventory": by_media[MEDIA["mcp"]],
            "tool_inventory": by_media[MEDIA["tools"]],
            "control_profile": by_media[MEDIA["profile"]],
            "data_authority_evidence": [by_media[MEDIA["evidence"]]],
            "evaluator_version": CURRENT_EVALUATOR_VERSION,
            "assessment_policy_version": CURRENT_ASSESSMENT_POLICY_VERSION,
            "action_authority_graph": by_media[MEDIA["graph"]],
            "control_profile_descriptor": by_media[MEDIA["descriptor"]],
            "evaluator_id": CURRENT_EVALUATOR_ID,
            "assessment_policy_id": CURRENT_ASSESSMENT_POLICY_ID,
        },
        "validity": {"not_before": fmt(not_before), "expires_at": fmt(expires_at)},
        "conditions": [],
        "extensions": {},
        "critical_extensions": [],
    }
    passport["passport_id"] = domain_id("global-ai-governance.agent-trust-passport.identifier.v1", "passport",
                                        {k: v for k, v in passport.items() if k != "passport_id"})
    return sign_document(passport, signing_key, typ="atp+jws", cty="application/agent-trust-passport+json")


def build_binding(agent: dict[str, Any], parent: dict[str, Any], depth: int, child_passport: dict[str, Any],
                  parent_passport: dict[str, Any]) -> dict[str, Any]:
    binding = {
        "binding_kind": "global-ai-governance.sub-agent-passport-binding",
        "binding_version": FLEET_VERSION,
        "binding_id": "",
        "child_passport_id": child_passport["passport_id"],
        "child_subject_id": agent["agent_id"],
        "parent_passport_id": parent_passport["passport_id"],
        "issued_by": parent["agent_id"],
        "delegation_depth": depth,
        "maximum_action_level": agent["maximum_action_level"],
        "action_terms": sorted(agent["action_terms"]),
        "not_before": child_passport["validity"]["not_before"],
        "expires_at": child_passport["validity"]["expires_at"],
    }
    binding["binding_id"] = fleet_binding_id(binding)
    return binding


# --------------------------------------------------------------------------- revocation list
def revocation_entry(passport_id: str, issuer_id: str, at: datetime, reason_code: str, reason: str) -> dict[str, Any]:
    entry = {"passport_id": passport_id, "framework": CURRENT_FRAMEWORK_ID, "revoked_at": fmt(at),
             "reason_code": reason_code, "reason": reason, "superseding_passport_id": None, "authority": issuer_id}
    entry["revocation_id"] = domain_id("global-ai-governance.agent-trust-passport.revocation-entry.identifier.v1",
                                       "entry", entry)
    return entry


def sign_revocation_list(signing_key: dict[str, Any], entries: list[dict[str, Any]], at: datetime, sequence: int,
                         previous_list_hash: str | None, lifetime: timedelta) -> dict[str, Any]:
    value = {"schema_version": CURRENT_SCHEMA_VERSION, "framework": CURRENT_FRAMEWORK_ID, "list_id": "",
             "issuer_id": signing_key["issuer_id"], "sequence_number": sequence, "issued_at": fmt(at),
             "next_update": fmt(at + lifetime), "previous_list_hash": previous_list_hash,
             "entries": sorted(entries, key=lambda e: (e["passport_id"], e["revocation_id"]))}
    value["list_id"] = domain_id("global-ai-governance.agent-trust-passport.revocation-list.identifier.v1", "list",
                                 {k: v for k, v in value.items() if k not in {"list_id", "proof"}})
    return sign_document(value, signing_key, typ="atp-revocation+jws", cty="application/agent-revocation-list+json")


# --------------------------------------------------------------------------- validation
def validate(passport_path: Path, key_path: Path, revocation_path: Path, manifest_path: Path, bundle_root: Path,
             at: datetime) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools/validate_artifact.py"), "--kind", "passport",
         "--trusted-key", str(key_path), "--revocation-list", str(revocation_path),
         "--bundle-manifest", str(manifest_path), "--bundle-root", str(bundle_root),
         "--at-time", fmt(at), str(passport_path)],
        capture_output=True, text=True, check=False)
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        report = {"verification_primary_status": "ERROR", "stderr": completed.stderr[-500:]}
    return report


# --------------------------------------------------------------------------- fleet issuance
def issue_fleet(policy: dict[str, Any], out: Path, *, at: datetime | None = None,
                signing_key: dict[str, Any] | None = None, check: bool = True) -> dict[str, Any]:
    policy = load_policy(policy)
    at = at or now_utc()
    issuer_id = policy["issuer_id"]
    validity = timedelta(days=int(policy.get("validity_days", 30)))
    lifetime = timedelta(hours=int(policy.get("revocation_refresh_hours", 24)))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    key_path = out / "signing-key.json"
    if signing_key is None:
        signing_key = read_json(key_path) if key_path.exists() else generate_signing_key(issuer_id)
    if signing_key.get("issuer_id") != issuer_id:
        raise IssuanceError("the signing key belongs to a different issuer_id")
    write_json(key_path, signing_key, private=True)
    trusted_path = write_json(out / "trusted-key.json",
                              trusted_key_record(signing_key, at - timedelta(minutes=5), at + validity + timedelta(days=1)))
    by_id = {a["agent_id"]: a for a in policy["agents"]}
    order = sorted(by_id, key=lambda a: (depth_of(a, by_id), a))
    issued: dict[str, dict[str, Any]] = {}
    agents_out: list[dict[str, Any]] = []
    for agent_id in order:
        agent = by_id[agent_id]
        depth = depth_of(agent_id, by_id)
        not_before, expires_at = at, at + validity
        if agent.get("parent"):
            parent_passport = issued[agent["parent"]]
            expires_at = min(expires_at, parse(parent_passport["validity"]["expires_at"]))
        folder = out / "agents" / agent_id
        values, manifest, descriptor = write_bundle(agent, folder / "bundle", issuer_id, at, not_before, expires_at)
        manifest_path = write_json(folder / "bundle-manifest.json", manifest)
        passport = build_passport(agent, issuer_id, values, manifest, descriptor, not_before, expires_at, signing_key)
        passport_path = write_json(folder / "passport.json", passport)
        issued[agent_id] = passport
        record = {"agent_id": agent_id, "passport_id": passport["passport_id"], "parent": agent.get("parent"),
                  "delegation_depth": depth, "maximum_action_level": agent["maximum_action_level"],
                  "action_terms": sorted(agent["action_terms"]),
                  "passport": str(passport_path.relative_to(out)),
                  "bundle_manifest": str(manifest_path.relative_to(out)),
                  "bundle_root": str((folder / "bundle").relative_to(out))}
        if agent.get("parent"):
            binding = build_binding(agent, by_id[agent["parent"]], depth, passport, issued[agent["parent"]])
            record["binding"] = str(write_json(folder / "sub-agent-binding.json", binding).relative_to(out))
        agents_out.append(record)
    revocation = sign_revocation_list(signing_key, [], at, 1, None, lifetime)
    revocation_path = write_json(out / "revocation-list.json", revocation)
    fleet = {"fleet_kind": "global-ai-governance.issued-fleet", "fleet_version": POLICY_VERSION,
             "issuer_id": issuer_id, "issued_at": fmt(at), "trusted_key": "trusted-key.json",
             "revocation_list": "revocation-list.json", "agents": agents_out, "authority_effect": "NONE"}
    if check:
        for record in agents_out:
            report = validate(out / record["passport"], trusted_path, revocation_path, out / record["bundle_manifest"],
                              out / record["bundle_root"], at)
            record["verification_primary_status"] = report.get("verification_primary_status")
    write_json(out / "fleet.json", fleet)
    return fleet


def revoke(out: Path, passport_id: str, *, at: datetime | None = None, reason_code: str = "OTHER",
           reason: str = "Revoked by the operator's fleet automation.") -> dict[str, Any]:
    out = Path(out)
    at = at or now_utc()
    signing_key = read_json(out / "signing-key.json")
    current = read_json(out / "revocation-list.json")
    if passport_id in {e["passport_id"] for e in current["entries"]}:
        return current
    lifetime = parse(current["next_update"]) - parse(current["issued_at"])
    entries = [*current["entries"], revocation_entry(passport_id, signing_key["issuer_id"], at, reason_code, reason)]
    updated = sign_revocation_list(signing_key, entries, at, current["sequence_number"] + 1, current["list_id"], lifetime)
    write_json(out / "revocation-list.json", updated)
    return updated


def refresh(out: Path, *, at: datetime | None = None) -> dict[str, Any]:
    """Re-sign the current revocation list with a new issue time so it stays fresh."""
    out = Path(out)
    at = at or now_utc()
    signing_key = read_json(out / "signing-key.json")
    current = read_json(out / "revocation-list.json")
    lifetime = parse(current["next_update"]) - parse(current["issued_at"])
    updated = sign_revocation_list(signing_key, current["entries"], at, current["sequence_number"] + 1,
                                   current["list_id"], lifetime)
    write_json(out / "revocation-list.json", updated)
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="issue-passports", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_issue = sub.add_parser("issue", help="Issue and validate passports for every agent in a fleet policy.")
    p_issue.add_argument("policy", help="Fleet issuance policy JSON.")
    p_issue.add_argument("--out", required=True, help="Output directory (holds the private signing key, mode 0600).")
    p_issue.add_argument("--at-time", help="Issue time, YYYY-MM-DDTHH:MM:SSZ. Defaults to now.")
    p_revoke = sub.add_parser("revoke", help="Add a passport to the signed revocation list.")
    p_revoke.add_argument("passport_id")
    p_revoke.add_argument("--out", required=True)
    p_revoke.add_argument("--reason-code", default="OTHER")
    p_revoke.add_argument("--at-time")
    p_refresh = sub.add_parser("refresh", help="Re-sign the revocation list so it stays fresh.")
    p_refresh.add_argument("--out", required=True)
    p_refresh.add_argument("--at-time")
    args = parser.parse_args(argv)
    at = parse(args.at_time) if getattr(args, "at_time", None) else None
    try:
        if args.command == "issue":
            fleet = issue_fleet(read_json(Path(args.policy)), Path(args.out), at=at)
            print(json.dumps(fleet, indent=2))
            return 0 if all(a.get("verification_primary_status") == "VALID" for a in fleet["agents"]) else 1
        if args.command == "revoke":
            print(json.dumps(revoke(Path(args.out), args.passport_id, at=at, reason_code=args.reason_code), indent=2))
            return 0
        print(json.dumps(refresh(Path(args.out), at=at), indent=2))
        return 0
    except (IssuanceError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
