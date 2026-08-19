from __future__ import annotations

from effectdelta.adapters.bank import BankTransferAdapter
from effectdelta.adapters.base import ActionAdapter, AdapterRegistry
from effectdelta.adapters.code_change import CodeChangeAdapter
from effectdelta.adapters.email import EmailAdapter
from effectdelta.adapters.file import FileAdapter
from effectdelta.adapters.media import MediaPublishAdapter
from effectdelta.adapters.sql import SqlAdapter


def default_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    for adapter in (
        EmailAdapter(),
        SqlAdapter(),
        FileAdapter(),
        CodeChangeAdapter(),
        BankTransferAdapter(),
        MediaPublishAdapter(),
    ):
        registry.register(adapter)
    return registry


__all__ = [
    "ActionAdapter",
    "AdapterRegistry",
    "BankTransferAdapter",
    "CodeChangeAdapter",
    "EmailAdapter",
    "FileAdapter",
    "MediaPublishAdapter",
    "SqlAdapter",
    "default_registry",
]
