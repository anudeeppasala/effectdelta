from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Callable, Iterable

from effectdelta.adapters.base import ActionAdapter
from effectdelta.models import Action, EffectVector

PathExpander = Callable[[str], list[str]]


def default_path_expander(pattern: str) -> list[str]:
    """Expand globs against a tiny virtual FS for offline demos."""
    virtual = [
        "src/app.py",
        "src/settings.py",
        "src/settings/theme.py",
        "src/components/Button.tsx",
        "src/pages/Settings.tsx",
        "src/pages/Home.tsx",
        "src/pages/Dashboard.tsx",
        "data/users.csv",
        "data/orders.csv",
        "logs/app.log",
        "secrets/prod.env",
    ]
    if any(ch in pattern for ch in "*?[]"):
        return [p for p in virtual if fnmatch.fnmatch(p, pattern)]
    # directory-style
    if pattern.endswith("/"):
        return [p for p in virtual if p.startswith(pattern)]
    return [pattern]


class FileAdapter(ActionAdapter):
    kind = "file"

    def __init__(self, expander: PathExpander | None = None) -> None:
        self.expander = expander or default_path_expander

    def intent_effect(self, action: Action) -> EffectVector:
        lower = action.intent.lower()
        if "all" in lower or "entire" in lower or "*" in lower:
            cardinality = 100.0
        else:
            cardinality = float(action.payload.get("intent_file_count", 1))
        return EffectVector(
            cardinality=cardinality,
            targets=frozenset({"workspace"}),
            irreversible="delete" in lower or "remove" in lower,
            resource_type="file",
            sensitivity=0.5,
            scope_files=int(cardinality),
            environment=str(action.payload.get("environment", "local")),
        )

    def proposed_effect(self, action: Action) -> EffectVector:
        patterns = action.payload.get("paths") or action.payload.get("path") or []
        if isinstance(patterns, str):
            patterns = [patterns]
        files = _unique(self._expand_all(patterns))
        op = str(action.payload.get("operation", "write")).lower()
        return EffectVector(
            cardinality=float(len(files)),
            targets=frozenset(files[:50]),
            irreversible=op in {"delete", "remove", "unlink"},
            resource_type="file",
            sensitivity=0.9 if any("secret" in f for f in files) else 0.5,
            scope_files=len(files),
            environment=str(action.payload.get("environment", "local")),
            notes=(f"expanded to {len(files)} path(s)",),
        )

    def _expand_all(self, patterns: Iterable[str]) -> list[str]:
        out: list[str] = []
        for pattern in patterns:
            # Prefer real FS if pattern exists; fall back to virtual expander
            path = Path(pattern)
            if any(ch in pattern for ch in "*?[]"):
                matched = [str(p) for p in Path().glob(pattern)]
                out.extend(matched or self.expander(pattern))
            elif path.exists():
                if path.is_dir():
                    out.extend(str(p) for p in path.rglob("*") if p.is_file())
                else:
                    out.append(str(path))
            else:
                out.extend(self.expander(pattern))
        return out


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
