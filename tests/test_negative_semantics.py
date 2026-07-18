# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

from tools.crypto import trusted_key_errors
from tools.semantic_rules import SUPPORTED_CRITICAL_EXTENSIONS, parse_time
from tools.strict_json import load_strict
from tools.verify_repository import (
    SCHEMA_BY_KIND,
    SEMANTIC_BY_KIND,
    id_errors,
    registry,
    validate_protected_header,
    validate_schema,
)

ROOT = Path(__file__).resolve().parents[1]


def test_every_negative_fixture_is_executed_and_rejected() -> None:
    index = load_strict(ROOT / "tests/negative/index.json", require_object=True)
    listed = sorted(case["file"] for case in index["cases"])
    actual = sorted(
        path.name
        for path in (ROOT / "tests/negative").glob("*.json")
        if path.name != "index.json"
    )
    assert listed == actual

    store = registry(ROOT)
    key = load_strict(
        ROOT / "examples/trusted-keys/test-ed25519-key.json",
        require_object=True,
    )

    for case in index["cases"]:
        path = ROOT / "tests/negative" / case["file"]
        value = load_strict(path, require_object=True)
        validator = case["validator"]
        kind = case["kind"]
        rejected: list[str] = []

        if validator == "artifact":
            schema_kind = "passport" if kind == "timestamp-passport" else kind
            rejected += validate_schema(ROOT, SCHEMA_BY_KIND[schema_kind], path, store)
            semantic = SEMANTIC_BY_KIND.get(schema_kind)
            if semantic:
                rejected += semantic(value)
        elif validator == "semantic":
            rejected += SEMANTIC_BY_KIND[kind](value)
        elif validator == "identifier":
            rejected += id_errors(kind, value)
        elif validator == "protected_header":
            rejected += validate_protected_header(
                value,
                content_type="application/agent-trust-passport+json",
                type_value="atp+jws",
            )
            if value.get("kid") != key.get("kid"):
                rejected.append("protected header kid does not match trusted key")
        elif validator == "critical_extensions":
            unknown = sorted(set(value.get("critical_extensions", [])) - SUPPORTED_CRITICAL_EXTENSIONS)
            rejected += [f"unsupported critical extension: {name}" for name in unknown]
        elif validator == "version":
            if value.get("schema_version") != "0.1.0-alpha.1":
                rejected.append("unsupported schema version")
        elif validator == "trusted_key":
            rejected += trusted_key_errors(
                value,
                expected_issuer=None,
                at_time=parse_time("2026-07-18T12:00:00Z"),
            )
        else:
            raise AssertionError(f"unknown validator: {validator}")

        assert rejected, f"negative fixture accepted: {case['file']}"
