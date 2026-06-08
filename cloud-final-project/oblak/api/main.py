from fastapi import FastAPI

from oblak.api.routes import router
from oblak.db.init_db import init_db


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title="Oblak API",
        version="0.1.0",
        description="Academic serverless platform for verified Python function execution.",
    )
    app.include_router(router)
    return app


app = create_app()
