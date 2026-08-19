from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    ALLOW = "allow"
    APPROVE = "approve"
    BLOCK = "block"


@dataclass
class Action:
    """Universal input: what the human wanted + what is about to run."""

    intent: str
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EffectVector:
    """Structured blast-radius description of an action."""

    cardinality: float = 0.0
    targets: frozenset[str] = field(default_factory=frozenset)
    irreversible: bool = False
    resource_type: str = "unknown"
    sensitivity: float = 0.0  # 0.0 low .. 1.0 critical
    environment: str = "unknown"
    scope_files: int = 0
    amount: float = 0.0
    channels: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = ()

    def with_notes(self, *extra: str) -> EffectVector:
        return EffectVector(
            cardinality=self.cardinality,
            targets=self.targets,
            irreversible=self.irreversible,
            resource_type=self.resource_type,
            sensitivity=self.sensitivity,
            environment=self.environment,
            scope_files=self.scope_files,
            amount=self.amount,
            channels=self.channels,
            notes=self.notes + extra,
        )


@dataclass
class DeltaReport:
    cardinality_delta: float = 0.0
    cardinality_ratio: float = 1.0
    destination_mismatch: bool = False
    amount_delta: float = 0.0
    amount_ratio: float = 1.0
    scope_files_delta: int = 0
    irreversibility_escalation: bool = False
    sensitivity_delta: float = 0.0
    channel_mismatch: bool = False
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    verdict: Verdict
    reason: str
    intent_effect: EffectVector
    proposed_effect: EffectVector
    deltas: DeltaReport
    breached_rules: tuple[str, ...] = ()

    @property
    def action(self) -> str:
        """Alias used in demos/docs."""
        return self.verdict.value

    def raise_if_blocked(self) -> None:
        if self.verdict is Verdict.BLOCK:
            from effectdelta.wrap import ActionBlocked

            raise ActionBlocked(self)
