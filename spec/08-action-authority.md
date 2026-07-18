<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Action Authority

**Version:** `v0.1.0-alpha.1`  
**Status:** Experimental public alpha. Not frozen.

## Levels

- Level 0: advisory output with no external execution capability.
- Level 1: read-only access to approved information.
- Level 2: drafting or proposing changes without submission or execution.
- Level 3: bounded, logged, reversible internal action with defined rollback.
- Level 4: privileged or externally consequential action affecting production, identities, sensitive data, external communications, security controls, or material business processes.
- Level 5: destructive, financial, legal, employment, human-safety, critical-infrastructure, mission-critical, or irreversible high-impact consequence.

## Reachable action graph

Authority is calculated from the complete reachable action graph, not isolated tool labels. The graph includes agents, subagents, tools, resources, data paths, approval gates, and execution edges.

An implementation MUST evaluate every authority dimension represented by the applicable schema and governance profile. Alpha.1’s reference calculation is limited to the fields defined in the Alpha.1 action-authority graph. Future profiles may add batch size, transaction value, frequency, tool installation or chaining, reversibility time, rollback completeness, and human-approval strength as explicit schema inputs.

A chain is assigned at least the maximum consequence reachable through any permitted path. Composition MAY raise the level above every individually declared tool level.


## Alpha.1 reference calculation

The reference calculation starts with the maximum of `requested_level` and every `base_level` reachable from the declared `agent_id`. It then applies these minimum floors:

- delegation, unattended execution, or code execution: Level 3;
- credential change, identity change, external publication, data movement, no reversibility, organizational or external blast radius: Level 4;
- self-modification or critical blast radius: Level 5;
- partial reversibility or team blast radius: Level 3.

`computed_level` MUST equal the maximum resulting level. Node identifiers MUST be unique, the declared agent node MUST exist and have type `AGENT`, every edge endpoint MUST exist, duplicate edges are prohibited, and every declared node MUST be reachable from the agent node.

## Alpha.1 Level 5 rule

No Alpha.1 profile may issue `APPROVED` or `APPROVED_WITH_CONDITIONS` for requested Level 5 authority. A Level 5 request produces `RESTRICTED` or `REJECTED` according to the specific action and profile.

Assessment of a Level 5 declaration does not authorize the action.


## Passport binding

A passport that carries action authority MUST bind one action-authority graph through the canonical bundle manifest. The verifier MUST validate the graph, recalculate `computed_level`, require the graph agent to equal the passport subject, require graph tool nodes and tool-inventory declarations to agree, and require the calculated level not to exceed the bound assessment or passport maximum. A Level 5 graph cannot support a permitted Alpha.1 disposition.
## Alpha.1 controlled authority vocabulary

The reference profile restricts agent capabilities, MCP scopes, and tool effects to versioned controlled vocabularies with deterministic minimum action levels. Every declared MCP server MUST appear as a reachable `MCP_SERVER` node. The node level MUST cover every declared server scope. Tool effects and agent capabilities MUST NOT require a level above the graph's reproducible `computed_level`. Unknown terms fail schema validation.

Reachable graph edge types also contribute minimum authority. A `PUBLISHES` edge requires `dimensions.external_publication=true` and Level 4 or higher. A `DELEGATES` edge requires `dimensions.delegation=true` and Level 3 or higher.

For `APPROVED_WITH_CONDITIONS`, the effective maximum action level is the minimum of the assessment maximum, passport maximum, and every active condition's temporary maximum. The graph MUST NOT exceed that effective ceiling.

