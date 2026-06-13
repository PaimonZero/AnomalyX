from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.schemas.prediction import RiskLevel, RuleSeverity, TriggeredRule


@dataclass(frozen=True)
class DecisionResult:
    risk_level: RiskLevel
    is_flagged: bool
    reason: str


class DecisionEngine:
    def __init__(self, medium_threshold: float, flag_threshold: float) -> None:
        if not 0 <= medium_threshold < flag_threshold <= 1:
            raise ValueError(
                "Risk thresholds must satisfy "
                "0 <= medium_threshold < flag_threshold <= 1."
            )
        self.medium_threshold = medium_threshold
        self.flag_threshold = flag_threshold

    @classmethod
    def from_settings(cls) -> "DecisionEngine":
        settings = get_settings()
        return cls(
            medium_threshold=settings.risk_threshold_medium,
            flag_threshold=settings.risk_threshold_flag,
        )

    def decide(
        self,
        risk_score: float,
        triggered_rules: list[TriggeredRule],
    ) -> DecisionResult:
        if not 0 <= risk_score <= 1:
            raise ValueError("risk_score must be between 0 and 1.")

        highest_severity = self._highest_rule_severity(triggered_rules)

        if highest_severity == RuleSeverity.CRITICAL:
            return DecisionResult(
                risk_level=RiskLevel.CRITICAL,
                is_flagged=True,
                reason="critical_rule_override",
            )

        if highest_severity == RuleSeverity.HIGH:
            return DecisionResult(
                risk_level=RiskLevel.HIGH,
                is_flagged=True,
                reason="high_rule_override",
            )

        if risk_score >= self.flag_threshold:
            return DecisionResult(
                risk_level=RiskLevel.HIGH,
                is_flagged=True,
                reason="ml_score_flag_threshold",
            )

        if risk_score >= self.medium_threshold:
            return DecisionResult(
                risk_level=RiskLevel.MEDIUM,
                is_flagged=False,
                reason="ml_score_medium_threshold",
            )

        return DecisionResult(
            risk_level=RiskLevel.LOW,
            is_flagged=False,
            reason="low_risk",
        )

    @staticmethod
    def _highest_rule_severity(
        triggered_rules: list[TriggeredRule],
    ) -> RuleSeverity | None:
        severity_rank = {
            RuleSeverity.MINOR: 1,
            RuleSeverity.MEDIUM: 2,
            RuleSeverity.HIGH: 3,
            RuleSeverity.CRITICAL: 4,
        }

        if not triggered_rules:
            return None

        return max(
            (rule.severity for rule in triggered_rules),
            key=lambda severity: severity_rank[severity],
        )
