from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(
        title="Todo API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )


app = create_app()
