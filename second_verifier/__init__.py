# SPDX-License-Identifier: Apache-2.0
"""Second passport verifier implementation.

Built separately from ``tools/validate_artifact.py``. Shares normative schemas
and synthetic examples only. Same-control-boundary; not external independent
maintenance. Verification is not authorization. authority_effect remains NONE.
"""

from .verify import VerifyResult, verify_passport

__all__ = ["VerifyResult", "verify_passport"]
