from __future__ import annotations

from dataclasses import dataclass
from json import JSONDecodeError
import logging
from typing import Protocol

from openai import OpenAI, OpenAIError

from app.core.config import get_settings
from app.schemas.alert import Alert
from app.schemas.prediction import TransactionRequest

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExplanationResult:
    text: str
    source: str


class AlertExplainer(Protocol):
    def explain(self, alert: Alert, transaction: TransactionRequest) -> ExplanationResult:
        """Generate a human-readable explanation for an alert."""


class OpenAIAlertExplainer:
    def explain(self, alert: Alert, transaction: TransactionRequest) -> ExplanationResult:
        settings = get_settings()
        if not settings.openai_api_key:
            return template_explanation(alert)

        try:
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AML analyst assistant. Explain why a transaction "
                            "was flagged using ONLY the provided rules, features, and risk "
                            "decision. Do not invent facts, identifiers, account names, phone "
                            "numbers, addresses, or unsupported amounts. Be concise and write "
                            "for a non-technical compliance officer."
                        ),
                    },
                    {
                        "role": "user",
                        "content": build_prompt(alert, transaction, settings.openai_explanation_language),
                    },
                ],
                temperature=0.2,
                max_tokens=260,
            )
            content = response.choices[0].message.content
            if not content:
                return template_explanation(alert)

            explanation = content.strip()
            if not is_grounded(explanation, alert):
                return template_explanation(alert)

            return ExplanationResult(text=explanation, source="openai")
        except (OpenAIError, TimeoutError, ConnectionError, JSONDecodeError):
            logger.exception(
                "Handled OpenAI alert explanation failure",
                extra=log_context(alert, transaction),
            )
            return template_explanation(alert)
        except Exception:
            logger.exception(
                "Unexpected OpenAI alert explanation failure",
                extra=log_context(alert, transaction),
            )
            raise


def build_prompt(alert: Alert, transaction: TransactionRequest, language: str) -> str:
    rules = [
        {
            "id": rule.id,
            "severity": rule.severity.value,
            "typology": rule.typology,
        }
        for rule in alert.triggered_rules
    ]
    top_features = [
        {
            "name": feature.name,
            "value": feature.value,
            "contribution": feature.contribution,
        }
        for feature in alert.top_features
    ]

    safe_context = {
        "transaction_id": mask_value(transaction.transaction_id),
        "sender_id": mask_value(transaction.sender_id),
        "receiver_id": mask_value(transaction.receiver_id),
        "amount": transaction.amount,
        "currency": transaction.currency,
        "channel": transaction.channel.value,
        "timestamp_hour": transaction.timestamp.hour,
    }

    return (
        f"Language requirement: {language}.\n"
        f"risk_level={alert.risk_level.value}; "
        f"is_flagged=true; risk_score={alert.risk_score};\n"
        f"triggered_rules={rules};\n"
        f"top_features={top_features};\n"
        f"non_pii_transaction_context={safe_context}.\n"
        "Explain the alert in 2-4 sentences."
    )


def template_explanation(alert: Alert) -> ExplanationResult:
    rule_ids = ", ".join(rule.id for rule in alert.triggered_rules) or "no rule"
    feature_names = ", ".join(feature.name for feature in alert.top_features[:3]) or "no features"
    text = (
        f"This transaction was flagged as {alert.risk_level.value} with risk score "
        f"{alert.risk_score:.4f}. Triggered rules: {rule_ids}. Main contributing "
        f"features: {feature_names}."
    )
    return ExplanationResult(text=text, source="template")


def log_context(alert: Alert, transaction: TransactionRequest) -> dict[str, object]:
    return {
        "transaction_id": transaction.transaction_id,
        "risk_level": alert.risk_level.value,
        "risk_score": alert.risk_score,
    }


def mask_value(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:3]}***{value[-3:]}"


def is_grounded(explanation: str, alert: Alert) -> bool:
    if not explanation.strip():
        return False

    allowed_rule_ids = {rule.id for rule in alert.triggered_rules}
    allowed_feature_names = {feature.name for feature in alert.top_features}
    suspicious_prefixes = {"user_", "acct_", "phone", "address", "passport"}
    lowered = explanation.lower()
    if any(prefix in lowered for prefix in suspicious_prefixes):
        return False

    referenced_rules = {
        token.strip(".,;:()[]{}")
        for token in explanation.replace("\n", " ").split()
        if token.startswith("R-")
    }
    if not referenced_rules.issubset(allowed_rule_ids):
        return False

    referenced_mock_features = {
        token.strip(".,;:()[]{}")
        for token in explanation.replace("\n", " ").split()
        if token.startswith("mock_")
    }
    return referenced_mock_features.issubset(allowed_feature_names)
