<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Independent Verifier Reproduction Kit

## Purpose and audience

This implementation-neutral kit is for a genuinely separate verifier maintainer reproducing Agentic AI Governance outcomes at commit `e951798d64e247612f625bf50f23b10a0e30992e` (tree `5e035f538bf427f619e5055499ca22abe09ac653`). It provides pinned normative and fixture inventories, expected outcomes, discrepancy reporting, and an independent receipt template. It does not provide or prescribe a second implementation.

> Independent implementation is not the same as a project-maintained second implementation.

Project-authored or Codex-authored verification is not independent verification. Independence requires a separate maintainer and control boundary, attributable execution evidence, and no reuse of project implementation decision logic.

## Reproduction procedure

1. Obtain the repository at the exact controlling commit and verify every SHA-256 entry in `manifest.json`.
2. Implement the normative rules from the pinned specification and schemas without importing, translating, or wrapping `tools/` decision logic.
3. Evaluate the positive, negative, Stateful Revocation, OPA-boundary, and Agent Incident lifecycle vectors listed in the manifest, using each declared evaluation context.
4. Record every actual result, reason code, and disposition. Do not coerce discrepancies into expected outcomes.
5. File discrepancies using `DISCREPANCY_REPORT.md` and complete `INDEPENDENT_RECEIPT_TEMPLATE.json` with maintainer attribution, repository/commit, environment, and artifact digests.
6. Submit the independently maintained implementation and receipt for steward review. Submission does not itself establish acceptance or release readiness.

## Reproduction context

Passport outcomes depend on the evaluation instant and on the bound validation inputs. The manifest declares them as the named evaluation context `passport-quickstart-2026-07-18`, referenced by `examples/passports/signed-unrevoked.json` and `examples/passports/signed-revoked.json`:

| Input | Value | SHA-256 at the controlling commit |
| --- | --- | --- |
| Evaluation time | `2026-07-18T12:00:00Z` | — |
| Trusted key | `examples/trusted-keys/test-ed25519-key.json` | `12aced78e53f588e1e5c29d44f57ba1eea9684c14322769451f484e9b8cba8d5` |
| Revocation list | `examples/revocation/valid-revocation-list.json` | `1a0f71185269d21e15abc3b7360465a9b1ae541fb910b1fa4d18033d66343212` |
| Bundle manifest | `examples/bundles/valid-bundle-manifest.json` | `abf8c861380e9f7d51841286b45f583f8d8b1559afc2d867a0392d3e553bcc34` |
| Bundle root | repository root at the controlling commit | not digested; bundle contents are bound by the digest-listed bundle manifest |

The evaluation time lies inside both passport validity windows, the trusted key validity window, and the revocation list freshness interval (`issued_at` 2026-07-18T00:00:00Z to `next_update` 2026-07-19T00:00:00Z). Passport vectors use stateless signed-revocation evaluation. Evaluating at another instant, such as the current wall clock, yields different and still fail-closed results (for example `EXPIRED`); that is a context difference, not a reproduction of the declared outcomes.

The Stateful Revocation `INITIALIZABLE` expectation assumes a fresh trusted continuity store with no previously accepted state.

Record the pinned evaluation time and context in the receipt fields `evaluation_time` and `evaluation_context`. `executed_at_utc` records execution provenance only and does not substitute for the pinned evaluation time.

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
