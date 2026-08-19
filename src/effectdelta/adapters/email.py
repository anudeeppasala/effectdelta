from __future__ import annotations

from typing import Callable

from effectdelta.adapters.base import ActionAdapter
from effectdelta.intent import estimate_intent_cardinality, parse_named_targets
from effectdelta.models import Action, EffectVector

RecipientResolver = Callable[[str], list[str]]


def default_recipient_resolver(address: str) -> list[str]:
    """Offline mock resolver for demos and tests."""
    key = address.strip().lower()
    directory = {
        "john@company.com": ["john@company.com"],
        "john": ["john@company.com"],
        "alice@company.com": ["alice@company.com"],
        "alice": ["alice@company.com"],
        "all@company.com": [f"user{i}@company.com" for i in range(1, 5001)],
        "everyone": [f"user{i}@company.com" for i in range(1, 5001)],
        "team@company.com": [f"team{i}@company.com" for i in range(1, 26)],
    }
    if key in directory:
        return directory[key]
    if "@" in key:
        return [key]
    return [key]


class EmailAdapter(ActionAdapter):
    kind = "send_email"

    def __init__(self, resolver: RecipientResolver | None = None) -> None:
        self.resolver = resolver or default_recipient_resolver

    def intent_effect(self, action: Action) -> EffectVector:
        targets = parse_named_targets(action.intent)
        cardinality = estimate_intent_cardinality(action.intent, default=float(len(targets) or 1))
        if targets:
            cardinality = float(len(targets))
        return EffectVector(
            cardinality=cardinality,
            targets=targets or frozenset({"unspecified"}),
            irreversible=True,
            resource_type="email",
            sensitivity=0.6,
            environment=str(action.payload.get("environment", "prod")),
            notes=("intent parsed from natural language",),
        )

    def proposed_effect(self, action: Action) -> EffectVector:
        raw_to = action.payload.get("to", action.payload.get("recipients", []))
        if isinstance(raw_to, str):
            addresses = [raw_to]
        else:
            addresses = list(raw_to)

        resolved: list[str] = []
        for addr in addresses:
            resolved.extend(self.resolver(str(addr)))

        # de-dupe preserve order
        unique: list[str] = []
        seen: set[str] = set()
        for item in resolved:
            low = item.lower()
            if low not in seen:
                seen.add(low)
                unique.append(low)

        return EffectVector(
            cardinality=float(len(unique)),
            targets=frozenset(unique),
            irreversible=True,
            resource_type="email",
            sensitivity=0.6 if len(unique) < 100 else 0.9,
            environment=str(action.payload.get("environment", "prod")),
            notes=(f"resolved {len(addresses)} address(es) → {len(unique)} recipients",),
        )
