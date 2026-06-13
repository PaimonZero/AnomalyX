from __future__ import annotations

import re
from collections.abc import Iterable

from app.schemas.prediction import TransactionRequest


def mask_value(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:3]}***{value[-3:]}"


class SecureDataWrapper:
    pii_patterns = (
        re.compile(r"\b(?:acct|account|user|phone|address|passport)[_:-]?[a-z0-9]+\b", re.IGNORECASE),
        re.compile(r"\b\+?\d{9,15}\b"),
    )

    def sanitize_transaction_context(self, transaction: TransactionRequest) -> dict[str, object]:
        return {
            "transaction_id": mask_value(transaction.transaction_id),
            "sender_id": mask_value(transaction.sender_id),
            "receiver_id": mask_value(transaction.receiver_id),
            "amount": transaction.amount,
            "currency": transaction.currency,
            "channel": transaction.channel.value,
            "timestamp_hour": transaction.timestamp.hour,
        }

    def contains_unmasked_identifier(self, text: str, transaction: TransactionRequest) -> bool:
        identifiers = (
            transaction.transaction_id,
            transaction.sender_id,
            transaction.receiver_id,
        )
        return any(identifier and identifier in text for identifier in identifiers)

    def contains_pii_like_token(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self.pii_patterns)

    def is_masked_context_value(self, value: object, safe_context: dict[str, object]) -> bool:
        return value in safe_context.values()

    def all_supported(self, values: Iterable[str], allowed_values: set[str]) -> bool:
        return set(values).issubset(allowed_values)


secure_data_wrapper = SecureDataWrapper()
