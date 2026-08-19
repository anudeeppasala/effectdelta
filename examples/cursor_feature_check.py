#!/usr/bin/env python3
"""Manual Cursor/feature workflow: call EffectDelta before accepting a big diff."""

from effectdelta import Gate, Rule, check_action


def main() -> None:
    gate = Gate(
        rules=[
            Rule(name="scope_delta", max_scope_files_delta=5, on_breach="block"),
            Rule(name="max_files", max_scope_files=8, on_breach="approve"),
        ]
    )

    requirements = "Add dark mode toggle on Settings page only"

    # What the AI proposed in your editor session
    proposed = {
        "files_changed": [
            "src/pages/Settings.tsx",
            "src/settings/theme.py",
            "src/components/Toggle.tsx",
        ],
        "diff_summary": "add dark mode toggle to settings page",
    }

    decision = check_action(
        intent=requirements,
        kind="code_change",
        payload=proposed,
        gate=gate,
    )
    print("Small change:", decision.verdict.value, "-", decision.reason)

    oversized = {
        "files_changed": [f"src/design-system/{i}.tsx" for i in range(40)],
        "diff_summary": "refactor entire design system",
    }
    decision = check_action(
        intent=requirements,
        kind="code_change",
        payload=oversized,
        gate=gate,
    )
    print("Huge change:", decision.verdict.value, "-", decision.reason)


if __name__ == "__main__":
    main()
