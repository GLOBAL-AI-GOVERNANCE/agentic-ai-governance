<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Fleet passport issuance from a policy file

[`tools/issue_passports.py`](../../tools/issue_passports.py) issues a signed Agent Trust Passport for every agent in a policy file, binds each sub-agent to its parent, writes a signed revocation list, and validates every passport with the reference validator. It needs no manual step, so it can run in CI or at agent start-up.

```bash
python tools/issue_passports.py issue examples/fleet-issuance/fleet-policy.json --out fleet/   # exit 0 when every passport is VALID
python tools/issue_passports.py revoke <passport_id> --out fleet/                              # re-signs the cumulative list
python tools/issue_passports.py refresh --out fleet/                                           # keeps the list fresh
```

From an installed package the command is `issue-passports`.

The policy refuses escalation. It rejects Level 5, `spend_funds`, a sub-agent above its parent's level or terms, delegation below Level 3, and tools or capabilities above an agent's level. `fleet/signing-key.json` holds the private key with mode 0600. Keep it out of version control. Issued passports use the synthetic, non-production reference profile and are for testing. They do not authorize anything.
