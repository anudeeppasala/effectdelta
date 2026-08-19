from __future__ import annotations

from effectdelta.adapters import default_registry
from effectdelta.adapters.base import AdapterRegistry
from effectdelta.models import Action, Decision, Verdict
from effectdelta.rules import Rule, worst_verdict
from effectdelta.scoring import DeltaScorer


class Gate:
    """Evaluate an Action: intent effect vs proposed effect → allow/approve/block."""

    def __init__(
        self,
        rules: list[Rule] | None = None,
        registry: AdapterRegistry | None = None,
        scorer: DeltaScorer | None = None,
    ) -> None:
        self.rules = rules or [
            Rule(
                name="cardinality",
                max_cardinality_ratio=2.0,
                on_breach="block",
            ),
            Rule(
                name="destination",
                forbid_destination_mismatch=True,
                on_breach="approve",
            ),
        ]
        self.registry = registry or default_registry()
        self.scorer = scorer or DeltaScorer()

    def check(self, action: Action) -> Decision:
        adapter = self.registry.get(action.kind)
        intent_effect = adapter.intent_effect(action)
        proposed_effect = adapter.proposed_effect(action)
        deltas = self.scorer.score(intent_effect, proposed_effect)

        verdict = Verdict.ALLOW
        reasons: list[str] = []
        breached: list[str] = []

        for rule in self.rules:
            message = rule.check(deltas, proposed_scope_files=proposed_effect.scope_files)
            if message:
                breached.append(message)
                reasons.append(message)
                verdict = worst_verdict(verdict, rule.verdict())

        if not reasons:
            reasons.append("proposed effect matches intent within configured rules")

        return Decision(
            verdict=verdict,
            reason="; ".join(reasons),
            intent_effect=intent_effect,
            proposed_effect=proposed_effect,
            deltas=deltas,
            breached_rules=tuple(breached),
        )
