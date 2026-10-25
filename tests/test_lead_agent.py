# SPDX-License-Identifier: Apache-2.0
"""Reference lead agent / orchestrator: guard, depth cap, cascade, shutdown test, audit ledger, providers."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import threading
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("lead_agent", ROOT / "examples/lead-agent/lead_agent.py")
lead = importlib.util.module_from_spec(SPEC)
sys.modules["lead_agent"] = lead
SPEC.loader.exec_module(lead)


@pytest.fixture(scope="module")
def demo() -> dict:
    return lead.run_demo()


def test_demo_passes_every_check(demo: dict) -> None:
    assert demo["passed"], demo["checks"]
    assert len(demo["checks"]) == 10


def test_level_5_always_denied_even_with_automated_approver(tmp_path: Path) -> None:
    policy = json.loads(json.dumps(lead.DEFAULT_POLICY))
    policy["level_4_approver"]["rules"].append({"tool": "spend_funds"})
    agent = lead.LeadAgent(tmp_path, policy=policy)
    worker, _ = agent.worker_for("procurement")
    result = agent.call(worker, "spend_funds", {"amount_usd": 1})
    assert result["decision"] == "deny"
    assert "LEVEL_5_NOT_PERMITTED" in result["fleet_reason_codes"]


def test_level_4_asks_a_person_by_default(tmp_path: Path) -> None:
    policy = json.loads(json.dumps(lead.DEFAULT_POLICY))
    policy["level_4_approver"] = {"mode": "person"}
    agent = lead.LeadAgent(tmp_path, policy=policy)
    assert agent.call(lead.LEAD_ID, "spawn_agent", {"role": "writer"})["decision"] == "ask"
    assert agent.call(lead.LEAD_ID, "search_notes", {})["decision"] == "allow"
    assert agent.snapshot()["pending_person_approvals"][0]["tool"] == "spawn_agent"


def test_unlisted_fetch_target_waits_for_a_person(tmp_path: Path) -> None:
    agent = lead.LeadAgent(tmp_path)
    assert agent.call(lead.LEAD_ID, "fetch_url", {"target": "unknown.example.net"})["decision"] == "ask"
    assert agent.call(lead.LEAD_ID, "fetch_url", {"target": "docs.example.org"})["decision"] == "approved"


def test_depth_cap_and_cascade(tmp_path: Path) -> None:
    agent = lead.LeadAgent(tmp_path)
    parent = lead.LEAD_ID
    for depth in range(1, 4):
        parent = agent.call(parent, "spawn_agent", {"role": "research"})["child"]
        assert agent.agents[parent]["depth"] == depth
        assert agent.passport_status(parent) == "VALID"
    blocked = agent.call(parent, "spawn_agent", {"role": "research"})
    assert blocked["decision"] == "deny" and "SPAWN_WOULD_EXCEED_DEPTH" in blocked["fleet_reason_codes"]
    first = next(a for a, r in agent.agents.items() if r["depth"] == 1)
    affected = agent.control("suspend", first)["affected"]
    assert len(affected) == 3 and lead.LEAD_ID not in affected
    assert agent.call(parent, "search_notes", {})["decision"] == "deny"
    assert agent.call(lead.LEAD_ID, "search_notes", {})["decision"] == "allow"
    agent.control("reinstate", first)
    assert agent.call(parent, "search_notes", {})["decision"] == "allow"
    agent.control("revoke", first)
    assert agent.state_of(parent) == "REVOKED"
    assert agent.passport_status(first) == "REVOKED"


def test_tool_outside_passport_inventory_denied(tmp_path: Path) -> None:
    agent = lead.LeadAgent(tmp_path)
    writer, _ = agent.worker_for("writer")
    assert agent.call(writer, "run_analysis", {})["decision"] == "deny"
    assert agent.call(writer, "unknown_tool", {})["decision"] == "deny"


def test_shutdown_test_passes(tmp_path: Path) -> None:
    agent = lead.LeadAgent(tmp_path)
    agent.chat("research and draft a summary")
    result = agent.shutdown_test()
    assert result["result"] == "PASS" and len(result["agents"]) == 3


def test_ledger_detects_tampering() -> None:
    ledger = lead.Ledger()
    for n in range(3):
        ledger.append("2026-07-18T12:00:00Z", {"kind": "note", "n": n})
    good = ledger.export()
    assert lead.Ledger.verify(good)[0]
    bad = json.loads(json.dumps(good))
    bad["records"][1]["event"]["n"] = 9
    assert not lead.Ledger.verify(bad)[0]
    cut = json.loads(json.dumps(good))
    del cut["records"][1]
    assert not lead.Ledger.verify(cut)[0]


def test_mock_model_is_deterministic() -> None:
    model = lead.MockModel()
    assert model.plan("Buy a thing") == model.plan("Buy a thing")
    assert model.plan("Buy a thing")[0]["tool"] == "spend_funds"


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


@pytest.mark.parametrize("provider, env, reply", [
    ("openai", "OPENAI_API_KEY", {"choices": [{"message": {"content": '{"steps": [{"role": "writer", "tool": "draft_text"}]}'}}]}),
    ("xai", "XAI_API_KEY", {"choices": [{"message": {"content": '{"steps": [{"role": "writer", "tool": "draft_text"}]}'}}]}),
    ("anthropic", "ANTHROPIC_API_KEY", {"content": [{"type": "text", "text": '{"steps": [{"role": "writer", "tool": "draft_text"}]}'}]}),
])
def test_provider_request_shape_offline(monkeypatch, provider, env, reply) -> None:
    monkeypatch.setenv(env, "test-key-not-real")
    seen = {}

    def opener(request, timeout):
        seen["url"], seen["headers"], seen["body"] = request.full_url, dict(request.headers), json.loads(request.data)
        return _Response(json.dumps(reply).encode())

    model = lead.ProviderModel(provider, opener=opener)
    assert model.plan("draft something") == [{"role": "writer", "tool": "draft_text", "args": {}}]
    base = lead.PROVIDERS[provider]["base"]
    assert seen["url"].startswith(base)
    assert "test-key-not-real" in json.dumps(seen["headers"])
    assert "test-key-not-real" not in json.dumps(seen["body"])


def test_provider_requires_env_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        lead.ProviderModel("openai")


def test_local_server_api_and_cors() -> None:
    server = lead.serve(port=0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def post(path, body, origin="https://ai-governance.solutions"):
            req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "Origin": origin})
            with urllib.request.urlopen(req) as response:
                return response.headers, json.loads(response.read())
        headers, chat = post("/api/chat", {"message": "Buy a dataset"})
        assert headers["Access-Control-Allow-Origin"] == "https://ai-governance.solutions"
        assert any(s["tool"] == "spend_funds" and s["decision"] == "deny" for s in chat["steps"])
        headers, _ = post("/api/shutdown-test", {}, origin="https://evil.example")
        assert headers.get("Access-Control-Allow-Origin") is None
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/audit") as response:
            assert lead.Ledger.verify(json.loads(response.read()))[0]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/.well-known/agent-card.json") as response:
            card = json.loads(response.read())
        assert {"name", "url", "version", "skills", "capabilities"} <= set(card)
        _, a2a = post("/a2a", {"jsonrpc": "2.0", "id": 1, "method": "message/send",
                                "params": {"message": {"role": "user", "parts": [{"kind": "text", "text": "draft a note"}]}}})
        assert a2a["result"]["role"] == "agent"
    finally:
        server.shutdown()
