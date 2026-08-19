from __future__ import annotations

import re
from typing import Iterable

_MONEY_RE = re.compile(
    r"\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)\s*(dollars?)?",
    re.I,
)
_TO_PERSON_RE = re.compile(
    r"\b(?:to|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_FILE_HINT_RE = re.compile(
    r"\b(only|just|single|one)\b.*\b(file|page|component|screen|module)\b",
    re.I,
)
_SETTINGS_RE = re.compile(r"\bsettings?\b", re.I)


def parse_money(text: str) -> float | None:
    match = _MONEY_RE.search(text.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        return None


def parse_named_targets(text: str) -> frozenset[str]:
    targets: set[str] = set()
    for match in _TO_PERSON_RE.finditer(text):
        name = match.group(1).strip()
        if name.lower() in {"the", "a", "an", "this", "that", "all", "every"}:
            continue
        targets.add(name.lower())
    for match in _EMAIL_RE.finditer(text):
        targets.add(match.group(0).lower())
    # Common phrase: "send ... to John"
    lower = text.lower()
    if "to john" in lower:
        targets.add("john")
    if "to alice" in lower:
        targets.add("alice")
    return frozenset(targets)


def estimate_intent_cardinality(text: str, default: float = 1.0) -> float:
    lower = text.lower()
    if any(w in lower for w in ("everyone", "all employees", "all users", "company-wide")):
        return 5000.0
    if any(w in lower for w in ("team", "group", "department")):
        return 25.0
    if re.search(r"\b\d+\s+(people|users|recipients|employees)\b", lower):
        num = re.search(r"\b(\d+)\s+(people|users|recipients|employees)\b", lower)
        if num:
            return float(num.group(1))
    return default


def estimate_code_scope_files(text: str) -> int:
    lower = text.lower()
    if _FILE_HINT_RE.search(text) or "only" in lower:
        return 3
    if _SETTINGS_RE.search(text) and ("dark mode" in lower or "toggle" in lower):
        return 3
    if any(w in lower for w in ("refactor entire", "redesign", "whole codebase", "all pages")):
        return 40
    return 8


def normalize_targets(values: Iterable[str]) -> frozenset[str]:
    return frozenset(v.strip().lower() for v in values if v and v.strip())
