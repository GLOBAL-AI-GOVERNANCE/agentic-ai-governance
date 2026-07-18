<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DR-005: Public Release Sequencing

**Status:** Accepted for `v0.1.0-alpha.1`.

**Steward decision date:** July 17, 2026.

**Decision authority:** Global AI Governance steward.

## Decision

The steward explicitly supersedes the earlier draft portfolio-sequencing dependency for Agentic AI Governance.

Agentic AI Governance may proceed on its own repository-specific evidence, subject to all of the following release gates:

1. A clean canonical repository tree passes local generation, conformance, and test checks.
2. Hosted CI passes on every supported Python runtime for the canonical commit.
3. The release uses an immutable tag, matching checksums, retrievable versioned schemas, and logged-out UAT.

Separate portfolio projects are not mechanical release prerequisites unless a causal technical, legal, security, licensing, or stewardship dependency is explicitly documented.

## Rationale

The Alpha.1 specification, schemas, examples, conformance fixtures, and reference validator are independently testable and do not require another portfolio repository to be published first. Release dependencies should correspond to actual dependencies rather than portfolio order alone. This decision preserves fail-closed release controls while preventing unrelated project state from silently blocking an otherwise qualified public-good release.

## Supersession

This record supersedes any unpublished draft decision that required separate Global AI Governance portfolio projects to be released or tagged before Agentic AI Governance could proceed.

Future changes to this sequencing rule require a new or amended governance decision record approved by the steward.
