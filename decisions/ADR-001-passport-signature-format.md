<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# ADR-001: Passport Signature Format

**Status:** Accepted for `v0.1.0-alpha.1`.

## Decision

Use JOSE `Ed25519` with standard detached Compact JWS under RFC 7515. The protected `b64` parameter is absent with effective value `true`. RFC 7797 unencoded-payload mode is prohibited in Alpha.1.

```text
payload_json = JCS(passport_without_proof)
payload = UTF8(payload_json)

protected_json = JCS(protected_header)
protected = UTF8(protected_json)

protected_b64 = BASE64URL(protected)
payload_b64 = BASE64URL(payload)

signing_input = ASCII(protected_b64 + "." + payload_b64)
signature = Ed25519-SIGN(private_key, signing_input)

proof.jws = protected_b64 + ".." + BASE64URL(signature)
```

The protected header contains exactly `alg`, `kid`, `typ`, and `cty`. No unprotected header and no duplicate outer cryptographic metadata are permitted.

## Consequences

The passport remains readable, the payload is not duplicated, algorithm interpretation is single-source, and deterministic test vectors are possible.
