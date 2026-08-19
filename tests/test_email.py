from effectdelta import Action, Gate, Rule, Verdict


def test_email_john_vs_everyone_is_blocked():
    gate = Gate(
        rules=[
            Rule(name="card", max_cardinality_ratio=2.0, on_breach="block"),
            Rule(name="dest", forbid_destination_mismatch=True, on_breach="approve"),
        ]
    )
    decision = gate.check(
        Action(
            intent="Send this report to John",
            kind="send_email",
            payload={"to": "all@company.com", "subject": "Report"},
        )
    )
    assert decision.verdict == Verdict.BLOCK
    assert decision.deltas.cardinality_ratio == 5000
    assert decision.proposed_effect.cardinality == 5000


def test_email_john_to_john_is_allowed():
    gate = Gate(
        rules=[
            Rule(name="card", max_cardinality_ratio=2.0, on_breach="block"),
        ]
    )
    decision = gate.check(
        Action(
            intent="Send this report to John",
            kind="send_email",
            payload={"to": "john@company.com"},
        )
    )
    assert decision.verdict == Verdict.ALLOW
    assert decision.proposed_effect.cardinality == 1
