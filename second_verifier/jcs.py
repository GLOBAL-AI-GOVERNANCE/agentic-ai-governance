# SPDX-License-Identifier: Apache-2.0
"""Minimal RFC 8785 / JCS canonicalization used by the second verifier only."""
from __future__ import annotations

import math
from typing import Any


def canonicalize(value: Any) -> bytes:
    return _render(value).encode("utf-8")


def _render(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return '"' + _escape(value) + '"'
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        text = format(value, ".15g")
        return text
    if isinstance(value, list):
        return "[" + ",".join(_render(item) for item in value) + "]"
    if isinstance(value, dict):
        items = []
        for key in sorted(value.keys()):
            if not isinstance(key, str):
                raise ValueError("object keys must be strings")
            items.append(f"{_render(key)}:{_render(value[key])}")
        return "{" + ",".join(items) + "}"
    raise TypeError(f"unsupported type {type(value)!r}")


def _escape(text: str) -> str:
    out: list[str] = []
    for ch in text:
        o = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif o < 0x20:
            out.append(f"\\u{o:04x}")
        else:
            out.append(ch)
    return "".join(out)
