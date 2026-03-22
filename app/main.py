"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    _logger.info(
        "Starting %s v%s (env=%s, gemini_model=%s)",
        settings.app_name,
        settings.app_version,
        settings.environment,
        settings.gemini_model,
    )
    yield
    _logger.info("Shutting down %s.", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="MVP de estudo para motor de retencao com IA e foco em churn.",
    summary="API do MVP agentic-client-guardian para clientes, analise e prioridades.",
    lifespan=lifespan,
)

# Allow the standalone frontend (file:// or localhost dev server) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment != "production" else [],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve the HTML frontend at /ui (e.g. http://localhost:8000/ui/)
try:
    app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")
except RuntimeError:
    _logger.warning("frontend/ directory not found — /ui will not be served.")
