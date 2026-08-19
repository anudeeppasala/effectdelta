from effectdelta import Action, Gate, Rule, check_action
from effectdelta.models import Verdict


def test_code_change_settings_vs_redesign_blocked():
    gate = Gate(
        rules=[
            Rule(name="scope", max_scope_files_delta=5, on_breach="block"),
            Rule(name="files", max_scope_files=10, on_breach="approve"),
        ]
    )
    decision = gate.check(
        Action(
            intent="Add dark mode toggle on Settings page only",
            kind="code_change",
            payload={
                "files_changed": [
                    f"src/design-system/{i}.tsx" for i in range(40)
                ],
                "diff_summary": "refactor entire design system and redesign all pages",
            },
        )
    )
    assert decision.verdict == Verdict.BLOCK
    assert decision.proposed_effect.scope_files >= 40


def test_code_change_small_settings_allowed():
    gate = Gate(
        rules=[
            Rule(name="scope", max_scope_files_delta=5, on_breach="block"),
            Rule(name="files", max_scope_files=10, on_breach="approve"),
        ]
    )
    decision = check_action(
        intent="Add dark mode toggle on Settings page only",
        kind="code_change",
        payload={
            "files_changed": [
                "src/pages/Settings.tsx",
                "src/settings/theme.py",
                "src/components/Toggle.tsx",
            ],
            "diff_summary": "add dark mode toggle to settings",
        },
        gate=gate,
    )
    assert decision.verdict == Verdict.ALLOW
