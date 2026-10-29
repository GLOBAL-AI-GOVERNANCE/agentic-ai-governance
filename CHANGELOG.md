<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Changelog

## Unreleased

- Added `tools/check_schema_ids.py` with offline and `--online` live resolution of every http(s) schema `$id`, wired into Conformance CI.
- The browser scenario at https://ai-governance.solutions/lead-agent/ runs locally and does not sign passports. `lead-agent verify-audit` re-checks the ledger it downloads.

## v0.1.0-alpha.5 - 2026-10-24

- Recorded the steward-approved Alpha.5 tooling release in DR-012. No schema identity, profile, signed example, or claim changes, and no claim is promoted.
- Added `tools/issue_passports.py` and the `issue-passports` console script. They issue signed passports and Sub-Agent Passport Bindings for every agent in a fleet policy file, write a signed revocation list, validate every passport, and handle revocation and refresh, with no manual step. The policy rejects Level 5, `spend_funds`, and any sub-agent that would exceed its parent.
- Added the reference lead agent / orchestrator `examples/lead-agent/lead_agent.py` and the `lead-agent` console script. It runs a guard on every tool call, Agent Fleet Controls for fleet actions, a delegation depth cap of 3, suspend/reinstate/revoke cascades, shutdown tests, and a hash-chained audit ledger. The planner is a deterministic offline model by default, with OpenAI-, Anthropic- and xAI-compatible planners when a key is set. Level 5 is always denied; Level 4 goes to the approver the operator names (a person by default, or the operator's automated approver for listed calls). It also has a local JSON API with an A2A agent card for the browser app.
- Added `AGENTS.md` with setup and check instructions for coding agents.

## v0.1.0-alpha.4 - 2026-10-24

- Recorded the steward-approved Alpha.4 Agent Fleet Controls release in DR-011. It adds claim `AAG-FLEET-001` with Delivery Status `DEFINED` and Evidence Status `NOT_YET_ESTABLISHED`, promotes no claim, and leaves the active increment unchanged.
- Added specification section `spec/11-agent-fleet-controls.md` and five `v0.1.0-alpha.4` schemas: fleet controls common definitions, fleet controls profile, fleet action request, Sub-Agent Passport Binding, and Passport Suspension List.
- Added the hash-anchored Agent Fleet Controls profile with per-level status maximum ages (Level 0-1 24 hours, Level 2 12 hours, Level 3 1 hour, Level 4 15 minutes, Level 5 5 minutes), minimum levels for the `spawn_agent`, `provision_compute`, `install_tool`, `network_call`, and `spend_funds` action terms, and a delegation depth cap of 3.
- Added a reinstatable `SUSPENDED` passport state distinct from terminal revocation, with content-addressed suspension lists.
- Added content-addressed sub-agent passport bindings: each sub-agent has its own passport, and its action level, action terms, and validity never exceed its parent's. Ancestor revocation and suspension apply to every descendant.
- Added the reference evaluator `tools/fleet_controls.py`, 23 synthetic conformance vectors with a digest-pinned manifest, repository verification of every vector, and regression tests.
- Documented that the independent-verifier kit stays pinned to its `v0.1.0-alpha.2` controlling commit; the Alpha.4 vectors are published separately.

## v0.1.0-alpha.3 - 2026-10-24

- Recorded the steward-approved Alpha.3 packaging release in DR-010. No claim is promoted; the OPA bridge, Agent Incident Readiness demonstration, and readiness mappings are included as references with Delivery Status `DEFINED`.
- Added a CI job that builds the sdist, wheel, and release-style source archive and installs each into a clean environment before validating the example passports. The release workflow repeats the archive install before attesting.
- Moved package license metadata to an SPDX expression with explicit license files.
- Added Python packaging metadata so `pip install git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance.git@v0.1.0-alpha.3` provides the importable `agentic_ai_governance` package and a `validate-passport` console script. The wheel bundles the reference validator, schemas, profiles, and synthetic examples; results are the unchanged `tools/validate_artifact.py` report.
- Updated the validation environment to `cryptography==50.0.1`, retaining the established pytest contract while taking the patch release's refreshed OpenSSL-backed wheels.
- Added the synthetic Agent Incident Readiness reference trace and deterministic verifier for the Authorized → Policy-Denied → Revoked → Rollback-Rejected → New-Passport Reauthorized lifecycle. The original passport remains terminally revoked, reauthorization requires a distinct passport, and no external enforcement is performed.
- Added a bounded, non-enforcing OPA bridge reference adapter, policy, synthetic vectors, stable reason codes, adversarial tests, and hosted OPA v1.19.1 verification. The implementation consumes established validation results, and preserves canonical operating dispositions.

## v0.1.0-alpha.2 - 2026-08-30

- Added an explicitly initialized, atomic local revocation continuity store to the reference verifier, with subprocess regressions for restart persistence, monotonic chaining, fail-closed corruption and freshness handling, and terminal cumulative revocation. This Alpha.2 reference capability provides rollback detection only relative to an intact trusted local store.
- Added a regression-checked sole-public-project-identity statement for GLOBAL AI GOVERNANCE.
- Established continuous V&V, one-active-increment sequencing, and the Stateful Revocation-first public roadmap.
- Added machine-readable Claims Register, prohibited-claims controls, and mixed-version schema catalog governance.
- Preserved the Alpha.1 generated distribution while making the distribution builder extensible to separately versioned future profiles.
- Added repository enforcement and tests for governance, claims, schema-catalog, and generated-distribution integrity.
- Enforced evidence references, verification method, and verification date for every `VERIFIED` claim.
- Added deterministic prohibited-wording scans for declared repository paths while retaining release review for external surfaces.
- Added catalog-wide local and cross-schema `$ref` resolution plus protected baseline schema identities.
- Recorded the steward-approved Alpha.2 release decision, promoted released current-main claims where justified, and advanced the one-active-increment program boundary to OPA without implementing OPA.

## v0.1.0-alpha.1

- Added semantic evidence admission, profile descriptors, inventory schemas, action-authority binding, complete condition equality, and evaluator/policy support checks.
- Added signed adversarial regressions for expired or untrusted evidence, unresolved references, profile drift, unsupported evaluator or policy metadata, destructive action graphs, and inventory-subject mismatch.
- Added pinned `pip-audit` to the connected CI gate.
- Enforced bidirectional equality between declared MCP inventory servers and reachable `MCP_SERVER` action-graph nodes.
- Published the experimental specification, versioned schemas, reusable profile, and synthetic examples.
- Added strict JSON parsing, RFC 8785 canonicalization, content-derived identifiers, and Ed25519 detached-JWS verification.
- Added assessment, verification-result, revocation, validity, signing-key, and action-authority consistency checks.
- Enforced the assessment `data_authority_status` result cap and added versioned Alpha.1 inventory schemas.
- Renamed the revoked passport example to `signed-revoked.json` to remove quickstart ambiguity.
- Added public governance decision records for stewardship, licensing, assurance, decision states, and release sequencing.
- Recorded the steward-approved release-sequencing supersession in DR-005, limiting release dependencies to explicitly documented causal dependencies.
- Added a complete signed-passport trust command with structured errors and fail-closed decisions.
- Separated issued assessment result, verification primary status, and operating disposition in the public CLI output.
- Added positive, negative, malformed-input, and trust-policy regressions across Python 3.11–3.13 CI.
- Added fail-closed bound-input verification for the canonical bundle manifest, inventories, control profile, data-authority evidence, and assessment summary.
- Rejected unknown critical extensions, contradictory passport summaries, unsupported versions, invalid revocation chronology, unrelated revocation authorities, and unusable Ed25519 verification keys.
- Replaced empty inventory placeholders in the quickstart with non-empty synthetic inventories and reconciled every passport binding.
- Updated GitHub Actions to SHA-pinned Node 24-compatible official releases.
- Pinned `cryptography==49.0.0` and `pytest==9.0.3` for the public-alpha validation environment.

- Closed the final policy-anchor and authority-semantics findings by pinning canonical profile hashes, enforcing condition ceilings, validating evidence at assessment and verification time, and mapping controlled capabilities, MCP scopes, tool effects, and graph edges to minimum action levels.
