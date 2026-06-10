from __future__ import annotations

from app.schemas.prediction import TransactionRequest


def mask_value(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:3]}***{value[-3:]}"


class SecureDataWrapper:
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


secure_data_wrapper = SecureDataWrapper()
