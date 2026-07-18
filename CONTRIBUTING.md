<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Contributing

Public issues and pull requests are welcome for specification defects, interoperability concerns, schemas, examples, profiles, and conformance tests.

## Before opening a pull request

1. Update normative text when behavior changes.
2. Add positive and negative evidence for every changed rule.
3. Run `python tools/verify_repository.py .` and `pytest -q`.
4. Rebuild the generated specification when `spec/` changes.

## Sign-off

The pull-request template requests a `Signed-off-by` line under the Developer Certificate of Origin. Add it automatically with:

```bash
git commit --signoff
```

The sign-off states that you have the right to submit the contribution under the repository's licenses. Read the [Developer Certificate of Origin 1.1](https://developercertificate.org/).

Security vulnerabilities must follow [SECURITY.md](SECURITY.md), not a public issue.
