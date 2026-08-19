"""EffectDelta — gate actions by comparing wanted vs proposed effect vectors."""

from effectdelta.gate import Gate
from effectdelta.models import Action, Decision, EffectVector, Verdict
from effectdelta.rules import Rule
from effectdelta.wrap import ActionBlocked, check_action, wrap_action

__all__ = [
    "Action",
    "ActionBlocked",
    "Decision",
    "EffectVector",
    "Gate",
    "Rule",
    "Verdict",
    "check_action",
    "wrap_action",
]

__version__ = "0.1.0"
