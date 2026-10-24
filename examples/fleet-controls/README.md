<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Agent Fleet Controls Examples

Synthetic `v0.1.0-alpha.4` fleet action requests. Every identifier and digest is synthetic. Expected outcomes are pinned in `conformance/fleet-controls/manifest.json`.

```bash
python tools/fleet_controls.py examples/fleet-controls/sub-agent-spawn-permitted.json
```

The command prints the result and exits `0` when the request is `PERMITTED` and `3` when it is `NOT_PERMITTED`. The result is a decision for an enforcement point to consume; no action is taken.
