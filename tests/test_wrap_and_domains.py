from effectdelta import Action, ActionBlocked, Gate, Rule, wrap_action
from effectdelta.models import Verdict


def test_sql_unscoped_delete_blocked():
    gate = Gate(rules=[Rule(name="rows", max_cardinality_ratio=10, on_breach="block")])
    decision = gate.check(
        Action(
            intent="Delete the user with id 42",
            kind="sql",
            payload={"sql": "DELETE FROM users"},
        )
    )
    assert decision.verdict == Verdict.BLOCK


def test_media_draft_vs_live_blocked():
    gate = Gate(
        rules=[
            Rule(name="audience", max_cardinality_ratio=5, on_breach="block"),
            Rule(name="channel", forbid_channel_mismatch=True, on_breach="block"),
        ]
    )
    decision = gate.check(
        Action(
            intent="Publish this draft to editors",
            kind="media_publish",
            payload={"channels": ["live"], "subscriber_count": 50000, "editor_count": 10},
        )
    )
    assert decision.verdict == Verdict.BLOCK


def test_wrap_action_blocks_before_side_effect():
    gate = Gate(rules=[Rule(name="card", max_cardinality_ratio=2, on_breach="block")])
    calls = {"sent": 0}

    @wrap_action(
        "send_email",
        intent="Send this report to John",
        payload_from_args=lambda to, **_: {"to": to},
        gate=gate,
    )
    def send_email(to: str) -> str:
        calls["sent"] += 1
        return "sent"

    try:
        send_email("all@company.com")
        assert False, "expected ActionBlocked"
    except ActionBlocked as exc:
        assert exc.decision.verdict == Verdict.BLOCK
        assert calls["sent"] == 0
