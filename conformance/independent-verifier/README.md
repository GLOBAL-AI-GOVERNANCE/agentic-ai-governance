<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Independent Verifier Reproduction Kit

## Purpose and audience

This implementation-neutral kit is for a genuinely separate verifier maintainer reproducing Agentic AI Governance outcomes at commit `60d5755299531f0e8c17e6beb559e7e1dc7e4910`. It provides pinned normative and fixture inventories, expected outcomes, discrepancy reporting, and an independent receipt template. It does not provide or prescribe a second implementation.

> Independent implementation is not the same as a project-maintained second implementation.

Project-authored or Codex-authored verification is not independent verification. Independence requires a separate maintainer and control boundary, attributable execution evidence, and no reuse of project implementation decision logic.

## Reproduction procedure

1. Obtain the repository at the exact controlling commit and verify every SHA-256 entry in `manifest.json`.
2. Implement the normative rules from the pinned specification and schemas without importing, translating, or wrapping `tools/` decision logic.
3. Evaluate the positive, negative, Stateful Revocation, OPA-boundary, and Agent Incident lifecycle vectors listed in the manifest.
4. Record every actual result, reason code, and disposition. Do not coerce discrepancies into expected outcomes.
5. File discrepancies using `DISCREPANCY_REPORT.md` and complete `INDEPENDENT_RECEIPT_TEMPLATE.json` with maintainer attribution, repository/commit, environment, and artifact digests.
6. Submit the independently maintained implementation and receipt for steward review. Submission does not itself establish acceptance or release readiness.

## PASS criteria

- Every pinned digest matches.
- Positive vectors produce the specified outcomes.
- Negative, malformed, stale, revoked, rollback, conflicting-state, unsupported-policy, and authority-exceeding vectors fail closed as specified.
- Policy denial remains distinct from revocation.
- A revoked passport is never restored; reauthorization uses a distinct passport.
- OPA outputs remain decisions with `external_enforcement: NOT_PERFORMED`.
- Stateful Revocation continuity claims remain bounded to an intact trusted local store.
- The independent receipt is attributable, complete, and reproducible.

Any mismatch is a finding. Preserve the observed result, minimize a reproducer, and stop any claim of independent reproduction until the discrepancy is resolved and re-run.

## Limitations and lifecycle

This kit does not establish independent maintenance, certification, compliance, production safety, external enforcement, runtime containment, universal interoperability, or a release decision. Status remains `PROPOSED / NOT_YET_ESTABLISHED` and `WAITING — INDEPENDENT MAINTENANCE NOT ESTABLISHED` until a genuinely separate maintainer supplies accepted evidence.
