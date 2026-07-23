<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Contributing

Public issues and pull requests are welcome for specification defects, interoperability concerns, schemas, examples, profiles, governance controls, and conformance tests.

## Normative Precedence

Contributions must follow the precedence recorded in [PROGRAM_BASELINE.md](governance/PROGRAM_BASELINE.md). A README, example, implementation detail, or test helper may not silently override a versioned schema, normative specification, profile, or accepted decision record.

## Before Opening a Pull Request

1. Identify the problem, threat, authority, trust boundary, evidence, stop condition, and recovery or reauthorization path.
2. Update normative text, schemas, profiles, the schema catalog, Claims Register, and prohibited claims where applicable.
3. Add positive, negative, adversarial, and non-regression evidence for every changed rule.
4. Run `python tools/build_dist.py --check`, `python tools/verify_repository.py .`, and `pytest -q`.
5. Confirm public examples contain only synthetic, public-safe information.

Claims must use only the approved Delivery and Evidence statuses. External facts omit Delivery Status. A capability must not be promoted beyond its released implementation and exact supporting evidence.

Governance files ending in `.yaml` use the JSON-compatible subset of YAML 1.2 and are loaded with the standard Python JSON parser. Automated prohibited-claim scanning performs case-insensitive exact-phrase matching over the repository path globs declared in `governance/prohibited-claims.yaml`. It does not detect semantic paraphrases, punctuation changes, or split phrases, so human release review remains mandatory for repository and external surfaces. Repository-relative supporting artifacts and local evidence references must exist inside the working tree; remote evidence references are syntax-checked without network retrieval.

## Generated Distributions

Alpha.1 remains an immutable versioned distribution. New specification or profile material must use a separately versioned generated artifact and must not be inserted into an aggregate still identified as Alpha.1.

## Sign-Off

The pull-request template requests a `Signed-off-by` line under the Developer Certificate of Origin. Add it automatically with:

```bash
git commit --signoff
```

The sign-off states that you have the right to submit the contribution under the repository's licenses. Read the [Developer Certificate of Origin 1.1](https://developercertificate.org/).

Security vulnerabilities must follow [SECURITY.md](SECURITY.md), not a public issue.
