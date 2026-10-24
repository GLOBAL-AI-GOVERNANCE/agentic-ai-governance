# SPDX-License-Identifier: Apache-2.0
"""``validate-passport`` console script."""

from __future__ import annotations

import argparse
import json
import sys

from agentic_ai_governance import __version__
from agentic_ai_governance.passport import EXAMPLES, validate_example, validate_passport

BOUNDARY = (
    "Verification is not authorization. This result does not approve deployment or grant authority; "
    "an accountable human retains that decision."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate-passport",
        description="Validate an Agent Trust Passport with the Agentic AI Governance reference validator.",
        epilog=BOUNDARY,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("passport", nargs="?", help="Passport JSON file.")
    parser.add_argument("--example", choices=sorted(EXAMPLES), help="Validate a bundled synthetic example instead.")
    parser.add_argument("--trusted-key", help="Trusted Ed25519 verification-key JSON.")
    parser.add_argument("--bundle-manifest", help="Canonical bound-input bundle manifest.")
    parser.add_argument("--bundle-root", help="Directory against which bundle-manifest paths are resolved.")
    parser.add_argument("--revocation-list", help="Current signed cumulative revocation-list JSON.")
    parser.add_argument("--revocation-state", help="Trusted local revocation continuity-state JSON.")
    parser.add_argument("--initialize-revocation-state", action="store_true",
                        help="Initialize a missing --revocation-state after supplied-list trust checks pass.")
    parser.add_argument("--at-time", help="Evaluation time, YYYY-MM-DDTHH:MM:SSZ. Defaults to current UTC time.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.example:
        if args.passport:
            parser.error("give a passport file or --example, not both")
        result = validate_example(args.example)
    else:
        missing = [flag for flag, value in (("passport", args.passport), ("--trusted-key", args.trusted_key),
                                            ("--bundle-manifest", args.bundle_manifest),
                                            ("--bundle-root", args.bundle_root)) if not value]
        if missing:
            parser.error("missing required input: " + ", ".join(missing))
        result = validate_passport(
            args.passport,
            trusted_key=args.trusted_key,
            bundle_manifest=args.bundle_manifest,
            bundle_root=args.bundle_root,
            revocation_list=args.revocation_list,
            revocation_state=args.revocation_state,
            initialize_revocation_state=args.initialize_revocation_state,
            at_time=args.at_time,
        )
    json.dump(result.report, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")
    print(BOUNDARY, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
