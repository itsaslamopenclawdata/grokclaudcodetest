from fastapi import FastAPI

from app.api import health
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.request_id import RequestIdMiddleware


def create_app() -> FastAPI:
    s = get_settings()
    configure_logging(s.log_level, s.log_json)
    app = FastAPI(
        title="Todo API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health.router)
    return app


app = create_app()
