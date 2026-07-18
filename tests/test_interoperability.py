# SPDX-License-Identifier: Apache-2.0
import pytest
from tools.canonical_json import canonicalize
from tools.semantic_rules import parse_time, validate_bundle_path, validate_protected_header


def test_rfc8785_utf16_property_order():
    value={"€":"Euro Sign","\r":"Carriage Return","דּ":"Hebrew","1":"One","😀":"Emoji","\u0080":"Control","ö":"O"}
    expected = '{"\\r":"Carriage Return","1":"One","\u0080":"Control","ö":"O","€":"Euro Sign","😀":"Emoji","דּ":"Hebrew"}'
    assert canonicalize(value).decode() == expected


def test_lone_surrogate_rejected():
    with pytest.raises(ValueError): canonicalize({"\ud800":"bad"})

@pytest.mark.parametrize('path',["a/..","a/.","C:/secret.json","e\u0301.json","a/\x7f.json","a//b","/absolute","a\\b"])
def test_unsafe_bundle_paths(path):
    assert validate_bundle_path(path)

@pytest.mark.parametrize('value',["2026-02-30T00:00:00Z","2026-13-01T00:00:00Z","2026-01-01T24:00:00Z","2026-01-01T00:00:60Z","2026-01-01T00:00:00z","2026-01-01T00:00:00+00:00","2026-01-01T00:00:00.1Z"])
def test_invalid_timestamps(value):
    with pytest.raises(ValueError): parse_time(value)


def test_wrong_typ_rejected():
    h={"alg":"Ed25519","kid":"k","typ":"wrong","cty":"application/agent-trust-passport+json"}
    assert 'unexpected typ' in validate_protected_header(h,content_type='application/agent-trust-passport+json',type_value='atp+jws')


def test_all_content_derived_identifiers_are_checked():
    from copy import deepcopy
    from pathlib import Path
    from tools.strict_json import load_strict
    from tools.verify_repository import id_errors

    root = Path(__file__).resolve().parents[1]
    cases = [
        ("bundle", "examples/bundles/valid-bundle-manifest.json", "bundle_id"),
        ("assessment", "examples/assessments/approved-readonly.json", "assessment_id"),
        ("passport", "examples/passports/signed-unrevoked.json", "passport_id"),
        ("revocation", "examples/revocation/valid-revocation-list.json", "list_id"),
    ]
    for kind, rel, field in cases:
        value = load_strict(root / rel, require_object=True)
        assert not id_errors(kind, value)
        changed = deepcopy(value)
        changed[field] = "sha256:" + "0" * 64
        assert id_errors(kind, changed)

    revocation = load_strict(root / "examples/revocation/valid-revocation-list.json", require_object=True)
    changed = deepcopy(revocation)
    changed["entries"][0]["revocation_id"] = "sha256:" + "0" * 64
    assert any("revocation_id mismatch" in error for error in id_errors("revocation", changed))
