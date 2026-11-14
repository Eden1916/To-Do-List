import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from todo_chat.config import Settings
from todo_chat.database import build_engine

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> CORSMiddleware:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(api):
        engine = build_engine(settings.database_url)
        api.state.engine = engine
        try:
            yield
        finally:
            engine.dispose()

    api = FastAPI(title="To-Do List Bot API", lifespan=lifespan)

    @api.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(
            {"message": message}, status_code=exc.status_code, headers=exc.headers
        )

    @api.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse({"message": "Invalid input"}, status_code=400)

    @api.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logger.error(
            "Unhandled API error", exc_info=(type(exc), exc, exc.__traceback__)
        )
        return JSONResponse({"message": "Internal server error"}, status_code=500)

    @api.get("/health")
    def health():
        return {"status": "ok"}

    # Wrap the entire app so unexpected errors carry CORS headers too.
    return CORSMiddleware(
        api,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )


app = create_app()
