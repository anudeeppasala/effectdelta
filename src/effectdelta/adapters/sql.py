from __future__ import annotations

import re
from typing import Callable

from effectdelta.adapters.base import ActionAdapter
from effectdelta.models import Action, EffectVector

RowEstimator = Callable[[str], int]

_MUTATING = re.compile(
    r"^\s*(DELETE|UPDATE|DROP|TRUNCATE|ALTER)\b",
    re.I | re.S,
)
_FROM_TABLE = re.compile(r"\bFROM\s+([A-Za-z_][\w]*)", re.I)
_UPDATE_TABLE = re.compile(r"\bUPDATE\s+([A-Za-z_][\w]*)", re.I)
_WHERE = re.compile(r"\bWHERE\b", re.I)


def default_row_estimator(sql: str) -> int:
    """Offline estimate: COUNT-style stand-in without executing mutation."""
    text = sql.strip()
    upper = text.upper()
    if upper.startswith("DROP") or upper.startswith("TRUNCATE"):
        return 1_000_000
    if not _WHERE.search(text):
        return 50_000
    # id = N style → 1 row; IN list → N; otherwise moderate
    if re.search(r"\bid\s*=\s*\d+\b", text, re.I):
        return 1
    in_list = re.search(r"\bIN\s*\(([^)]*)\)", text, re.I)
    if in_list:
        parts = [p for p in in_list.group(1).split(",") if p.strip()]
        return max(1, len(parts))
    return 250


class SqlAdapter(ActionAdapter):
    kind = "sql"

    def __init__(self, estimator: RowEstimator | None = None) -> None:
        self.estimator = estimator or default_row_estimator

    def intent_effect(self, action: Action) -> EffectVector:
        # Prefer explicit intent hints in payload, else conservative single-row
        wanted = action.payload.get("intent_row_count")
        if wanted is None:
            lower = action.intent.lower()
            if "all" in lower or "entire" in lower:
                wanted = 50_000
            elif re.search(r"\b\d+\s+rows?\b", lower):
                m = re.search(r"\b(\d+)\s+rows?\b", lower)
                wanted = int(m.group(1)) if m else 1
            else:
                wanted = 1
        return EffectVector(
            cardinality=float(wanted),
            targets=frozenset({str(action.payload.get("table", "table"))}),
            irreversible=_looks_irreversible(action.intent),
            resource_type="sql",
            sensitivity=0.8,
            environment=str(action.payload.get("environment", "prod")),
        )

    def proposed_effect(self, action: Action) -> EffectVector:
        sql = str(action.payload.get("sql", ""))
        table = _extract_table(sql) or str(action.payload.get("table", "unknown"))
        rows = self.estimator(sql)
        irreversible = bool(_MUTATING.match(sql)) and (
            sql.strip().upper().startswith(("DELETE", "DROP", "TRUNCATE"))
        )
        return EffectVector(
            cardinality=float(rows),
            targets=frozenset({table.lower()}),
            irreversible=irreversible,
            resource_type="sql",
            sensitivity=0.95 if rows > 1000 else 0.7,
            environment=str(action.payload.get("environment", "prod")),
            notes=("non-mutating row estimate via probe",),
        )


def _extract_table(sql: str) -> str | None:
    m = _FROM_TABLE.search(sql) or _UPDATE_TABLE.search(sql)
    return m.group(1) if m else None


def _looks_irreversible(intent: str) -> bool:
    lower = intent.lower()
    return any(w in lower for w in ("delete", "drop", "truncate", "remove permanently"))
