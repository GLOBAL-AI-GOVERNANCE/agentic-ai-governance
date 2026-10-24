<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agent Fleet Controls Conformance Vectors

This directory pins the `v0.1.0-alpha.4` Agent Fleet Controls conformance material: the normative section `spec/11-agent-fleet-controls.md`, its schemas and profile, and synthetic request vectors in `examples/fleet-controls/` with expected outcomes.

`manifest.json` lists every artifact with its SHA-256 digest. Each vector records the expected `operating_disposition`, `passport_state`, `reason_codes`, `effective_level`, and `delegation_depth`. Vectors are evaluated at the pinned instant `2026-10-24T12:00:00Z`, which every request carries as `evaluated_at`.

## Verifier target version

These vectors target `v0.1.0-alpha.4`. The independent-verifier reproduction kit in `conformance/independent-verifier/` stays pinned to its existing controlling commit on the `v0.1.0-alpha.2` line and does not include these vectors. Moving the kit target to `v0.1.0-alpha.4` requires a separate steward decision (see `decisions/DR-011-alpha4-agent-fleet-controls.md`).

## Reproduction

1. Verify every SHA-256 entry in `manifest.json`.
2. Implement the rules in `spec/11-agent-fleet-controls.md` and evaluate each vector.
3. Record every actual result. Do not coerce discrepancies into expected outcomes.

The project's reference evaluator reproduces every expected outcome with `python tools/fleet_controls.py <vector>`. That is project-authored testing, not independent verification. Independent verification is `PROPOSED / NOT_YET_ESTABLISHED`.

## Limitations

Vectors are synthetic. They do not carry signatures; signature checks for passports and revocation lists stay on the Alpha.1 path. The vectors do not establish runtime enforcement, certification, or production use.
