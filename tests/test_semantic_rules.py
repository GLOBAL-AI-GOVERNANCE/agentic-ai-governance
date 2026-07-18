# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
from pathlib import Path
from tools.strict_json import load_strict
from tools.semantic_rules import (compute_action_level,validate_action_authority_semantics,validate_agent_inventory_semantics,validate_assessment_semantics,validate_bundle_semantics,validate_data_authority_semantics,validate_mcp_inventory_semantics,validate_passport_semantics,validate_profile_descriptor_semantics,validate_revocation_semantics,validate_tool_inventory_semantics,validate_verification_semantics)
ROOT=Path(__file__).resolve().parents[1]
def load(rel): return load_strict(ROOT/rel, require_object=True)
def test_valid_examples_pass_semantic_rules():
 assert not validate_bundle_semantics(load('examples/bundles/valid-bundle-manifest.json'))
 assert not validate_passport_semantics(load('examples/passports/unsigned-valid.json'))
 assert not validate_passport_semantics(load('examples/passports/signed-revoked.json'))
 assert not validate_assessment_semantics(load('examples/assessments/approved-readonly.json'))
 assert not validate_verification_semantics(load('examples/verification/unsigned-valid-result.json'))
 assert not validate_verification_semantics(load('examples/verification/signed-valid-result.json'))
 assert not validate_revocation_semantics(load('examples/revocation/valid-revocation-list.json'))
 assert not validate_action_authority_semantics(load('examples/action-authority/readonly-graph.json'))
 assert not validate_data_authority_semantics(load('examples/data-authority/synthetic-evidence.json'))
 assert not validate_agent_inventory_semantics(load('examples/inventories/agent.json'))
 assert not validate_mcp_inventory_semantics(load('examples/inventories/mcp.json'))
 assert not validate_tool_inventory_semantics(load('examples/inventories/tools.json'))
 assert not validate_profile_descriptor_semantics(load('profiles/mcp-governance-profile.json'))
def test_reference_action_level():
 value=load('examples/action-authority/readonly-graph.json'); assert compute_action_level(value)==value['computed_level']==2


def test_unknown_data_authority_caps_assessment_at_restricted():
 value=load('examples/assessments/approved-readonly.json').copy()
 value['data_authority_status']='UNKNOWN'
 value['result']='APPROVED'
 assert 'UNKNOWN data authority cannot exceed RESTRICTED' in validate_assessment_semantics(value)
