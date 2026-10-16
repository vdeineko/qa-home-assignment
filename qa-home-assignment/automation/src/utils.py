"""Shared helpers for parsing values rendered in the UI."""
from __future__ import annotations

import re

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def parse_amount(text: str) -> float:
    """Extract the first numeric value from a UI label, e.g. 'Balance: €120.00' -> 120.0."""
    found = _NUMBER.search(text.replace(",", "."))
    if not found:
        raise ValueError(f"no number found in {text!r}")
    return float(found.group())
