# SPDX-License-Identifier: Apache-2.0
package agentic.opa_bridge

import rego.v1

default decision := {
	"operating_disposition": "NOT_PERMITTED",
	"reason_codes": ["BRIDGE_INPUT_INVALID"],
	"external_enforcement": "NOT_PERFORMED",
}

deny_reasons contains "POLICY_UNSUPPORTED" if {
	input.policy.policy_id != "global-ai-governance.opa-enforcement-bridge"
}

deny_reasons contains "POLICY_UNSUPPORTED" if {
	input.policy.policy_version != "1.0.0-unreleased"
}

deny_reasons contains "PROFILE_UNSUPPORTED" if {
	input.policy.profile_id != "global-ai-governance.mcp-governance"
}

deny_reasons contains "PROFILE_UNSUPPORTED" if {
	input.policy.profile_version != "0.1.0-alpha.1"
}

deny_reasons contains "VALIDATION_NOT_ESTABLISHED" if {
	input.validated_result.validation_state != "ESTABLISHED"
}

deny_reasons contains "CANONICAL_VALIDATION_NOT_VALID" if {
	input.validated_result.primary_status != "VALID"
}

deny_reasons contains "CANONICAL_DISPOSITION_NOT_PERMITTED" if {
	not input.validated_result.operating_disposition in {
		"PERMITTED",
		"PERMITTED_WITH_CONDITIONS",
	}
}

deny_reasons contains "REVOCATION_NOT_CURRENT" if {
	input.validated_result.revocation_status != "CURRENT_NOT_REVOKED"
}

deny_reasons contains "VALIDATION_OUTSIDE_VALIDITY" if {
	evaluated := time.parse_rfc3339_ns(input.evaluation_time)
	verified := time.parse_rfc3339_ns(input.validated_result.verified_at)
	evaluated < verified
}

deny_reasons contains "VALIDATION_OUTSIDE_VALIDITY" if {
	evaluated := time.parse_rfc3339_ns(input.evaluation_time)
	valid_until := time.parse_rfc3339_ns(input.validated_result.valid_until)
	evaluated >= valid_until
}

deny_reasons contains "VALIDATION_STALE" if {
	evaluated := time.parse_rfc3339_ns(input.evaluation_time)
	verified := time.parse_rfc3339_ns(input.validated_result.verified_at)
	evaluated >= verified
	(evaluated - verified) / 1000000000 > input.policy.max_validation_age_seconds
}

deny_reasons contains "ACTION_LEVEL_EXCEEDS_AUTHORITY" if {
	input.request.action_level > input.validated_result.maximum_action_level
}

deny_reasons contains "ACTION_OUTSIDE_AUTHORITY" if {
	not input.request.action in input.validated_result.allowed_actions
}

deny_reasons contains "RESOURCE_OUTSIDE_AUTHORITY" if {
	not input.request.resource in input.validated_result.allowed_resources
}

deny_reasons contains "POLICY_DENIED" if {
	input.request.action in input.policy.denied_actions
}

deny_reasons contains "ACTION_NOT_ALLOWED_BY_POLICY" if {
	not input.request.action in input.policy.allowed_actions
}

deny_reasons contains "RESOURCE_NOT_ALLOWED_BY_POLICY" if {
	not input.request.resource in input.policy.allowed_resources
}

deny_reasons contains "REQUIRED_CONTEXT_MISSING" if {
	some required in input.policy.required_context
	object.get(input.context, required, "__OPA_CONTEXT_MISSING__") == "__OPA_CONTEXT_MISSING__"
}

approval_required if {
	input.request.action in input.policy.approval_required_actions
}

decision := {
	"operating_disposition": "NOT_PERMITTED",
	"reason_codes": sort([code | deny_reasons[code]]),
	"external_enforcement": "NOT_PERFORMED",
} if {
	count(deny_reasons) > 0
}

decision := {
	"operating_disposition": "PERMITTED_WITH_CONDITIONS",
	"reason_codes": ["POLICY_APPROVAL_REQUIRED"],
	"external_enforcement": "NOT_PERFORMED",
} if {
	count(deny_reasons) == 0
	approval_required
}

decision := {
	"operating_disposition": "PERMITTED_WITH_CONDITIONS",
	"reason_codes": ["CANONICAL_CONDITIONS_RETAINED"],
	"external_enforcement": "NOT_PERFORMED",
} if {
	count(deny_reasons) == 0
	not approval_required
	input.validated_result.operating_disposition == "PERMITTED_WITH_CONDITIONS"
}

decision := {
	"operating_disposition": "PERMITTED",
	"reason_codes": ["POLICY_AND_AUTHORITY_MATCH"],
	"external_enforcement": "NOT_PERFORMED",
} if {
	count(deny_reasons) == 0
	not approval_required
	input.validated_result.operating_disposition == "PERMITTED"
}
