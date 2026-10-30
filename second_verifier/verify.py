# SPDX-License-Identifier: Apache-2.0
"""Second-implementation Agent Trust Passport verifier.

Does not import the reference validator under ``tools/``. Schema files under
``schemas/`` are shared normative inputs. Results always carry
``authority_effect: NONE``.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator

from .jcs import canonicalize

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
PASSPORT_SCHEMA = "agent-trust-passport.schema.json"
TRUSTED_KEY_SCHEMA = "trusted-key.schema.json"
REVOCATION_SCHEMA = "revocation-list.schema.json"
B64 = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass(frozen=True)
class VerifyResult:
    primary_status: str
    operating_disposition: str
    checks: dict[str, str]
    errors: list[str]
    authority_effect: str = "NONE"

    @property
    def ok(self) -> bool:
        return self.primary_status == "VALID" and not self.errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "primary_status": self.primary_status,
            "operating_disposition": self.operating_disposition,
            "checks": self.checks,
            "errors": list(self.errors),
            "authority_effect": self.authority_effect,
            "verifier": "second_verifier",
        }


def _b64e(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64d(value: str) -> bytes:
    if not isinstance(value, str) or not B64.fullmatch(value):
        raise ValueError("malformed base64url")
    pad = "=" * ((4 - len(value) % 4) % 4)
    decoded = base64.urlsafe_b64decode(value + pad)
    if _b64e(decoded) != value:
        raise ValueError("non-canonical base64url")
    return decoded


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"not a UTC Z timestamp: {value!r}")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _schema_store() -> dict[str, Any]:
    store: dict[str, Any] = {}
    for path in SCHEMAS.glob("*.schema.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        schema_id = doc.get("$id")
        if isinstance(schema_id, str):
            store[schema_id] = doc
        store[path.name] = doc
    return store


def _validate_schema(document: dict[str, Any], schema_name: str) -> list[str]:
    store = _schema_store()
    schema = store[schema_name]
    # Draft202012Validator resolves local $ref via the schema store registry when available.
    try:
        from referencing import Registry, Resource
        from referencing.jsonschema import DRAFT202012
        registry = Registry()
        for key, doc in store.items():
            if isinstance(doc, dict) and "$id" in doc:
                registry = registry.with_resource(doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
            if isinstance(key, str) and key.endswith(".schema.json"):
                registry = registry.with_resource(key, Resource.from_contents(doc, default_specification=DRAFT202012))
        validator = Draft202012Validator(schema, registry=registry)
    except Exception:
        validator = Draft202012Validator(schema)
    return sorted({error.message for error in validator.iter_errors(document)})


def _passport_semantics(passport: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    attestation = passport.get("assurance", {}).get("attestation_status")
    if attestation == "NONE" and "proof" in passport:
        errors.append("unsigned passport must omit proof")
    if attestation == "ISSUER_SIGNED" and "proof" not in passport:
        errors.append("signed passport requires proof")
    if "proof" in passport and set(passport["proof"]) != {"jws"}:
        errors.append("proof may contain only jws")

    conditions = passport.get("conditions", [])
    ids = [c.get("condition_id") for c in conditions]
    if ids != sorted(ids):
        errors.append("conditions must be sorted by condition_id")
    if len(ids) != len(set(ids)):
        errors.append("duplicate condition_id")

    bindings = passport.get("bindings", {})
    hashes = bindings.get("data_authority_evidence", [])
    if hashes != sorted(hashes):
        errors.append("data_authority_evidence must be sorted")
    if len(hashes) != len(set(hashes)):
        errors.append("duplicate data_authority_evidence")

    critical = passport.get("critical_extensions", [])
    if critical != sorted(critical):
        errors.append("critical_extensions must be sorted")
    extensions = passport.get("extensions", {})
    for key in critical:
        if key not in extensions:
            errors.append(f"critical extension {key} is not present")

    issued = passport.get("issued_assessment", {})
    result = issued.get("result")
    summary = issued.get("control_summary", {})
    maximum = issued.get("maximum_action_level")
    fail_count = summary.get("FAIL", 0)
    error_count = summary.get("ERROR", 0)
    not_evaluated_count = summary.get("NOT_EVALUATED", 0)
    if result == "APPROVED":
        if any((fail_count, error_count, not_evaluated_count)):
            errors.append("APPROVED requires FAIL, ERROR, and NOT_EVALUATED counts to be zero")
        if conditions:
            errors.append("APPROVED requires no conditions")
        if maximum == 5:
            errors.append("APPROVED cannot authorize Level 5 in Alpha.1")
    elif result == "APPROVED_WITH_CONDITIONS":
        if not conditions:
            errors.append("APPROVED_WITH_CONDITIONS requires at least one condition")
        if any((fail_count, error_count)):
            errors.append("APPROVED_WITH_CONDITIONS cannot contain FAIL or ERROR controls")
        if maximum == 5:
            errors.append("APPROVED_WITH_CONDITIONS cannot authorize Level 5 in Alpha.1")

    validity = passport.get("validity", {})
    if validity:
        try:
            not_before = _parse_time(validity["not_before"])
            expires_at = _parse_time(validity["expires_at"])
        except (KeyError, ValueError, TypeError) as exc:
            errors.append(f"validity timestamps: {exc}")
        else:
            if not_before >= expires_at:
                errors.append("not_before must precede expires_at")
    return errors


def _jwk_thumbprint_kid(jwk: dict[str, Any]) -> str:
    members = {"crv": jwk.get("crv"), "kty": jwk.get("kty"), "x": jwk.get("x")}
    thumb = _b64e(hashlib.sha256(canonicalize(members)).digest())
    return "urn:ietf:params:oauth:jwk-thumbprint:sha-256:" + thumb


def _trusted_key_errors(key: dict[str, Any], *, expected_issuer: str | None, at_time: datetime) -> list[str]:
    errors: list[str] = []
    if expected_issuer is not None and key.get("issuer_id") != expected_issuer:
        errors.append("trusted key issuer does not match artifact issuer")
    jwk = key.get("jwk", {})
    try:
        public_bytes = _b64d(jwk.get("x"))
        if len(public_bytes) != 32:
            raise ValueError("Ed25519 x must decode to exactly 32 bytes")
        Ed25519PublicKey.from_public_bytes(public_bytes)
    except Exception as exc:
        errors.append(f"trusted key JWK x is unusable: {exc}")
    try:
        expected_kid = _jwk_thumbprint_kid(jwk)
    except Exception as exc:
        errors.append(f"unable to calculate JWK thumbprint: {exc}")
    else:
        if key.get("kid") != expected_kid:
            errors.append("trusted key kid does not match its RFC 7638 JWK thumbprint")
    if jwk.get("alg") != "Ed25519" or key.get("allowed_algorithms") != ["Ed25519"]:
        errors.append("trusted key does not permit Ed25519")
    if jwk.get("use") != "sig" or jwk.get("key_ops") != ["verify"]:
        errors.append("trusted key is not restricted to signature verification")
    status = key.get("status")
    if status != "ACTIVE":
        errors.append(f"trusted key status is {status}")
    try:
        not_before = _parse_time(key["not_before"])
        expires_at = _parse_time(key["expires_at"])
        if at_time < not_before:
            errors.append("trusted key is not yet valid at the evaluation time")
        if at_time >= expires_at:
            errors.append("trusted key is expired at the evaluation time")
    except Exception as exc:
        errors.append(f"trusted key validity: {exc}")
    return errors


def _verify_jws(document: dict[str, Any], key: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        protected_b64, detached_payload, signature_b64 = document["proof"]["jws"].split(".")
        if detached_payload != "":
            raise ValueError("payload segment must be empty")
        protected_bytes = _b64d(protected_b64)
        header = json.loads(protected_bytes)
        if protected_bytes != canonicalize(header):
            errors.append("protected header must use JCS encoding")
        if header.get("alg") != "Ed25519":
            errors.append("protected header alg must be Ed25519")
        if header.get("typ") != "atp+jws":
            errors.append("protected header typ must be atp+jws")
        if header.get("cty") != "application/agent-trust-passport+json":
            errors.append("protected header cty mismatch")
        if header.get("kid") != key.get("kid"):
            errors.append("protected header kid does not match trusted key")
        payload = {name: value for name, value in document.items() if name != "proof"}
        payload_b64 = _b64e(canonicalize(payload))
        public_bytes = _b64d(key["jwk"]["x"])
        signature = _b64d(signature_b64)
        signing_input = (protected_b64 + "." + payload_b64).encode("ascii")
        Ed25519PublicKey.from_public_bytes(public_bytes).verify(signature, signing_input)
    except Exception as exc:
        errors.append(f"detached JWS verification failed: {exc}")
    return errors


def _validity_errors(passport: dict[str, Any], at_time: datetime) -> list[str]:
    validity = passport.get("validity", {})
    try:
        not_before = _parse_time(validity["not_before"])
        expires_at = _parse_time(validity["expires_at"])
    except Exception as exc:
        return [f"validity: {exc}"]
    errors = []
    if at_time < not_before:
        errors.append("passport is not yet valid")
    if at_time >= expires_at:
        errors.append("passport is expired")
    return errors


def _revocation_errors(passport: dict[str, Any], revocation: dict[str, Any] | None) -> list[str]:
    if revocation is None:
        return []
    passport_id = passport.get("passport_id")
    for entry in revocation.get("entries", []):
        if entry.get("passport_id") == passport_id:
            return [f"passport is revoked: {entry.get('reason', 'revoked')}"]
    return []


def _file_digest(path: Path, canonicalization: str) -> str:
    raw = path.read_bytes()
    if canonicalization == "EXACT_BYTES":
        return "sha256:" + hashlib.sha256(raw).hexdigest()
    if canonicalization != "JCS":
        raise ValueError(f"unsupported canonicalization: {canonicalization}")
    return "sha256:" + hashlib.sha256(canonicalize(json.loads(raw))).hexdigest()


def _bundle_binding_errors(passport: dict[str, Any], manifest: dict[str, Any], bundle_root: Path) -> list[str]:
    errors: list[str] = []
    bindings = passport.get("bindings", {})
    if bindings.get("assessment_bundle") != manifest.get("bundle_id"):
        errors.append("passport assessment_bundle does not equal the supplied manifest bundle_id")
    root = bundle_root.resolve()
    digests_by_path: dict[str, str] = {}
    for entry in manifest.get("files", []):
        rel = entry.get("path")
        want = entry.get("hash")
        canon = entry.get("canonicalization", "JCS")
        if not isinstance(rel, str) or not isinstance(want, str):
            errors.append("bundle file entry missing path or hash")
            continue
        path = (root / rel).resolve()
        if root not in path.parents and path != root:
            errors.append(f"bundle path escapes root: {rel}")
            continue
        if not path.is_file():
            errors.append(f"missing bound artifact: {rel}")
            continue
        try:
            got = _file_digest(path, canon)
        except Exception as exc:
            errors.append(f"unable to digest {rel}: {exc}")
            continue
        if got != want:
            errors.append(f"bound artifact digest mismatch: {rel}")
        digests_by_path[rel] = got
    # Cross-check selected passport binding digests against manifest files when present.
    mapping = {
        "agent_inventory": "examples/inventories/agent.json",
        "mcp_inventory": "examples/inventories/mcp.json",
        "tool_inventory": "examples/inventories/tools.json",
        "action_authority_graph": "examples/action-authority/readonly-graph.json",
        "control_profile": "profiles/mcp-governance-profile.md",
    }
    for key, rel in mapping.items():
        expected = bindings.get(key)
        if expected and rel in digests_by_path and digests_by_path[rel] != expected:
            errors.append(f"passport binding {key} does not match bundle file digest")
    return errors


def verify_passport(
    passport_path: str | Path,
    *,
    trusted_key: str | Path,
    bundle_manifest: str | Path,
    bundle_root: str | Path,
    revocation_list: str | Path | None = None,
    at_time: str = "2026-07-18T12:00:00Z",
) -> VerifyResult:
    checks = {
        "structure": "NOT_RUN",
        "semantics": "NOT_RUN",
        "signature": "NOT_RUN",
        "signing_key_trust": "NOT_RUN",
        "bindings": "NOT_RUN",
        "validity": "NOT_RUN",
        "revocation": "NOT_RUN",
    }
    errors: list[str] = []
    when = _parse_time(at_time)

    try:
        passport = _load_json(Path(passport_path))
        key = _load_json(Path(trusted_key))
        manifest = _load_json(Path(bundle_manifest))
        revocation = _load_json(Path(revocation_list)) if revocation_list else None
    except Exception as exc:
        return VerifyResult("INVALID", "NOT_PERMITTED", checks, [str(exc)])

    schema_errors = _validate_schema(passport, PASSPORT_SCHEMA)
    if schema_errors:
        checks["structure"] = "FAIL"
        return VerifyResult("INVALID", "NOT_PERMITTED", checks, schema_errors)
    checks["structure"] = "PASS"

    key_schema_errors = _validate_schema(key, TRUSTED_KEY_SCHEMA)
    if key_schema_errors:
        checks["signing_key_trust"] = "FAIL"
        return VerifyResult("INDETERMINATE", "NOT_PERMITTED", checks, key_schema_errors)

    if revocation is not None:
        rev_schema_errors = _validate_schema(revocation, REVOCATION_SCHEMA)
        if rev_schema_errors:
            checks["revocation"] = "FAIL"
            return VerifyResult("INDETERMINATE", "NOT_PERMITTED", checks, rev_schema_errors)

    semantic_errors = _passport_semantics(passport)
    if semantic_errors:
        checks["semantics"] = "FAIL"
        return VerifyResult("INVALID", "NOT_PERMITTED", checks, semantic_errors)
    checks["semantics"] = "PASS"

    if "proof" in passport:
        sig_errors = _verify_jws(passport, key)
        if sig_errors:
            checks["signature"] = "FAIL"
            return VerifyResult("INVALID", "NOT_PERMITTED", checks, sig_errors)
        checks["signature"] = "PASS"
        trust_errors = _trusted_key_errors(
            key, expected_issuer=passport.get("issuer_id"), at_time=when
        )
        if trust_errors:
            checks["signing_key_trust"] = "FAIL"
            return VerifyResult("INDETERMINATE", "NOT_PERMITTED", checks, trust_errors)
        checks["signing_key_trust"] = "PASS"
    else:
        checks["signature"] = "NOT_APPLICABLE"
        checks["signing_key_trust"] = "NOT_APPLICABLE"

    binding_errors = _bundle_binding_errors(passport, manifest, Path(bundle_root))
    if binding_errors:
        checks["bindings"] = "FAIL"
        return VerifyResult("INVALID", "NOT_PERMITTED", checks, binding_errors)
    checks["bindings"] = "PASS"

    validity_errors = _validity_errors(passport, when)
    if validity_errors:
        checks["validity"] = "FAIL"
        return VerifyResult("INVALID", "NOT_PERMITTED", checks, validity_errors)
    checks["validity"] = "PASS"

    revocation_errors = _revocation_errors(passport, revocation)
    if revocation_errors:
        checks["revocation"] = "FAIL"
        return VerifyResult("REVOKED", "NOT_PERMITTED", checks, revocation_errors)
    checks["revocation"] = "PASS" if revocation is not None else "NOT_RUN"

    return VerifyResult("VALID", "PERMITTED", checks, [])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Second-implementation passport verifier.")
    parser.add_argument("passport")
    parser.add_argument("--trusted-key", required=True)
    parser.add_argument("--bundle-manifest", required=True)
    parser.add_argument("--bundle-root", required=True)
    parser.add_argument("--revocation-list")
    parser.add_argument("--at-time", default="2026-07-18T12:00:00Z")
    args = parser.parse_args(argv)
    result = verify_passport(
        args.passport,
        trusted_key=args.trusted_key,
        bundle_manifest=args.bundle_manifest,
        bundle_root=args.bundle_root,
        revocation_list=args.revocation_list,
        at_time=args.at_time,
    )
    json.dump(result.as_dict(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
