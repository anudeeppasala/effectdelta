from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from effectdelta.gate import Gate
from effectdelta.models import Action, Decision, Verdict

F = TypeVar("F", bound=Callable[..., Any])


class ActionBlocked(RuntimeError):
    def __init__(self, decision: Decision) -> None:
        self.decision = decision
        super().__init__(f"Action blocked: {decision.reason}")


def check_action(
    intent: str,
    kind: str,
    payload: dict[str, Any] | None = None,
    *,
    gate: Gate | None = None,
    metadata: dict[str, Any] | None = None,
) -> Decision:
    """Manual entry point for Cursor/feature workflows and custom agents."""
    active_gate = gate or Gate()
    return active_gate.check(
        Action(
            intent=intent,
            kind=kind,
            payload=payload or {},
            metadata=metadata or {},
        )
    )


def wrap_action(
    kind: str,
    *,
    intent: str | Callable[..., str],
    payload_from_args: Callable[..., dict[str, Any]] | None = None,
    gate: Gate | None = None,
    block_on_approve: bool = False,
) -> Callable[[F], F]:
    """Decorator: forecast effect + enforce policy before the function body runs."""

    active_gate = gate or Gate()

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            resolved_intent = intent(*args, **kwargs) if callable(intent) else intent
            payload = (
                payload_from_args(*args, **kwargs)
                if payload_from_args
                else dict(kwargs)
            )
            decision = active_gate.check(
                Action(intent=resolved_intent, kind=kind, payload=payload)
            )
            if decision.verdict is Verdict.BLOCK:
                raise ActionBlocked(decision)
            if block_on_approve and decision.verdict is Verdict.APPROVE:
                raise ActionBlocked(decision)
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
