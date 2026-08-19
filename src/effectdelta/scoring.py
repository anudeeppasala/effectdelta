from __future__ import annotations

from effectdelta.models import DeltaReport, EffectVector


def _ratio(proposed: float, intent: float) -> float:
    if intent <= 0:
        return float("inf") if proposed > 0 else 1.0
    return proposed / intent


class DeltaScorer:
    """Compare intent vs proposed effect vectors into quantitative deltas."""

    def score(self, intent: EffectVector, proposed: EffectVector) -> DeltaReport:
        intent_targets = {t.lower() for t in intent.targets}
        proposed_targets = {t.lower() for t in proposed.targets}
        destination_mismatch = bool(intent_targets) and not intent_targets.issubset(
            proposed_targets
        )

        intent_channels = {c.lower() for c in intent.channels}
        proposed_channels = {c.lower() for c in proposed.channels}
        channel_mismatch = bool(intent_channels) and not intent_channels.issubset(
            proposed_channels
        )

        return DeltaReport(
            cardinality_delta=max(0.0, proposed.cardinality - intent.cardinality),
            cardinality_ratio=_ratio(proposed.cardinality, intent.cardinality),
            destination_mismatch=destination_mismatch,
            amount_delta=max(0.0, proposed.amount - intent.amount),
            amount_ratio=_ratio(proposed.amount, intent.amount),
            scope_files_delta=max(0, proposed.scope_files - intent.scope_files),
            irreversibility_escalation=(
                proposed.irreversible and not intent.irreversible
            ),
            sensitivity_delta=max(0.0, proposed.sensitivity - intent.sensitivity),
            channel_mismatch=channel_mismatch,
            details={
                "intent_targets": sorted(intent_targets),
                "proposed_targets": sorted(proposed_targets),
                "intent_cardinality": intent.cardinality,
                "proposed_cardinality": proposed.cardinality,
                "intent_amount": intent.amount,
                "proposed_amount": proposed.amount,
                "intent_scope_files": intent.scope_files,
                "proposed_scope_files": proposed.scope_files,
            },
        )
