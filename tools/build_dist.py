#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
from pathlib import Path

ORDER = [
    "00-status-and-scope.md", "01-normative-conventions.md", "02-data-and-encoding.md",
    "03-assessment-model.md", "04-verification-model.md", "05-agent-trust-passport.md",
    "06-signature-profile.md", "07-revocation.md", "08-action-authority.md",
    "09-data-authority-interop.md", "10-conformance.md", "references.md",
]


def build(root: Path) -> str:
    parts = [
        "<!-- SPDX-License-Identifier: CC-BY-4.0 -->\n",
        "# Agentic AI Governance Framework\n\n",
        "> **GENERATED FILE - DO NOT EDIT DIRECTLY**  \n",
        "> Source: `spec/`  \n",
        "> Version: `v0.1.0-alpha.1`  \n",
        "> Status: Experimental public alpha. Specification and schemas are not frozen.\n\n",
    ]
    for name in ORDER:
        text = (root / "spec" / name).read_text(encoding="utf-8")
        lines = text.splitlines()
        lines = [line for line in lines if not line.startswith("<!-- SPDX-License-Identifier:")]
        for idx, line in enumerate(lines):
            if line.startswith("# "):
                lines[idx] = "## " + line[2:]
                break
        parts.append("\n".join(lines).strip() + "\n\n")
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    target = root / "dist" / "AGENTIC_AI_GOVERNANCE_SPEC.md"
    expected = build(root)
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != expected:
            print("generated specification is stale")
            return 1
        print("generated specification is current")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(expected, encoding="utf-8", newline="\n")
    print(target)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
