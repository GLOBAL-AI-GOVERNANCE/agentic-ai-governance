<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Reference lead agent / orchestrator

`lead_agent.py` is a reference lead agent that runs an agent fleet with no manual step. It uses the same code as the rest of this repository: passports come from [`tools/issue_passports.py`](../../tools/issue_passports.py), fleet decisions from [`tools/fleet_controls.py`](../../tools/fleet_controls.py), and passport checks from the reference validator. It needs only the package dependencies (`jsonschema`, `cryptography`). By default it is fully offline.

```bash
python examples/lead-agent/lead_agent.py demo            # or, from an installed package: lead-agent demo
python examples/lead-agent/lead_agent.py serve           # JSON API on http://127.0.0.1:8765 for the browser app
python examples/lead-agent/lead_agent.py verify-audit audit-ledger.json
```

`demo` exits 0 only when all ten of its checks pass. A browser version that runs entirely on the page is at <https://ai-governance.solutions/lead-agent/>.

## What it governs

| Control | How it works |
| --- | --- |
| Sub-agent passports | Every sub-agent gets its own signed Agent Trust Passport and a Sub-Agent Passport Binding to its parent. Its level, action terms and validity never exceed the parent's. Each passport is checked by the reference validator and must be `VALID`. |
| A guard on every tool call | In order: Level 5 is denied; the passport must be `VALID` at this clock; no passport in the lineage may be revoked or suspended; the tool must be in the passport inventory and within its ceiling; fleet actions (`spawn_agent`, `network_call`, `spend_funds`) must be `PERMITTED` by Agent Fleet Controls. If all of that passes, Levels 0-3 run and Level 4 goes to the approver. |
| Level 4 approver | Set by the operator in `level_4_approver`. With `"mode": "person"`, Level 4 waits for an accountable person and the other work carries on. With `"mode": "automated"`, the operator lists the Level 4 calls its own automation approves, for example `spawn_agent`, or `fetch_url` to named hosts. Anything not listed waits for a person. |
| Level 5 | Always denied. It cannot be configured or approved. |
| Delegation depth | Capped at 3 below the lead (Agent Fleet Controls profile). A spawn that would go deeper is denied with `SPAWN_WOULD_EXCEED_DEPTH`. |
| Suspend, reinstate, revoke | Suspension is reinstatable; revocation re-signs the cumulative revocation list and is terminal. Either one applies to every descendant. |
| Shutdown test | Suspends the lead's passport, checks that every agent is stopped, reinstates it, and checks that every agent resumes. The result is `PASS` or `FAIL`. |
| Audit ledger | Every goal, plan, issuance, guard decision, result and control action is appended to a SHA-256 hash-chained ledger. `verify-audit` re-checks the chain. The browser app writes the same record format. |

Status lists are re-issued in-process, so they stay within the 15-minute freshness window that Level 4 requires.

## Models

The default planner is deterministic and offline: no key and no network. To plan with a hosted model, set `LEAD_AGENT_PROVIDER` and that provider's key in the environment:

| `LEAD_AGENT_PROVIDER` | Key variable | API shape |
| --- | --- | --- |
| `openai` | `OPENAI_API_KEY` | Chat Completions, JSON output |
| `xai` | `XAI_API_KEY` | OpenAI-compatible, `https://api.x.ai/v1` |
| `anthropic` | `ANTHROPIC_API_KEY` | Messages API |

`LEAD_AGENT_BASE_URL` and `LEAD_AGENT_MODEL` override the endpoint and model, so any OpenAI-compatible server works. Keys are read from the environment, sent only in the request header to that provider, and never written to the ledger, the API responses or disk. The model only proposes a plan: every step still goes through the guard. The tests check the request shape for all three providers against a local stub. No live provider call is made in CI.

## Local server

`serve` listens on `127.0.0.1` only. It accepts cross-origin requests from `https://ai-governance.solutions` and from `localhost`, so the browser app can use it, and it answers the private-network preflight. Endpoints:

- `POST /api/chat` `{"message": "..."}`
- `POST /api/control` `{"action": "suspend" | "reinstate" | "revoke", "agent_id": "..."}`
- `POST /api/shutdown-test`
- `GET /api/state`
- `GET /api/audit`
- `GET /.well-known/agent-card.json`, an A2A agent card
- `POST /a2a`, which takes an A2A `message/send` JSON-RPC request

## Boundaries

The tools are synthetic stand-ins: nothing outside the process is fetched, published, spent or deleted. Passports are issued under the synthetic, non-production reference profile. Every result carries `authority_effect: NONE`. A guard `allow` means no check stopped the call; it is not an approval of the work and not an external enforcement. Evidence status for Agent Fleet Controls stays `NOT_YET_ESTABLISHED`.
