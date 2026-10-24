<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# v0.1.0-alpha.3 Release Notes

Agentic AI Governance `v0.1.0-alpha.3` is an experimental prerelease. It makes the reference Passport validator installable with `pip` from the release tag or the release archive. Specification semantics and released schema identities are unchanged from `v0.1.0-alpha.2`.

## Install

```bash
python -m pip install "git+https://github.com/GLOBAL-AI-GOVERNANCE/agentic-ai-governance.git@v0.1.0-alpha.3"
validate-passport --example signed-unrevoked     # exit 0, artifact_validation_status PASS
validate-passport --example signed-revoked       # exit 1, verification_primary_status REVOKED
```

The release archive `agentic-ai-governance-v0.1.0-alpha.3.zip` installs the same way. It is built in GitHub Actions from the tag and ships with SHA-256 checksums and build provenance:

```bash
gh attestation verify agentic-ai-governance-v0.1.0-alpha.3.zip --repo GLOBAL-AI-GOVERNANCE/agentic-ai-governance
```

## What ships

- **Installable validator.** The `agentic_ai_governance` package and `validate-passport` command. The wheel carries the reference validator, schemas, profiles, and synthetic examples, and returns the unchanged `tools/validate_artifact.py` report.
- **Archive install test.** CI builds the sdist, wheel, and release-style source archive, installs each into a clean environment, and validates the signed example passports.
- **Validation environment.** `cryptography==50.0.1`.

## Included as references, not promoted

The release source includes the OPA Enforcement Bridge, the synthetic Agent Incident Readiness demonstration, and the Zero Trust Agent Readiness and Intelligence Assurance Gateway mappings. Under DR-010 they keep Delivery Status `DEFINED`; none is a shipped capability claim.

## Assurance boundary

Verification is not authorization. This prerelease does not provide host or database anti-rollback, credential or session termination, runtime containment, production IAM, a production policy engine, certification, legal compliance, or proof that an agent is safe. Independent verification by a separately maintained verifier remains open.

## Verification

The release commit passes the Python 3.11, 3.12, and 3.13 Conformance matrix, repository verification, the complete pytest suite, dependency consistency and advisory audit, the signed-passport trust path, the generated-distribution check, Claims Register validation, and the clean-environment package and archive installs.
