<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# v0.1.0-alpha.2 Release Notes

Agentic AI Governance `v0.1.0-alpha.2` is an experimental prerelease that ships the verified post-Alpha.1 reference-tooling and repository-governance delta while preserving the Alpha.1 normative specification and released schema identities.

## What ships

- **Stateful Revocation continuity.** The reference verifier can optionally persist trusted revocation continuity across restarts with explicit initialization, monotonic sequence and predecessor checks, fail-closed corrupt/stale-state handling, and terminal cumulative revocation relative to an intact trusted local store.
- **Claims and release governance.** Machine-readable Claims Register, prohibited-claims controls, continuous V&V policy, one-active-increment sequencing, public-release scrub controls, and evidence requirements are now part of the released repository state.
- **Schema and repository integrity controls.** The schema catalog, protected released-schema digests, catalog-wide reference resolution, generated-distribution integrity, and extensible distribution tooling are released without changing the Alpha.1 generated distribution.

## Compatibility and preservation

The Alpha.1 generated specification remains byte-identical. The Alpha.1 tagged release remains historical and immutable. Alpha.2 does not redefine the Alpha.1 passport, authority, signature, evidence, or cumulative revocation-list contracts.

The default CLI remains stateless unless `--revocation-state PATH` is supplied. A new store is created only with `--initialize-revocation-state` after the supplied revocation list passes trust and freshness checks.

One revocation-state path is a single-writer reference continuity store. Concurrent writers to the same path are outside the supported Alpha.2 reference boundary.

## Assurance boundary

This prerelease does not provide host/database anti-rollback, credential or session termination, runtime containment, production IAM, a production policy engine, certification, legal compliance, universal interoperability, or proof that an agent is safe. Independent clean-room reproduction remains separate from repository conformance.

OPA enforcement is not included in this release and has not begun.

## Verification

The release candidate must pass the protected Python 3.11, 3.12, and 3.13 Conformance matrix, repository verification, complete pytest suite, dependency consistency and advisory audit, signed-passport trust path, generated-distribution check, Claims Register validation, and the controlled private-denylist public-release scrub.
