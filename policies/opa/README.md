<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# OPA Enforcement Bridge

**Status:** Current-main reference implementation; `DEFINED / VERIFIED`; unreleased.

The bridge is a deterministic policy-decision adapter. It consumes an already-established canonical Agentic validation result, a bounded request, the pinned bridge policy identity, and explicit context. It returns the existing Agentic operating-disposition vocabulary plus stable reason codes and evidence references.

```text
canonical passport / authority / revocation validation
-> established validation result
-> bounded OPA bridge input
-> PERMITTED | PERMITTED_WITH_CONDITIONS | NOT_PERMITTED
-> external enforcement system (not implemented here)
```

`tools/opa_bridge.py` validates the bridge contract and creates a reconstructable result. `bridge.rego` mirrors the bounded policy decision for OPA. The included JSON examples are synthetic. The bridge does not verify raw passports, widen validated authority, reinterpret revocation continuity, make network calls, or enforce an action.

Run the Python reference:

```bash
python tools/opa_bridge.py examples/opa/permitted-read.json
```

Run the OPA policy tests with OPA v1.19.1:

```bash
opa test policies/opa -v
```

Policy denial is not passport revocation. A policy result is not evidence of credential, session, workload, tool, or network enforcement. Gateways, IAM systems, runtimes, and tool proxies remain responsible for enforcement and evidence.
