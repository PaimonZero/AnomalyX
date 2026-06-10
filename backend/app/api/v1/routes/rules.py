import logging

from fastapi import APIRouter, HTTPException

from app.rules.engine import RuleEngineError, rule_engine_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rules")


@router.get("")
def list_rules() -> dict:
    return rule_engine_manager.engine.to_dict()


@router.post("/reload")
def reload_rules() -> dict:
    try:
        engine = rule_engine_manager.reload()
    except RuleEngineError as exc:
        logger.error("Failed to reload rules", exc_info=True)
        raise HTTPException(status_code=400, detail="Rule processing error") from exc

    return {
        "status": "reloaded",
        "active_rules": len(engine.rules),
        "version": engine.version,
    }
