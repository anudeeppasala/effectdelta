from effectdelta import Action, Gate, Rule
from effectdelta.models import Verdict


def test_bank_amount_mismatch_blocked():
    gate = Gate(
        rules=[
            Rule(name="amount", max_amount_ratio=2.0, on_breach="block"),
            Rule(name="dest", forbid_destination_mismatch=True, on_breach="block"),
        ]
    )
    decision = gate.check(
        Action(
            intent="Transfer $50 to Alice",
            kind="bank_transfer",
            payload={"to": "alice", "amount": 5000},
        )
    )
    assert decision.verdict == Verdict.BLOCK
    assert decision.deltas.amount_ratio == 100


def test_bank_matching_transfer_allowed():
    gate = Gate(
        rules=[
            Rule(name="amount", max_amount_ratio=2.0, on_breach="block"),
            Rule(name="dest", forbid_destination_mismatch=True, on_breach="block"),
        ]
    )
    decision = gate.check(
        Action(
            intent="Transfer $50 to Alice",
            kind="bank_transfer",
            payload={"to": "alice", "amount": 50},
        )
    )
    assert decision.verdict == Verdict.ALLOW
