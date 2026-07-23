<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Release Gate

**Status:** Mandatory for every public release and prerelease.

## Gate One: Conformance

A release candidate must prove:

- Normative text, schemas, profiles, examples, and implementation agree.
- Positive, negative, adversarial, and non-regression tests pass.
- Generated distributions are current and correctly versioned.
- The schema catalog is complete, every cataloged content digest matches, and every reference resolves.
- Existing released identifiers and artifacts remain unchanged unless a versioned migration explicitly permits change.

## Gate Two: Claims and Public Boundary

A release candidate must prove:

- Claims Register validation passes, including mandatory and resolvable evidence for every `VERIFIED` claim.
- Automated prohibited-wording scans pass for declared repository path globs, and release review covers declared external surfaces.
- Every public capability statement has the correct Delivery and Evidence Status.
- Known limitations and unsupported environments are documented.
- Public examples contain only synthetic, public-safe data.
- No trade secret, credential, customer data, confidential relationship, or protected implementation detail is present.
- The canonical public project identity check passes, and a private denylist stored outside the repository reports no known matches across every tracked UTF-8 text file. Public artifacts may contain only the scrub result, accurate tracked-text scope, scrub-policy version, bounded limitations, and whether private evidence is retained. Private terms, term counts, raw denylist digests, and matching-term metadata remain in controlled private audit storage.

## Gate Three: Hosted and Reproducible Evidence

A release candidate must provide:

- Canonical commit and release tag.
- Repository, profile, schema, store, and reason-code versions as applicable.
- Schema, profile, generated-distribution, and release digests.
- Test totals and supported runtime versions.
- Dependency-audit and hosted-CI results.
- Release checksums, known limitations, and logged-out reproduction instructions.
- Independent-reproduction status stated separately and accurately.

## Hosted Platform Controls

Branch protection, required checks, secret scanning, Dependabot, and private vulnerability reporting require platform-generated evidence. Documentation alone does not establish that a hosting control is active.

## Release Blockers

A release must not proceed when:

1. A required check fails, is skipped without authorization, or cannot be reproduced.
2. Public wording exceeds the demonstrated capability or assurance boundary.
3. Specification, schema, profile, implementation, example, or generated distribution disagrees.

## Release Decision

Maintainers prepare evidence and recommend disposition. The steward approves the public tag, release status, and claim promotion. Release tooling may verify this decision but may not create it.
