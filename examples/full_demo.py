#!/usr/bin/env python3
"""Run the three killer demos: email, banking, and code-change."""

from __future__ import annotations

from effectdelta import Action, Gate, Rule, check_action


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def show(decision) -> None:
    print(f"Verdict : {decision.verdict.value.upper()}")
    print(f"Reason  : {decision.reason}")
    print(
        f"Intent  : cardinality={decision.intent_effect.cardinality}, "
        f"targets={sorted(decision.intent_effect.targets)[:5]}, "
        f"amount={decision.intent_effect.amount}, "
        f"scope_files={decision.intent_effect.scope_files}"
    )
    print(
        f"Proposed: cardinality={decision.proposed_effect.cardinality}, "
        f"targets={sorted(decision.proposed_effect.targets)[:5]}, "
        f"amount={decision.proposed_effect.amount}, "
        f"scope_files={decision.proposed_effect.scope_files}"
    )
    d = decision.deltas
    print(
        f"Deltas  : card_ratio={d.cardinality_ratio}, "
        f"amount_ratio={d.amount_ratio}, "
        f"scope_delta={d.scope_files_delta}, "
        f"dest_mismatch={d.destination_mismatch}"
    )


def main() -> None:
    banner("1) Email — 'to John' vs all@company.com (5000)")
    email_gate = Gate(
        rules=[
            Rule(name="cardinality", max_cardinality_ratio=2.0, on_breach="block"),
            Rule(name="destination", forbid_destination_mismatch=True, on_breach="approve"),
        ]
    )
    show(
        email_gate.check(
            Action(
                intent="Send this report to John",
                kind="send_email",
                payload={"to": "all@company.com", "subject": "Q2 Report"},
            )
        )
    )

    banner("2) Banking — Transfer $50 to Alice vs $5000")
    bank_gate = Gate(
        rules=[
            Rule(name="amount", max_amount_ratio=2.0, on_breach="block"),
            Rule(name="destination", forbid_destination_mismatch=True, on_breach="block"),
        ]
    )
    show(
        bank_gate.check(
            Action(
                intent="Transfer $50 to Alice",
                kind="bank_transfer",
                payload={"to": "alice", "amount": 5000},
            )
        )
    )

    banner("3) Code change — Settings-only vs 40-file redesign")
    code_gate = Gate(
        rules=[
            Rule(name="scope_delta", max_scope_files_delta=5, on_breach="block"),
            Rule(name="max_files", max_scope_files=10, on_breach="approve"),
        ]
    )
    show(
        check_action(
            intent="Add dark mode toggle on Settings page only",
            kind="code_change",
            payload={
                "files_changed": [f"src/design-system/{i}.tsx" for i in range(40)],
                "diff_summary": "refactor entire design system and redesign all pages",
            },
            gate=code_gate,
        )
    )

    banner("Done — EffectDelta compared wanted vs proposed effects")


if __name__ == "__main__":
    main()
