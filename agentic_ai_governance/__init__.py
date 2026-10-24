# SPDX-License-Identifier: Apache-2.0
"""Installable entry point for the Agentic AI Governance reference Passport validator.

Verification is not authorization. Results describe the supplied artifacts only;
an accountable human retains approval, risk acceptance, rollback, and shutdown.
"""

from agentic_ai_governance.passport import (
    EXAMPLES,
    PassportValidation,
    reference_root,
    validate_example,
    validate_passport,
)

__version__ = "0.1.0a4"

__all__ = [
    "EXAMPLES",
    "PassportValidation",
    "__version__",
    "reference_root",
    "validate_example",
    "validate_passport",
]
