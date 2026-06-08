from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Backend API for the AnomalyX AML prototype.",
    )
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router)

    return app


app = create_app()
