from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from effectdelta.models import DeltaReport, Verdict

OnBreach = Literal["allow", "approve", "block"]


@dataclass
class Rule:
    """User-defined threshold. First matching breach with highest severity wins later in Gate."""

    name: str = "rule"
    max_cardinality_ratio: float | None = None
    max_cardinality_delta: float | None = None
    forbid_destination_mismatch: bool = False
    max_amount_ratio: float | None = None
    max_amount_delta: float | None = None
    max_scope_files: int | None = None
    max_scope_files_delta: int | None = None
    forbid_irreversibility_escalation: bool = False
    max_sensitivity_delta: float | None = None
    forbid_channel_mismatch: bool = False
    on_breach: OnBreach = "block"

    def check(self, deltas: DeltaReport, proposed_scope_files: int = 0) -> str | None:
        """Return breach message if this rule is violated, else None."""
        if (
            self.max_cardinality_ratio is not None
            and deltas.cardinality_ratio > self.max_cardinality_ratio
        ):
            return (
                f"{self.name}: cardinality ratio "
                f"{deltas.cardinality_ratio:.2f} > {self.max_cardinality_ratio}"
            )
        if (
            self.max_cardinality_delta is not None
            and deltas.cardinality_delta > self.max_cardinality_delta
        ):
            return (
                f"{self.name}: cardinality delta "
                f"{deltas.cardinality_delta} > {self.max_cardinality_delta}"
            )
        if self.forbid_destination_mismatch and deltas.destination_mismatch:
            return f"{self.name}: destination mismatch"
        if (
            self.max_amount_ratio is not None
            and deltas.amount_ratio > self.max_amount_ratio
        ):
            return (
                f"{self.name}: amount ratio "
                f"{deltas.amount_ratio:.2f} > {self.max_amount_ratio}"
            )
        if (
            self.max_amount_delta is not None
            and deltas.amount_delta > self.max_amount_delta
        ):
            return (
                f"{self.name}: amount delta "
                f"{deltas.amount_delta} > {self.max_amount_delta}"
            )
        if (
            self.max_scope_files is not None
            and proposed_scope_files > self.max_scope_files
        ):
            return (
                f"{self.name}: scope files "
                f"{proposed_scope_files} > {self.max_scope_files}"
            )
        if (
            self.max_scope_files_delta is not None
            and deltas.scope_files_delta > self.max_scope_files_delta
        ):
            return (
                f"{self.name}: scope files delta "
                f"{deltas.scope_files_delta} > {self.max_scope_files_delta}"
            )
        if self.forbid_irreversibility_escalation and deltas.irreversibility_escalation:
            return f"{self.name}: irreversibility escalation"
        if (
            self.max_sensitivity_delta is not None
            and deltas.sensitivity_delta > self.max_sensitivity_delta
        ):
            return (
                f"{self.name}: sensitivity delta "
                f"{deltas.sensitivity_delta} > {self.max_sensitivity_delta}"
            )
        if self.forbid_channel_mismatch and deltas.channel_mismatch:
            return f"{self.name}: channel mismatch"
        return None

    def verdict(self) -> Verdict:
        return Verdict(self.on_breach)


_SEVERITY = {Verdict.ALLOW: 0, Verdict.APPROVE: 1, Verdict.BLOCK: 2}


def worst_verdict(current: Verdict, candidate: Verdict) -> Verdict:
    return candidate if _SEVERITY[candidate] > _SEVERITY[current] else current
