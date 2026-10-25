#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reference lead agent / orchestrator that governs an agent fleet with no manual step.

What it does, all in one process and offline by default:

- issues a signed Agent Trust Passport for itself and for every sub-agent it spawns
  (tools/issue_passports.py), each sub-agent bound to its parent by a sub-agent passport binding;
- sends every tool call through one guard: passport VALID at this clock, no revoked or suspended
  passport in the lineage, the tool's Action Level within the passport ceiling, Agent Fleet Controls
  PERMITTED for fleet actions (spawn, network), then Levels 0-3 run, Level 4 goes to the approver the
  operator's policy names (a person by default), and Level 5 is always denied;
- caps delegation depth (Agent Fleet Controls profile: 3);
- suspends, reinstates and revokes passports, with the effect cascading to every descendant;
- runs shutdown tests (suspend the root, confirm every agent stops, reinstate, confirm they resume);
- records every decision in a hash-chained audit ledger that anyone can re-verify.

The model is pluggable. The default is a deterministic offline planner (no key, no network). With
LEAD_AGENT_PROVIDER set to openai, anthropic or xai and the matching API key in the environment, the
planner asks that provider for a plan instead; keys are read from the environment only and sent only
to the chosen provider. The tools are synthetic stand-ins: nothing outside this process is touched.

Every result is non-authorizing (authority_effect NONE). A guard "allow" means no check stopped the
call; it is not an approval of the work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import threading
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import issue_passports as issuer  # noqa: E402
from tools.canonical_json import canonicalize  # noqa: E402
from tools.fleet_controls import evaluate as fleet_evaluate, suspension_list_id  # noqa: E402

VERSION = "0.1.0"
ALLOW, ASK, DENY, APPROVED = "allow", "ask", "deny", "approved"
UNKNOWN_TOOL_LEVEL = 4
MAX_DEPTH = 3
LEAD_ID = "agent.lead"

# Operator policy: the Action Level of every tool, which fleet action term it uses, and who approves
# Level 4. Level 5 is always denied and is not configurable here.
DEFAULT_POLICY: dict[str, Any] = {
    "tools": {
        "search_notes": {"level": 1, "description": "Search synthetic notes"},
        "draft_text": {"level": 2, "description": "Draft internal text"},
        "run_analysis": {"level": 3, "description": "Run a bounded, logged, reversible analysis"},
        "fetch_url": {"level": 4, "term": "network_call", "description": "Fetch a page (simulated)"},
        "spawn_agent": {"level": 4, "term": "spawn_agent", "description": "Start a governed sub-agent"},
        "publish_external": {"level": 4, "description": "Publish outside the organization (simulated)"},
        "spend_funds": {"level": 5, "term": "spend_funds", "description": "Spend money (simulated)"},
        "delete_records": {"level": 5, "description": "Delete records (simulated)"},
    },
    "level_4_approver": {
        "mode": "automated",
        "approver_id": "operator.fleet-approver",
        "rules": [
            {"tool": "spawn_agent"},
            {"tool": "fetch_url", "targets": ["docs.example.org", "data.example.org"]},
        ],
        "otherwise": "person",
    },
}

ROLES = {
    "research": {"display_name": "Research sub-agent", "tools": ["search_notes", "fetch_url", "spawn_agent"],
                 "level": 4, "terms": ["network_call", "spawn_agent"]},
    "writer": {"display_name": "Writing sub-agent", "tools": ["draft_text", "publish_external"],
               "level": 4, "terms": []},
    "analyst": {"display_name": "Analysis sub-agent", "tools": ["run_analysis", "search_notes"],
                "level": 3, "terms": []},
    "procurement": {"display_name": "Procurement sub-agent", "tools": ["search_notes", "spend_funds"],
                    "level": 4, "terms": ["network_call"]},
}


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def fmt(value: datetime) -> str:
    return issuer.fmt(value)


def sha(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize(value)).hexdigest()


# --------------------------------------------------------------------------- audit ledger
class Ledger:
    """Append-only, hash-chained audit ledger. Same record format as the browser app."""

    KIND = "global-ai-governance.lead-agent-audit"

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def append(self, at: str, event: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            prev = self.records[-1]["hash"] if self.records else None
            record = {"seq": len(self.records) + 1, "at": at, "event": event, "prev": prev}
            record["hash"] = sha(record)
            self.records.append(record)
            return record

    def export(self) -> dict[str, Any]:
        return {"ledger_kind": self.KIND, "ledger_version": VERSION, "records": list(self.records),
                "head": self.records[-1]["hash"] if self.records else None, "authority_effect": "NONE"}

    @staticmethod
    def verify(document: dict[str, Any]) -> tuple[bool, str]:
        records = document.get("records")
        if document.get("ledger_kind") != Ledger.KIND or not isinstance(records, list):
            return False, "not a lead-agent audit ledger"
        prev = None
        for index, record in enumerate(records, start=1):
            body = {k: v for k, v in record.items() if k != "hash"}
            if record.get("seq") != index or record.get("prev") != prev:
                return False, f"record {index}: sequence or chain link broken"
            if sha(body) != record.get("hash"):
                return False, f"record {index}: hash does not match its content"
            prev = record["hash"]
        if document.get("head") != prev:
            return False, "head does not match the last record"
        return True, f"{len(records)} records verified"


# --------------------------------------------------------------------------- models
class MockModel:
    """Deterministic offline planner: the same goal always gives the same plan."""

    name = "mock (deterministic, offline)"

    def plan(self, goal: str) -> list[dict[str, Any]]:
        text = goal.lower()
        steps: list[dict[str, Any]] = []
        target = "docs.example.org"
        match = re.search(r"\b((?:[a-z0-9-]+\.)+(?:org|com|net|io|dev|ai|solutions))\b", text)
        if match:
            target = match.group(1)
        if re.search(r"research|find|look up|investigate|compare|learn", text):
            steps += [{"role": "research", "tool": "search_notes", "args": {"query": goal[:80]}},
                      {"role": "research", "tool": "fetch_url", "args": {"target": target}}]
        if re.search(r"deep|nested|delegate further|sub-sub|chain", text):
            steps += [{"role": "research", "tool": "spawn_agent", "args": {"role": "research"}, "nested": 3}]
        if re.search(r"analy|calculate|model|forecast", text):
            steps += [{"role": "analyst", "tool": "run_analysis", "args": {"topic": goal[:60]}}]
        if re.search(r"write|draft|summar|report|plan", text):
            steps += [{"role": "writer", "tool": "draft_text", "args": {"topic": goal[:60]}}]
        if re.search(r"publish|post|email|send|announce", text):
            steps += [{"role": "writer", "tool": "publish_external", "args": {"channel": "public-site"}}]
        if re.search(r"buy|pay|spend|purchase|order|\$\d", text):
            steps += [{"role": "procurement", "tool": "spend_funds", "args": {"amount_usd": 500}}]
        if re.search(r"delete|wipe|erase|destroy", text):
            steps += [{"role": "analyst", "tool": "delete_records", "args": {"scope": "all"}}]
        if not steps:
            steps = [{"role": "research", "tool": "search_notes", "args": {"query": goal[:80]}},
                     {"role": "writer", "tool": "draft_text", "args": {"topic": goal[:60]}}]
        return steps


PLAN_INSTRUCTIONS = (
    "You are a lead agent planner. Reply with JSON only: {\"steps\": [{\"role\": R, \"tool\": T, \"args\": {}}]}. "
    "Roles: research, writer, analyst, procurement. Tools: search_notes, fetch_url, run_analysis, draft_text, "
    "publish_external, spend_funds, delete_records. Use at most 6 steps."
)

PROVIDERS = {
    "openai": {"env": "OPENAI_API_KEY", "base": "https://api.openai.com/v1", "model": "gpt-4.1-mini", "style": "chat"},
    "xai": {"env": "XAI_API_KEY", "base": "https://api.x.ai/v1", "model": "grok-4", "style": "chat"},
    "anthropic": {"env": "ANTHROPIC_API_KEY", "base": "https://api.anthropic.com/v1", "model": "claude-sonnet-4-5",
                  "style": "messages"},
}


class ProviderModel:
    """OpenAI-, xAI- (OpenAI-compatible) or Anthropic-compatible planner. The key comes from the environment."""

    def __init__(self, provider: str, *, base_url: str | None = None, model: str | None = None,
                 opener: Callable[..., Any] = urllib.request.urlopen) -> None:
        spec = PROVIDERS[provider]
        self.provider, self.style = provider, spec["style"]
        self.key = os.environ.get(spec["env"], "")
        if not self.key:
            raise RuntimeError(f"{spec['env']} is not set")
        self.base = (base_url or os.environ.get("LEAD_AGENT_BASE_URL") or spec["base"]).rstrip("/")
        self.model = model or os.environ.get("LEAD_AGENT_MODEL") or spec["model"]
        self.name = f"{provider}:{self.model}"
        self._open = opener

    def request(self, goal: str) -> urllib.request.Request:
        if self.style == "chat":
            body = {"model": self.model, "messages": [{"role": "system", "content": PLAN_INSTRUCTIONS},
                                                      {"role": "user", "content": goal}],
                    "response_format": {"type": "json_object"}}
            headers = {"Authorization": f"Bearer {self.key}"}
            url = self.base + "/chat/completions"
        else:
            body = {"model": self.model, "max_tokens": 800, "system": PLAN_INSTRUCTIONS,
                    "messages": [{"role": "user", "content": goal}]}
            headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01"}
            url = self.base + "/messages"
        return urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                      headers={"Content-Type": "application/json", **headers})

    def plan(self, goal: str) -> list[dict[str, Any]]:
        with self._open(self.request(goal), timeout=60) as response:
            payload = json.loads(response.read().decode())
        if self.style == "chat":
            text = payload["choices"][0]["message"]["content"]
        else:
            text = "".join(part.get("text", "") for part in payload.get("content", []))
        match = re.search(r"\{.*\}", text, re.S)
        steps = json.loads(match.group(0) if match else text).get("steps", [])
        clean = []
        for step in steps[:6]:
            if isinstance(step, dict) and step.get("role") in ROLES and isinstance(step.get("tool"), str):
                clean.append({"role": step["role"], "tool": step["tool"], "args": step.get("args") or {}})
        return clean


def model_from_env() -> Any:
    provider = os.environ.get("LEAD_AGENT_PROVIDER", "").strip().lower()
    return ProviderModel(provider) if provider else MockModel()


# --------------------------------------------------------------------------- synthetic tools
def run_tool(tool: str, args: dict[str, Any]) -> str:
    if tool == "search_notes":
        return f"3 synthetic notes match {str(args.get('query', ''))[:40]!r}"
    if tool == "fetch_url":
        return f"Fetched a synthetic page from {args.get('target')} (simulated; no network call)"
    if tool == "run_analysis":
        return "Analysis complete on synthetic data (bounded, logged, reversible)"
    if tool == "draft_text":
        return f"Drafted an internal summary on {str(args.get('topic', ''))[:40]!r}"
    if tool == "publish_external":
        return "Published (simulated)"
    return "Done (simulated)"


# --------------------------------------------------------------------------- the orchestrator
class LeadAgent:
    def __init__(self, workdir: Path | None = None, policy: dict[str, Any] | None = None, model: Any = None,
                 clock: Callable[[], datetime] = now_utc) -> None:
        self._tmp = None
        if workdir is None:
            self._tmp = tempfile.TemporaryDirectory(prefix="lead-agent-")
            workdir = Path(self._tmp.name)
        self.workdir = Path(workdir)
        self.policy = json.loads(json.dumps(policy or DEFAULT_POLICY))
        self.model = model or MockModel()
        self.clock = clock
        self.ledger = Ledger()
        self.lock = threading.RLock()
        self.agents: dict[str, dict[str, Any]] = {}
        self.suspensions: dict[str, dict[str, Any]] = {}
        self.pending: list[dict[str, Any]] = []
        self.counter = 0
        self._validity: dict[tuple[str, int], str] = {}
        self.issuer_id = "operator.lead-agent.issuer"
        self.out = self.workdir / "fleet"
        self.out.mkdir(parents=True, exist_ok=True)
        self.signing_key = issuer.generate_signing_key(self.issuer_id)
        issuer.write_json(self.out / "signing-key.json", self.signing_key, private=True)
        at = self.clock()
        issuer.write_json(self.out / "trusted-key.json",
                          issuer.trusted_key_record(self.signing_key, at - timedelta(minutes=5), at + timedelta(days=31)))
        issuer.write_json(self.out / "revocation-list.json",
                          issuer.sign_revocation_list(self.signing_key, [], at, 1, None, timedelta(hours=24)))
        self._record("fleet_started", {"issuer_id": self.issuer_id, "model": self.model.name,
                                       "delegation_max_depth": MAX_DEPTH,
                                       "level_4_approver": self.policy["level_4_approver"].get("mode", "person")})
        self._issue(LEAD_ID, "Lead agent", None, 4, ["network_call", "spawn_agent"],
                    ["search_notes", "draft_text", "spawn_agent", "fetch_url"])

    # ----- records and status
    def _record(self, kind: str, data: dict[str, Any]) -> dict[str, Any]:
        return self.ledger.append(fmt(self.clock()), {"kind": kind, **data})

    def _revocation(self) -> dict[str, Any]:
        refreshed = issuer.refresh(self.out, at=self.clock())
        return refreshed

    def _suspension_list(self, at: datetime) -> dict[str, Any]:
        value = {"list_kind": "global-ai-governance.passport-suspension-list", "list_version": "0.1.0-alpha.4",
                 "list_id": "", "issuer_id": self.issuer_id, "issued_at": fmt(at),
                 "next_update": fmt(at + timedelta(hours=1)),
                 "entries": sorted(self.suspensions.values(), key=lambda e: e["passport_id"])}
        value["list_id"] = suspension_list_id(value)
        return value

    def lineage(self, agent_id: str) -> list[dict[str, Any]]:
        chain, current = [], self.agents[agent_id]
        while current is not None:
            chain.append(current)
            current = self.agents.get(current["parent"]) if current["parent"] else None
        return list(reversed(chain))

    def state_of(self, agent_id: str) -> str:
        at = self.clock()
        revoked = {e["passport_id"] for e in issuer.read_json(self.out / "revocation-list.json")["entries"]}
        states = []
        for record in self.lineage(agent_id):
            if record["passport_id"] in revoked:
                states.append("REVOKED")
            else:
                entry = self.suspensions.get(record["passport_id"])
                if entry and entry["reinstated_at"] is None and issuer.parse(entry["suspended_at"]) <= at:
                    states.append("SUSPENDED")
        return "REVOKED" if "REVOKED" in states else "SUSPENDED" if states else "ACTIVE"

    # ----- issuance
    def _issue(self, agent_id: str, display_name: str, parent: str | None, level: int, terms: list[str],
               tools: list[str]) -> dict[str, Any]:
        at = self.clock()
        spec = {"agent_id": agent_id, "display_name": display_name, "maximum_action_level": level,
                "action_terms": sorted(terms), "delegates": "spawn_agent" in tools,
                "capabilities": ["draft:internal-summary", "read:approved-public-information"],
                "tools": [{"tool_id": "tool." + t.replace("_", "-"),
                           "action_level": min(self.policy["tools"][t]["level"], level)} for t in sorted(tools)]}
        spec = {**issuer.load_policy({"policy_kind": issuer.POLICY_KIND, "issuer_id": self.issuer_id,
                                      "agents": [{**spec, "parent": None}]})["agents"][0], "parent": parent}
        not_before = at
        expires_at = at + timedelta(days=30)
        if parent:
            expires_at = min(expires_at, issuer.parse(self.agents[parent]["passport"]["validity"]["expires_at"]))
        folder = self.out / "agents" / agent_id
        values, manifest, descriptor = issuer.write_bundle(spec, folder / "bundle", self.issuer_id, at, not_before,
                                                           expires_at)
        issuer.write_json(folder / "bundle-manifest.json", manifest)
        passport = issuer.build_passport(spec, self.issuer_id, values, manifest, descriptor, not_before, expires_at,
                                         self.signing_key)
        issuer.write_json(folder / "passport.json", passport)
        depth = 0 if parent is None else self.agents[parent]["depth"] + 1
        record = {"agent_id": agent_id, "display_name": display_name, "parent": parent, "depth": depth,
                  "level": level, "terms": sorted(terms), "tools": sorted(tools), "passport": passport,
                  "passport_id": passport["passport_id"], "folder": folder, "binding": None}
        if parent:
            parent_record = self.agents[parent]
            binding = issuer.build_binding(spec, {"agent_id": parent}, depth, passport, parent_record["passport"])
            issuer.write_json(folder / "sub-agent-binding.json", binding)
            record["binding"] = binding
        self.agents[agent_id] = record
        status = self.passport_status(agent_id)
        self._record("passport_issued", {"agent_id": agent_id, "parent": parent, "depth": depth,
                                         "passport_id": passport["passport_id"], "maximum_action_level": level,
                                         "binding_id": record["binding"]["binding_id"] if record["binding"] else None,
                                         "verification_primary_status": status})
        return record

    def passport_status(self, agent_id: str) -> str:
        record = self.agents[agent_id]
        revocation = issuer.read_json(self.out / "revocation-list.json")
        key = (agent_id, revocation["sequence_number"] if revocation["entries"] else 0)
        if key not in self._validity:
            report = issuer.validate(record["folder"] / "passport.json", self.out / "trusted-key.json",
                                     self.out / "revocation-list.json", record["folder"] / "bundle-manifest.json",
                                     record["folder"] / "bundle", self.clock())
            self._validity[key] = report.get("verification_primary_status") or "ERROR"
        return self._validity[key]

    # ----- the guard
    def _fleet_request(self, agent_id: str, term: str, level: int, target: str) -> dict[str, Any]:
        at = self.clock()
        lineage = self.lineage(agent_id)
        root = lineage[0]
        revocation = issuer.read_json(self.out / "revocation-list.json")
        if (at - issuer.parse(revocation["issued_at"])).total_seconds() > 600:
            revocation = self._revocation()
        self.counter += 1
        return {
            "request_kind": "global-ai-governance.fleet-action-request", "request_version": "0.1.0-alpha.4",
            "request_id": f"lead-agent.request.{self.counter}",
            "profile": {"profile_id": "global-ai-governance.agent-fleet-controls", "profile_version": "0.1.0-alpha.4"},
            "evaluated_at": fmt(at),
            "root_passport": {"passport_id": root["passport_id"], "subject_id": root["agent_id"],
                              "maximum_action_level": root["level"], "action_terms": root["terms"],
                              "not_before": root["passport"]["validity"]["not_before"],
                              "expires_at": root["passport"]["validity"]["expires_at"]},
            "delegation_chain": [r["binding"] for r in lineage[1:]],
            "revocation_status": {"list_id": revocation["list_id"], "issued_at": revocation["issued_at"],
                                  "next_update": revocation["next_update"],
                                  "revoked_passport_ids": sorted(e["passport_id"] for e in revocation["entries"])},
            "suspension_list": self._suspension_list(at),
            "action": {"term": term, "requested_level": level, "target_id": target or "synthetic.target"},
        }

    def _approver(self, tool: str, args: dict[str, Any]) -> tuple[str, str]:
        approver = self.policy.get("level_4_approver") or {"mode": "person"}
        if approver.get("mode") == "automated":
            for rule in approver.get("rules", []):
                if rule.get("tool") != tool:
                    continue
                targets = rule.get("targets")
                if targets is None or args.get("target") in targets:
                    return APPROVED, f"Level 4: approved by the operator's automated approver {approver['approver_id']}"
        return ASK, "Level 4: waiting for an accountable person (operator policy)"

    def guard(self, agent_id: str, tool: str, args: dict[str, Any]) -> dict[str, Any]:
        spec = self.policy["tools"].get(tool)
        level = spec["level"] if spec else UNKNOWN_TOOL_LEVEL
        reasons: list[str] = []
        fleet_result = None
        record = self.agents[agent_id]
        if level >= 5:
            reasons.append(f"Level {level}: blocked; agents may not take this action")
        status = self.passport_status(agent_id)
        if status != "VALID":
            reasons.append(f"passport is {status}")
        state = self.state_of(agent_id)
        if state != "ACTIVE":
            reasons.append(f"passport lineage is {state}")
        if tool not in record["tools"]:
            reasons.append("tool is not in this agent's passport inventory")
        if level > record["level"]:
            reasons.append(f"Level {level} is above the passport ceiling {record['level']}")
        if spec and spec.get("term"):
            fleet_result = fleet_evaluate(self._fleet_request(agent_id, spec["term"], level,
                                                              str(args.get("target", ""))), ROOT)
            if fleet_result["operating_disposition"] != "PERMITTED":
                reasons.append("Agent Fleet Controls: " + ", ".join(fleet_result["reason_codes"]))
        if reasons:
            decision = DENY
        elif level == 4:
            decision, why = self._approver(tool, args)
            reasons.append(why)
        else:
            decision = ALLOW
            reasons.append(f"Level {level}: within the passport ceiling and the unattended limit (Level 3)")
        result = {"agent_id": agent_id, "tool": tool, "action_level": level, "decision": decision,
                  "reasons": reasons, "depth": record["depth"], "passport_id": record["passport_id"],
                  "fleet_reason_codes": fleet_result["reason_codes"] if fleet_result else None,
                  "authority_effect": "NONE"}
        self._record("guard_decision", {k: v for k, v in result.items() if k != "authority_effect"})
        return result

    # ----- actions
    def call(self, agent_id: str, tool: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        with self.lock:
            args = args or {}
            decision = self.guard(agent_id, tool, args)
            if decision["decision"] in (ALLOW, APPROVED):
                if tool == "spawn_agent":
                    child = self._spawn(agent_id, args.get("role", "research"))
                    decision["output"] = f"Started {child['agent_id']}"
                    decision["child"] = child["agent_id"]
                else:
                    decision["output"] = run_tool(tool, args)
                self._record("tool_result", {"agent_id": agent_id, "tool": tool, "output": decision["output"]})
            elif decision["decision"] == ASK:
                self.pending.append({"agent_id": agent_id, "tool": tool, "args": args})
            return decision

    def _spawn(self, parent: str, role: str) -> dict[str, Any]:
        spec = ROLES[role]
        n = sum(1 for a in self.agents.values() if a["agent_id"].startswith(f"agent.{role}")) + 1
        level = min(spec["level"], self.agents[parent]["level"])
        terms = [t for t in spec["terms"] if t in self.agents[parent]["terms"]] if level >= 4 else []
        tools = [t for t in spec["tools"] if self.policy["tools"][t]["level"] <= level or
                 self.policy["tools"][t]["level"] >= 5]
        tools = [t for t in tools if not (self.policy["tools"][t].get("term") and
                                          self.policy["tools"][t]["term"] not in terms and
                                          self.policy["tools"][t]["level"] < 5)]
        return self._issue(f"agent.{role}-{n}", f"{spec['display_name']} {n}", parent, level, terms, tools)

    def worker_for(self, role: str, parent: str = LEAD_ID) -> tuple[str | None, dict[str, Any] | None]:
        """An active sub-agent for the role, spawning one (through the guard) when none exists."""
        for record in self.agents.values():
            if record["parent"] == parent and record["agent_id"].startswith(f"agent.{role}-") \
                    and self.state_of(record["agent_id"]) == "ACTIVE":
                return record["agent_id"], None
        result = self.call(parent, "spawn_agent", {"role": role})
        return result.get("child"), result

    def chat(self, message: str) -> dict[str, Any]:
        with self.lock:
            self._record("goal", {"text": message[:500], "model": self.model.name})
            if self.state_of(LEAD_ID) != "ACTIVE":
                reply = f"The lead agent is {self.state_of(LEAD_ID).lower()}; no work was started."
                self._record("reply", {"text": reply})
                return {"reply": reply, "plan": [], "steps": [], "state": self.snapshot()}
            plan = self.model.plan(message)
            self._record("plan", {"steps": [{"role": s["role"], "tool": s["tool"]} for s in plan]})
            results = []
            for step in plan:
                worker, spawned = self.worker_for(step["role"])
                if spawned:
                    results.append(spawned)
                if worker is None:
                    continue
                if step.get("nested"):
                    parent = worker
                    for _ in range(step["nested"]):
                        attempt = self.call(parent, "spawn_agent", {"role": "research"})
                        results.append(attempt)
                        if not attempt.get("child"):
                            break
                        parent = attempt["child"]
                    continue
                results.append(self.call(worker, step["tool"], step.get("args", {})))
            counts = {d: sum(1 for r in results if r["decision"] == d) for d in (ALLOW, APPROVED, ASK, DENY)}
            reply = (f"Plan of {len(plan)} step{'s' if len(plan) != 1 else ''}, {len(results)} guarded tool calls: "
                     f"{counts[ALLOW]} ran, {counts[APPROVED]} approved by the operator's "
                     f"automated approver, {counts[ASK]} waiting for a person, {counts[DENY]} denied.")
            self._record("reply", {"text": reply})
            return {"reply": reply, "plan": [{"role": s["role"], "tool": s["tool"]} for s in plan], "steps": results,
                    "state": self.snapshot()}

    def control(self, action: str, agent_id: str) -> dict[str, Any]:
        with self.lock:
            record = self.agents[agent_id]
            at = fmt(self.clock())
            if action == "suspend":
                self.suspensions[record["passport_id"]] = {"passport_id": record["passport_id"], "suspended_at": at,
                                                           "reason_code": "OPERATOR_HOLD", "reinstated_at": None}
            elif action == "reinstate":
                entry = self.suspensions.get(record["passport_id"])
                if entry and entry["reinstated_at"] is None:
                    if entry["suspended_at"] >= at:
                        entry["suspended_at"] = fmt(self.clock() - timedelta(seconds=1))
                    entry["reinstated_at"] = at
            elif action == "revoke":
                issuer.revoke(self.out, record["passport_id"], at=self.clock(), reason_code="OTHER",
                              reason="Revoked by the lead agent's operator automation.")
            else:
                raise ValueError("action must be suspend, reinstate or revoke")
            affected = [a for a in self.agents if record["passport_id"] in
                        {r["passport_id"] for r in self.lineage(a)}]
            self._record("control", {"action": action, "agent_id": agent_id, "passport_id": record["passport_id"],
                                     "affected": affected})
            return {"action": action, "agent_id": agent_id, "affected": affected, "state": self.snapshot()}

    def shutdown_test(self) -> dict[str, Any]:
        """Suspend the root, confirm every agent is stopped, reinstate, confirm they resume."""
        with self.lock:
            agents = [a for a in self.agents if self.state_of(a) == "ACTIVE"]
            self.control("suspend", LEAD_ID)
            stopped = {a: self.guard(a, "search_notes", {})["decision"] for a in agents
                       if "search_notes" in self.agents[a]["tools"]}
            stopped_all = all(d == DENY for d in stopped.values()) and all(
                self.state_of(a) == "SUSPENDED" for a in agents)
            self.control("reinstate", LEAD_ID)
            resumed_all = all(self.state_of(a) == "ACTIVE" for a in agents)
            result = {"test": "shutdown", "agents": agents, "stopped_all": stopped_all, "resumed_all": resumed_all,
                      "result": "PASS" if stopped_all and resumed_all else "FAIL"}
            self._record("shutdown_test", result)
            return {**result, "state": self.snapshot()}

    def snapshot(self) -> dict[str, Any]:
        return {"agents": [{"agent_id": a["agent_id"], "display_name": a["display_name"], "parent": a["parent"],
                            "depth": a["depth"], "maximum_action_level": a["level"], "passport_id": a["passport_id"],
                            "binding_id": a["binding"]["binding_id"] if a["binding"] else None,
                            "state": self.state_of(a["agent_id"]), "tools": a["tools"]}
                           for a in self.agents.values()],
                "pending_person_approvals": list(self.pending), "delegation_max_depth": MAX_DEPTH,
                "model": self.model.name, "ledger_head": self.ledger.records[-1]["hash"],
                "ledger_length": len(self.ledger.records), "authority_effect": "NONE"}


# --------------------------------------------------------------------------- demo
DEMO_GOALS = (
    "Research agent governance on docs.example.org and draft a summary",
    "Buy a $500 dataset licence",
    "Delegate further: chain research sub-agents as deep as allowed",
    "Publish the summary to the public site",
)


def run_demo(out: Path | None = None) -> dict[str, Any]:
    agent = LeadAgent(out)
    transcript = [{"goal": goal, **{k: v for k, v in agent.chat(goal).items() if k != "state"}} for goal in DEMO_GOALS]
    researcher = next(a for a in agent.agents if a.startswith("agent.research-"))
    suspend = agent.control("suspend", LEAD_ID)
    blocked = agent.call(researcher, "search_notes", {"query": "while suspended"})
    agent.control("reinstate", LEAD_ID)
    resumed = agent.call(researcher, "search_notes", {"query": "after reinstatement"})
    shutdown = agent.shutdown_test()
    writer = next(a for a in agent.agents if a.startswith("agent.writer-"))
    agent.control("revoke", writer)
    revoked = agent.call(writer, "draft_text", {"topic": "after revocation"})
    ledger = agent.ledger.export()
    ok, detail = Ledger.verify(ledger)
    steps = [s for t in transcript for s in t["steps"]]
    checks = {
        "every passport VALID at issue": all(
            r["event"].get("verification_primary_status") == "VALID"
            for r in ledger["records"] if r["event"]["kind"] == "passport_issued"),
        "Level 5 spend denied": any(s["tool"] == "spend_funds" and s["decision"] == DENY for s in steps),
        "depth cap stops a spawn": any(s["tool"] == "spawn_agent" and s["decision"] == DENY and
                                       "SPAWN_WOULD_EXCEED_DEPTH" in (s["fleet_reason_codes"] or []) for s in steps),
        "Level 4 publish waits for a person": any(s["tool"] == "publish_external" and s["decision"] == ASK
                                                  for s in steps),
        "Level 4 fetch approved by automated approver": any(s["tool"] == "fetch_url" and s["decision"] == APPROVED
                                                            for s in steps),
        "suspend cascades to children": len(suspend["affected"]) == len(agent.agents) and blocked["decision"] == DENY,
        "reinstate resumes": resumed["decision"] == ALLOW,
        "shutdown test passes": shutdown["result"] == "PASS",
        "revoked passport stays denied": revoked["decision"] == DENY,
        "audit ledger verifies": ok,
    }
    if out:
        issuer.write_json(Path(out) / "audit-ledger.json", ledger)
    return {"checks": checks, "passed": all(checks.values()), "agents": len(agent.agents),
            "ledger": detail, "transcript": [{"goal": t["goal"], "reply": t["reply"]} for t in transcript]}


# --------------------------------------------------------------------------- local server
ALLOWED_ORIGINS = ("https://ai-governance.solutions",)


def agent_card(port: int) -> dict[str, Any]:
    return {
        "name": "Reference lead agent / orchestrator",
        "description": "Governs an agent fleet: passports bound to the parent, a guard on every tool call, "
                       "a delegation depth cap, suspend/revoke, shutdown tests and a hash-chained audit ledger. "
                       "Results are non-authorizing (authority_effect NONE).",
        "url": f"http://127.0.0.1:{port}/a2a",
        "version": VERSION,
        "protocolVersion": "0.3.0",
        "preferredTransport": "JSONRPC",
        "provider": {"organization": "Global AI Governance", "url": "https://ai-governance.solutions/"},
        "documentationUrl": "https://ai-governance.solutions/lead-agent/",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {"id": "govern-goal", "name": "Plan and run a goal through governed sub-agents",
             "description": "Plans the goal, spawns governed sub-agents and routes every tool call through the guard.",
             "tags": ["governance", "orchestration", "agent-fleet"], "examples": ["Research X and draft a summary"]},
            {"id": "shutdown-test", "name": "Run a shutdown test",
             "description": "Suspends the root passport, confirms every agent stops, then reinstates.",
             "tags": ["shutdown", "governance"]},
        ],
    }


def make_handler(agent: LeadAgent, port: int) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "lead-agent/" + VERSION

        def log_message(self, *_: Any) -> None:
            return

        def _cors(self) -> None:
            origin = self.headers.get("Origin", "")
            if origin in ALLOWED_ORIGINS or re.fullmatch(r"http://(localhost|127\.0\.0\.1)(:\d+)?", origin or "-"):
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Private-Network", "true")

        def _send(self, status: int, body: Any) -> None:
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self._cors()
            self.end_headers()
            self.wfile.write(data)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/state":
                self._send(200, agent.snapshot())
            elif self.path == "/api/audit":
                self._send(200, agent.ledger.export())
            elif self.path in ("/.well-known/agent-card.json", "/.well-known/agent.json"):
                self._send(200, agent_card(port))
            elif self.path == "/api/health":
                self._send(200, {"ok": True, "model": agent.model.name, "version": VERSION})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            try:
                length = min(int(self.headers.get("Content-Length") or 0), 65536)
                body = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/api/chat":
                    self._send(200, agent.chat(str(body.get("message", ""))[:2000]))
                elif self.path == "/api/control":
                    self._send(200, agent.control(str(body.get("action")), str(body.get("agent_id"))))
                elif self.path == "/api/shutdown-test":
                    self._send(200, agent.shutdown_test())
                elif self.path == "/a2a":
                    text = " ".join(p.get("text", "") for p in body.get("params", {}).get("message", {})
                                    .get("parts", []) if isinstance(p, dict))
                    result = agent.chat(text)
                    self._send(200, {"jsonrpc": "2.0", "id": body.get("id"), "result": {
                        "kind": "message", "role": "agent", "messageId": f"lead-agent-{len(agent.ledger.records)}",
                        "parts": [{"kind": "text", "text": result["reply"]},
                                  {"kind": "data", "data": {"steps": result["steps"]}}]}})
                else:
                    self._send(404, {"error": "not found"})
            except (KeyError, ValueError) as exc:
                self._send(400, {"error": str(exc)})

    return Handler


def serve(port: int = 8765, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    agent = LeadAgent(model=model_from_env())
    return ThreadingHTTPServer((host, port), make_handler(agent, port))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lead-agent", description="Reference lead agent / orchestrator.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_demo = sub.add_parser("demo", help="Run the governed fleet scenario offline and check every outcome.")
    p_demo.add_argument("--out", help="Keep the fleet files and audit-ledger.json in this directory.")
    p_serve = sub.add_parser("serve", help="Serve the JSON API for the browser app on 127.0.0.1.")
    p_serve.add_argument("--port", type=int, default=8765)
    p_verify = sub.add_parser("verify-audit", help="Re-verify an exported audit ledger (from here or the browser).")
    p_verify.add_argument("ledger")
    args = parser.parse_args(argv)
    if args.command == "demo":
        out = Path(args.out) if args.out else None
        if out:
            out.mkdir(parents=True, exist_ok=True)
        result = run_demo(out)
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1
    if args.command == "verify-audit":
        ok, detail = Ledger.verify(json.loads(Path(args.ledger).read_text(encoding="utf-8")))
        print(json.dumps({"verified": ok, "detail": detail}))
        return 0 if ok else 1
    server = serve(args.port)
    print(json.dumps({"listening": f"http://127.0.0.1:{args.port}", "model": server.RequestHandlerClass and
                      "see /api/health", "app": "https://ai-governance.solutions/lead-agent/"}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
