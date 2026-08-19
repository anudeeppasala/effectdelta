from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from effectdelta.models import Action, EffectVector


class ActionAdapter(ABC):
    """Domain plugin: turn an Action into intent + proposed effect vectors."""

    kind: str

    @abstractmethod
    def intent_effect(self, action: Action) -> EffectVector:
        raise NotImplementedError

    @abstractmethod
    def proposed_effect(self, action: Action) -> EffectVector:
        raise NotImplementedError


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, ActionAdapter] = {}

    def register(self, adapter: ActionAdapter) -> None:
        self._adapters[adapter.kind] = adapter

    def get(self, kind: str) -> ActionAdapter:
        try:
            return self._adapters[kind]
        except KeyError as exc:
            known = ", ".join(sorted(self._adapters)) or "(none)"
            raise KeyError(
                f"No adapter registered for action kind {kind!r}. Known: {known}"
            ) from exc

    def has(self, kind: str) -> bool:
        return kind in self._adapters


Resolver = Callable[[dict], EffectVector]
