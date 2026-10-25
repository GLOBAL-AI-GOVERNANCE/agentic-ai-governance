<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# v0.1.0-alpha.5 Release Notes

Agentic AI Governance `v0.1.0-alpha.5` is an experimental prerelease. It adds unattended passport issuance and a reference lead agent / orchestrator, so a governed agent fleet can be set up and run without a manual step. No schema identity, profile, vector, or signed example changes.

## Install

```bash
python -m pip install "git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance.git@v0.1.0-alpha.5"
curl -fsSLO https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance/v0.1.0-alpha.5/examples/fleet-issuance/fleet-policy.json
issue-passports issue fleet-policy.json --out fleet/   # every passport VALID, exit 0
lead-agent demo                                        # ten checks, exit 0
```

The release archive `agentic-ai-governance-v0.1.0-alpha.5.zip` installs the same way. It is built in GitHub Actions from the tag and ships with SHA-256 checksums and build provenance:

```bash
gh attestation verify agentic-ai-governance-v0.1.0-alpha.5.zip --repo GLOBAL-AI-GOVERNANCE/agentic-ai-governance
```

## What ships

- **Unattended issuance.** `issue-passports` issues signed passports and Sub-Agent Passport Bindings for a whole fleet from a policy file, writes a signed revocation list, validates every passport, and handles revocation and refresh. The policy rejects Level 5, `spend_funds`, and any sub-agent that would exceed its parent.
- **Reference lead agent / orchestrator.** `lead-agent` runs a guard on every tool call, Agent Fleet Controls for fleet actions, a delegation depth cap of 3, suspend/reinstate/revoke cascades, shutdown tests, and a hash-chained audit ledger. The planner is a deterministic offline model by default, with OpenAI-, Anthropic- and xAI-compatible planners when a key is set in the environment. `lead-agent serve` exposes a local JSON API and an A2A agent card for the browser app at <https://ai-governance.solutions/lead-agent/>.
- **Approver routing.** Level 5 is always denied. Level 4 goes to a person by default, or to the operator's automated approver for the calls the policy lists.

## Assurance boundary

Both additions are references with `authority_effect: NONE`, tested by the repository suite. They do not provide runtime containment, production IAM, certification, or legal compliance. `AAG-FLEET-001` stays `DEFINED / NOT_YET_ESTABLISHED`, and independent verification by a separately maintained verifier remains open (`DR-012`).

## Verification

The release commit passes the Python 3.11, 3.12, and 3.13 Conformance matrix, repository verification, the complete pytest suite, and the clean-environment package and archive installs.

## Previous release

### v0.1.0-alpha.4

Agentic AI Governance `v0.1.0-alpha.4` is an experimental prerelease. It adds Agent Fleet Controls: rules and a reference evaluator that decide whether an agent, or a sub-agent it started, may take a fleet action before it runs. The additions are new schemas and a new profile; released schema identities, the MCP Governance Profile, and the signed examples are unchanged.

#### Install

```bash
python -m pip install "git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance.git@v0.1.0-alpha.4"
validate-passport --example signed-unrevoked     # exit 0, artifact_validation_status PASS
```

The release archive `agentic-ai-governance-v0.1.0-alpha.4.zip` installs the same way. It is built in GitHub Actions from the tag and ships with SHA-256 checksums and build provenance:

```bash
gh attestation verify agentic-ai-governance-v0.1.0-alpha.4.zip --repo GLOBAL-AI-GOVERNANCE/agentic-ai-governance
```

The fleet evaluator runs from the source archive or a checkout:

```bash
python tools/fleet_controls.py examples/fleet-controls/sub-agent-spawn-permitted.json   # exit 0, PERMITTED
python tools/fleet_controls.py examples/fleet-controls/ancestor-suspended.json          # exit 3, SUSPENDED
```

#### What ships

- **Status freshness by level.** Revocation and suspension status must be newer than a per-level maximum age: 24 hours at Levels 0-1, 12 hours at Level 2, 1 hour at Level 3, 15 minutes at Level 4, 5 minutes at Level 5. Requests may tighten these values, never loosen them.
- **Suspension.** A reinstatable `SUSPENDED` state, separate from revocation. Revocation stays terminal even when a suspension entry or a stale list is presented.
- **Fleet action terms.** `spawn_agent`, `provision_compute`, `install_tool`, and `network_call` require Level 4. `spend_funds` requires Level 5, which stays not permitted.
- **Delegation depth cap.** At most 3 levels below the root passport. A spawn that would exceed the cap is refused.
- **Sub-agent passports.** Each sub-agent has its own passport, bound to its parent by a content-addressed Sub-Agent Passport Binding. Its level, terms, and validity never exceed the parent's. Revocation or suspension of any ancestor applies to every descendant.
- **Hash-anchored profile.** The evaluator pins the profile document and descriptor hashes, so a request cannot redefine the limits.
- **Conformance vectors.** 23 synthetic vectors with expected outcomes, pinned by SHA-256 in `conformance/fleet-controls/manifest.json` and reproduced by repository verification and tests.

#### Verifier target

The independent-verifier kit stays pinned to its `v0.1.0-alpha.2` controlling commit. The Alpha.4 vectors are published separately; moving the kit target requires a separate steward decision (`DR-011`).

#### Assurance boundary

Agent Fleet Controls have Delivery Status `DEFINED` and Evidence Status `NOT_YET_ESTABLISHED`. The evaluator consumes already-verified passport and status facts; it does not verify signatures, authenticate agents, or enforce its decision. Evaluation time must come from a clock the deployment trusts. Vectors are synthetic. This prerelease does not provide runtime containment, production IAM, a production policy engine, certification, or legal compliance. Independent verification by a separately maintained verifier remains open.

#### Verification

The release commit passes the Python 3.11, 3.12, and 3.13 Conformance matrix, repository verification including every fleet vector, the complete pytest suite, dependency consistency and advisory audit, the signed-passport trust path, the generated-distribution check, Claims Register validation, and the clean-environment package and archive installs.
