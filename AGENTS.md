<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# AGENTS.md

Instructions for coding agents working in this repository.

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Checks (all must pass before a pull request)

```bash
python tools/build_dist.py --check
python tools/verify_repository.py .
python -m compileall -q tools tests
pytest -q
```

CI also runs `opa test policies/opa -v` and `pip_audit --strict -r requirements-dev.txt`.

## Useful commands

- `python tools/validate_artifact.py --kind passport ...` runs the reference validator. Exit 0 means PASS.
- `python tools/issue_passports.py issue examples/fleet-issuance/fleet-policy.json --out /tmp/fleet` issues a fleet's passports from a policy, unattended.
- `python tools/fleet_controls.py <request.json>` returns a fleet action decision.
- `python examples/lead-agent/lead_agent.py demo` runs the governed lead agent scenario offline.

## Rules

- Do not edit `dist/` by hand. Regenerate it with `python tools/build_dist.py`.
- Every example is synthetic. Never add real keys, identities or personal data.
- Keep the boundary wording: verification is not authorization, and every reference result has `authority_effect: NONE`.
- Do not change claim statuses, conformance vectors or pinned hashes without a decision record in `decisions/`.
