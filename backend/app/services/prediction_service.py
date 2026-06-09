from __future__ import annotations

import time

from fastapi import BackgroundTasks

from app.core.decision import DecisionEngine
from app.core.metrics import LLM_EXPLANATION_COUNT, LLM_LATENCY, record_prediction
from app.llm.explainer import AlertExplainer, OpenAIAlertExplainer
from app.ml.factory import get_model_predictor
from app.rules.engine import rule_engine_manager
from app.schemas.prediction import PredictionResponse, TransactionRequest
from app.services.alert_service import AlertService
from app.services.idempotency_service import IdempotencyClaim, IdempotencyService

IDEMPOTENCY_PROCESSING_WAIT_SECONDS = 10.0
IDEMPOTENCY_PROCESSING_POLL_SECONDS = 0.05


class PredictionService:
    def __init__(
        self,
        decision_engine: DecisionEngine | None = None,
        alert_service: AlertService | None = None,
        explainer: AlertExplainer | None = None,
        idempotency_service: IdempotencyService | None = None,
    ) -> None:
        self.decision_engine = decision_engine or DecisionEngine.from_settings()
        self.alert_service = alert_service or AlertService()
        self.explainer = explainer or OpenAIAlertExplainer()
        self.idempotency_service = idempotency_service or IdempotencyService()

    def predict(
        self,
        transaction: TransactionRequest,
        background_tasks: BackgroundTasks | None = None,
        idempotency_key: str | None = None,
    ) -> PredictionResponse:
        effective_idempotency_key = idempotency_key or transaction.transaction_id
        idempotency_claim = self._claim_or_wait_for_response(effective_idempotency_key)
        if idempotency_claim.response is not None:
            return idempotency_claim.response
        if not idempotency_claim.is_claimed:
            raise RuntimeError("Prediction is already processing for this idempotency key.")

        try:
            triggered_rules = rule_engine_manager.engine.evaluate(transaction)
            model_prediction = get_model_predictor().predict(transaction)
            decision = self.decision_engine.decide(
                risk_score=model_prediction.risk_score,
                triggered_rules=triggered_rules,
            )

            alert_id = None
            if decision.is_flagged:
                alert = self.alert_service.create_alert(
                    transaction_id=transaction.transaction_id,
                    risk_score=model_prediction.risk_score,
                    risk_level=decision.risk_level,
                    triggered_rules=triggered_rules,
                    top_features=model_prediction.top_features,
                )
                alert_id = alert.id
                if background_tasks is not None:
                    background_tasks.add_task(self.explain_alert, alert_id, transaction)

            response = PredictionResponse(
                transaction_id=transaction.transaction_id,
                risk_score=model_prediction.risk_score,
                risk_level=decision.risk_level,
                is_flagged=decision.is_flagged,
                model_version=model_prediction.model_version,
                triggered_rules=triggered_rules,
                top_features=model_prediction.top_features,
                explanation=None,
                explanation_source=None,
                alert_id=alert_id,
            )
            self.idempotency_service.store_response(effective_idempotency_key, response)
        except Exception:
            self.idempotency_service.release_response_claim(effective_idempotency_key)
            raise

        record_prediction(
            risk_level=response.risk_level.value,
            is_flagged=response.is_flagged,
            triggered_rules=response.triggered_rules,
        )
        return response

    def _claim_or_wait_for_response(self, idempotency_key: str) -> IdempotencyClaim:
        deadline = time.monotonic() + IDEMPOTENCY_PROCESSING_WAIT_SECONDS
        while True:
            claim = self.idempotency_service.claim_response(idempotency_key)
            if claim.is_claimed or claim.response is not None:
                return claim
            if time.monotonic() >= deadline:
                return claim
            time.sleep(IDEMPOTENCY_PROCESSING_POLL_SECONDS)

    def explain_alert(self, alert_id: str, transaction: TransactionRequest) -> None:
        start_time = time.perf_counter()
        alert = self.alert_service.get_alert(alert_id)
        explanation = self.explainer.explain(alert, transaction)
        self.alert_service.update_explanation(
            alert_id=alert_id,
            explanation=explanation.text,
            explanation_source=explanation.source,
        )
        latency_seconds = time.perf_counter() - start_time
        LLM_EXPLANATION_COUNT.labels(source=explanation.source).inc()
        LLM_LATENCY.labels(source=explanation.source).observe(latency_seconds)
