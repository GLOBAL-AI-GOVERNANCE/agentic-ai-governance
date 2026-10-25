# SPDX-License-Identifier: Apache-2.0
"""``issue-passports`` and ``lead-agent`` console scripts.

Both run the reference scripts shipped with the package (``tools/issue_passports.py`` and
``examples/lead-agent/lead_agent.py``) with the current interpreter, so an installed wheel and a
source checkout behave the same.
"""

from __future__ import annotations

import subprocess
import sys

from agentic_ai_governance.passport import reference_root


def _run(relative: str, argv: list[str] | None) -> int:
    script = reference_root() / relative
    args = sys.argv[1:] if argv is None else argv
    return subprocess.call([sys.executable, str(script), *args])


def issue_passports_main(argv: list[str] | None = None) -> int:
    return _run("tools/issue_passports.py", argv)


def lead_agent_main(argv: list[str] | None = None) -> int:
    return _run("examples/lead-agent/lead_agent.py", argv)
