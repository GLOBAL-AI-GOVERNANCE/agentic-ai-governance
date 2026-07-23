<!-- SPDX-License-Identifier: CC-BY-4.0 -->
## Change

## Design Validation

```text
Problem → Threat → Protected asset → Authority → Trust boundary → Evidence → Stop condition → Recovery or reauthorization
```

## Interoperability and Claims Impact

- Claims Register entries added or updated:
- Delivery Status:
- Evidence Status:
- Schema-catalog impact:
- Generated-distribution impact:
- Known limitations:

## Engineering Evidence

```text
Normative requirement → Schema or profile → Positive vector → Negative vector → Adversarial vector → Expected result
```

## Checks

- [ ] Normative precedence preserved
- [ ] Exact enum and reason-code tokens preserved
- [ ] Schema catalog updated where applicable
- [ ] Claims Register evidence requirements and automated prohibited-wording scans pass
- [ ] Positive, negative, adversarial, and non-regression evidence added
- [ ] Generated distributions rebuilt and correctly versioned
- [ ] Existing Alpha.1 identifiers and released artifacts remain unchanged
- [ ] Public examples contain only synthetic, public-safe information
- [ ] Security, legal, interoperability, and assurance claims remain bounded
- [ ] `python tools/build_dist.py --check` passes
- [ ] `python tools/verify_repository.py .` passes
- [ ] `pytest -q` passes
- [ ] `Signed-off-by` line present
