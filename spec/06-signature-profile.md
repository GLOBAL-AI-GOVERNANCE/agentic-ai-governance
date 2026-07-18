<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Signature Profile

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Algorithm allowlist

Alpha.1 issuance and verification MUST use JOSE `alg = Ed25519`. Deprecated `EdDSA`, `none`, and every other algorithm MUST be rejected.

## Detached Compact JWS

Alpha.1 uses standard detached Compact JWS under RFC 7515. The protected `b64` parameter is absent, so its effective value is `true`. RFC 7797 unencoded-payload mode is prohibited.

The signing procedure is:

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

Base64url padding is omitted.

## Protected header

The protected header MUST contain exactly:

```json
{
  "alg": "Ed25519",
  "kid": "<issuer-scoped JWK thumbprint URI>",
  "typ": "atp+jws",
  "cty": "application/agent-trust-passport+json"
}
```

No unprotected header is permitted. Unknown protected-header parameters are rejected in Alpha.1.

## Key identity

Keys are resolved by `(issuer_id, kid)`. `kid` SHOULD be a JWK Thumbprint URI based on an RFC 7638 SHA-256 thumbprint.

A public Ed25519 JWK uses `kty = OKP`, `crv = Ed25519`, `alg = Ed25519`, `use = sig`, `key_ops = [verify]`, and public parameter `x`. Public key records MUST reject private parameter `d`.

## Key lifecycle

A trusted-key record identifies administrative status and validity interval. Verifiers distinguish `ACTIVE`, `RETIRED`, `REVOKED`, `COMPROMISED`, `NOT_YET_VALID`, and `EXPIRED` states and return the corresponding signing-key status.

Retired keys MAY verify artifacts issued while the key was valid only under a separately documented institutional policy with sufficient retirement-time evidence. The Alpha.1 reference validator conservatively rejects RETIRED keys. Revoked or compromised keys fail closed.

## Test keys

Private production keys MUST NOT enter the repository. Deterministic conformance vectors MAY contain explicitly labeled test-only seed material that has no operational value.

## Revocation-list protected header

Revocation lists use the same detached-JWS construction with `typ = atp-revocation+jws` and `cty = application/agent-revocation-list+json`. Verifiers MUST validate the exact protected-header key set, `alg`, `kid`, `typ`, `cty`, detached payload segment, base64url encoding, and Ed25519 signature.
