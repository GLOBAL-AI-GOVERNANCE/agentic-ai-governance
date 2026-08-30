# SPDX-License-Identifier: Apache-2.0
package agentic.opa_bridge_test

import data.agentic.opa_bridge
import rego.v1

valid_input := {
	"evaluation_time": "2026-08-30T12:05:00Z",
	"validated_result": {
		"validation_state": "ESTABLISHED",
		"verified_at": "2026-08-30T12:00:00Z",
		"valid_until": "2026-08-30T13:00:00Z",
		"primary_status": "VALID",
		"operating_disposition": "PERMITTED",
		"revocation_status": "CURRENT_NOT_REVOKED",
		"maximum_action_level": 1,
		"allowed_actions": ["read:approved-public-information"],
		"allowed_resources": ["resource.synthetic.public-catalog"],
	},
	"request": {
		"action": "read:approved-public-information",
		"resource": "resource.synthetic.public-catalog",
		"action_level": 1,
	},
	"policy": {
		"policy_id": "global-ai-governance.opa-enforcement-bridge",
		"policy_version": "1.0.0-unreleased",
		"profile_id": "global-ai-governance.mcp-governance",
		"profile_version": "0.1.0-alpha.1",
		"allowed_actions": ["read:approved-public-information"],
		"allowed_resources": ["resource.synthetic.public-catalog"],
		"denied_actions": [],
		"required_context": ["purpose"],
		"approval_required_actions": [],
		"max_validation_age_seconds": 900,
	},
	"context": {"purpose": "synthetic-public-reference-read"},
}

test_permitted if {
	result := opa_bridge.decision with input as valid_input
	result.operating_disposition == "PERMITTED"
	result.reason_codes == ["POLICY_AND_AUTHORITY_MATCH"]
	result.external_enforcement == "NOT_PERFORMED"
}

test_policy_denied_without_revocation if {
	denied := object.union(valid_input.policy, {
		"denied_actions": ["read:approved-public-information"],
	})
	candidate := object.union(valid_input, {"policy": denied})
	result := opa_bridge.decision with input as candidate
	result.operating_disposition == "NOT_PERMITTED"
	result.reason_codes == ["POLICY_DENIED"]
}

test_policy_cannot_expand_authority if {
	request := object.union(valid_input.request, {
		"action": "publish:external",
	})
	policy := object.union(valid_input.policy, {
		"allowed_actions": [
			"read:approved-public-information",
			"publish:external",
		],
	})
	candidate := object.union(valid_input, {"request": request, "policy": policy})
	result := opa_bridge.decision with input as candidate
	result.operating_disposition == "NOT_PERMITTED"
	"ACTION_OUTSIDE_AUTHORITY" in result.reason_codes
}

test_revoked_authority_is_not_permitted if {
	validated := object.union(valid_input.validated_result, {
		"primary_status": "REVOKED",
		"revocation_status": "REVOKED",
	})
	candidate := object.union(valid_input, {"validated_result": validated})
	result := opa_bridge.decision with input as candidate
	result.operating_disposition == "NOT_PERMITTED"
	"REVOCATION_NOT_CURRENT" in result.reason_codes
}

test_missing_context_is_not_permitted if {
	policy := object.union(valid_input.policy, {
		"required_context": ["missing-context"],
	})
	candidate := object.union(valid_input, {"policy": policy})
	result := opa_bridge.decision with input as candidate
	result.operating_disposition == "NOT_PERMITTED"
	"REQUIRED_CONTEXT_MISSING" in result.reason_codes
}
