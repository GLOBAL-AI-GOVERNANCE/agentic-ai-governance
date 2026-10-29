<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Second verifier

A second Agent Trust Passport verifier implementation maintained in this
repository, built separately from `tools/validate_artifact.py`.

It shares normative schemas and synthetic examples only. It does not import the
reference validator. Results keep `authority_effect: NONE`. Verification is not
authorization. Same-control-boundary work; it does not satisfy an external
independent-maintenance gate by itself.

```bash
python -m second_verifier \
  examples/passports/signed-unrevoked.json \
  --trusted-key examples/trusted-keys/test-ed25519-key.json \
  --bundle-manifest examples/bundles/valid-bundle-manifest.json \
  --bundle-root . \
  --revocation-list examples/revocation/valid-revocation-list.json \
  --at-time 2026-07-18T12:00:00Z
```
