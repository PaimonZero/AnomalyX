from fastapi import APIRouter, HTTPException

from app.rules.engine import RuleEngineError, rule_engine_manager


router = APIRouter(prefix="/rules")


@router.get("")
def list_rules() -> dict:
    return rule_engine_manager.engine.to_dict()


@router.post("/reload")
def reload_rules() -> dict:
    try:
        engine = rule_engine_manager.reload()
    except RuleEngineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "reloaded",
        "active_rules": len(engine.rules),
        "version": engine.version,
    }
