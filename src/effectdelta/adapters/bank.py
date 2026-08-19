from __future__ import annotations

from effectdelta.adapters.base import ActionAdapter
from effectdelta.intent import parse_money, parse_named_targets
from effectdelta.models import Action, EffectVector


class BankTransferAdapter(ActionAdapter):
    """Example banking adapter — companies replace resolver with real account services."""

    kind = "bank_transfer"

    def intent_effect(self, action: Action) -> EffectVector:
        amount = parse_money(action.intent)
        if amount is None:
            amount = float(action.payload.get("intent_amount", 0) or 0)
        targets = parse_named_targets(action.intent)
        if action.payload.get("intent_to"):
            targets = frozenset({str(action.payload["intent_to"]).lower()}) | targets
        return EffectVector(
            cardinality=1.0,
            targets=targets or frozenset({"unspecified"}),
            irreversible=True,
            resource_type="bank_transfer",
            sensitivity=0.95,
            amount=float(amount),
            environment=str(action.payload.get("environment", "prod")),
        )

    def proposed_effect(self, action: Action) -> EffectVector:
        amount = float(action.payload.get("amount", 0) or 0)
        to_account = str(action.payload.get("to", action.payload.get("to_account", "unknown")))
        return EffectVector(
            cardinality=1.0,
            targets=frozenset({to_account.lower()}),
            irreversible=True,
            resource_type="bank_transfer",
            sensitivity=0.95 if amount >= 1000 else 0.8,
            amount=amount,
            environment=str(action.payload.get("environment", "prod")),
            notes=("transfer not executed — effect forecast only",),
        )
