from effectdelta.adapters.base import AdapterRegistry
from effectdelta.models import EffectVector
from effectdelta.scoring import DeltaScorer


def test_cardinality_ratio_and_destination_mismatch():
    scorer = DeltaScorer()
    intent = EffectVector(cardinality=1, targets=frozenset({"john"}))
    proposed = EffectVector(
        cardinality=5000,
        targets=frozenset({f"user{i}@company.com" for i in range(5)}),
    )
    deltas = scorer.score(intent, proposed)
    assert deltas.cardinality_delta == 4999
    assert deltas.cardinality_ratio == 5000
    assert deltas.destination_mismatch is True


def test_amount_ratio():
    scorer = DeltaScorer()
    intent = EffectVector(amount=50, targets=frozenset({"alice"}))
    proposed = EffectVector(amount=5000, targets=frozenset({"alice"}))
    deltas = scorer.score(intent, proposed)
    assert deltas.amount_ratio == 100
    assert deltas.destination_mismatch is False


def test_registry_unknown_kind():
    registry = AdapterRegistry()
    try:
        registry.get("nope")
        assert False, "expected KeyError"
    except KeyError as exc:
        assert "nope" in str(exc)
