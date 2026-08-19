from __future__ import annotations

import re
from typing import Any

from effectdelta.adapters.base import ActionAdapter
from effectdelta.intent import estimate_code_scope_files, parse_named_targets
from effectdelta.models import Action, EffectVector

_AREA_RE = re.compile(
    r"\b(settings|dashboard|home|auth|billing|api|design system|theme)\b",
    re.I,
)


class CodeChangeAdapter(ActionAdapter):
    """Compare requirements scope vs proposed diff/file blast radius.

    Designed for manual Cursor/feature workflows:
      gate.check(Action(intent=requirements, kind="code_change", payload={...}))
    """

    kind = "code_change"

    def intent_effect(self, action: Action) -> EffectVector:
        scope = estimate_code_scope_files(action.intent)
        areas = frozenset(m.group(1).lower() for m in _AREA_RE.finditer(action.intent))
        targets = areas or parse_named_targets(action.intent) or frozenset({"app"})
        return EffectVector(
            cardinality=float(scope),
            targets=targets,
            irreversible=False,
            resource_type="code",
            sensitivity=0.4,
            scope_files=scope,
            environment=str(action.payload.get("environment", "dev")),
            notes=("intent scope inferred from requirements text",),
        )

    def proposed_effect(self, action: Action) -> EffectVector:
        files = _as_file_list(action.payload)
        summary = str(action.payload.get("diff_summary", "")).lower()
        areas = _areas_from_files(files)
        if "design system" in summary or "entire" in summary or "redesign" in summary:
            # Inflate if summary screams broad refactor even when file list is partial
            scope = max(len(files), 40)
        else:
            scope = len(files) or int(action.payload.get("files_changed_count", 0))

        sensitivity = 0.4
        if any(
            part in "/".join(files).lower()
            for part in ("auth", "billing", "secret", "migration")
        ):
            sensitivity = 0.8

        return EffectVector(
            cardinality=float(scope),
            targets=areas or frozenset({"app"}),
            irreversible=bool(action.payload.get("breaking", False)),
            resource_type="code",
            sensitivity=sensitivity,
            scope_files=scope,
            environment=str(action.payload.get("environment", "dev")),
            notes=(f"proposed touch set: {scope} file(s)",),
        )


def _as_file_list(payload: dict[str, Any]) -> list[str]:
    files = payload.get("files_changed") or payload.get("files") or []
    if isinstance(files, str):
        return [files]
    return [str(f) for f in files]


def _areas_from_files(files: list[str]) -> frozenset[str]:
    areas: set[str] = set()
    for path in files:
        lower = path.lower()
        for area in ("settings", "dashboard", "home", "auth", "billing", "theme"):
            if area in lower:
                areas.add(area)
        if "design" in lower:
            areas.add("design system")
    return frozenset(areas)
