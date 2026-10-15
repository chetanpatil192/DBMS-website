"""FastAPI Application Entrypoint and Lifespan Configuration."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.v1.router import api_v1_router
from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.db.client import db_manager

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and orderly shutdown lifecycle events."""
    settings = get_settings()
    logger.info("Starting %s v%s in '%s' mode", settings.PROJECT_NAME, __version__, settings.ENVIRONMENT)

    # Initialize PyMongo connection pool
    try:
        db_manager.connect(settings)
        # Attempt non-blocking initial ping check
        ping_result = db_manager.ping()
        if ping_result.get("connected"):
            logger.info("Successfully connected to MongoDB at %s (latency: %.2f ms)", settings.MONGODB_URI, ping_result["latency_ms"])
        else:
            logger.warning("MongoDB ping failed on startup: %s. Application will run in degraded mode.", ping_result.get("error"))
    except Exception as exc:
        logger.error("Failed to establish database connection during startup: %s", exc)

    yield

    # Orderly shutdown: drain and close PyMongo sockets
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    db_manager.close()
    logger.info("Application shutdown complete.")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory for Commerce Insights FastAPI backend."""
    current_settings = settings or get_settings()

    app = FastAPI(
        title=current_settings.PROJECT_NAME,
        version=__version__,
        description=(
            "Analytical API and benchmark engine for Commerce Insights, "
            "designed to evaluate MongoDB read performance, aggregation pipelines, "
            "and indexing architectures."
        ),
        docs_url=f"{current_settings.API_V1_STR}/docs",
        redoc_url=f"{current_settings.API_V1_STR}/redoc",
        openapi_url=f"{current_settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Register CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=current_settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Centralized exception handlers for standard ErrorEnvelope
    register_exception_handlers(app)

    # Mount API Routers
    app.include_router(api_v1_router, prefix=current_settings.API_V1_STR)

    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"

    # Static assets mounting
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get(
        "/",
        summary="Root Status & Web App Entrypoint",
        description="Serves the React dashboard to browsers, or service metadata to API clients.",
    )
    async def root(request: Request) -> Response:
        accept_header = request.headers.get("accept", "")
        # If browser requests HTML, serve the production single-page application
        if "text/html" in accept_header and (frontend_dist / "index.html").exists():
            return FileResponse(frontend_dist / "index.html")

        # Otherwise return API discovery JSON
        return JSONResponse(
            content={
                "service": current_settings.PROJECT_NAME,
                "version": __version__,
                "docs_url": f"{current_settings.API_V1_STR}/docs",
                "health_url": f"{current_settings.API_V1_STR}/health",
                "status": "operational",
            }
        )

    # SPA catch-all for client-side routing
    if frontend_dist.exists():
        @app.get("/{catchall:path}", include_in_schema=False)
        async def serve_spa_catchall(catchall: str) -> Response:
            if (
                catchall.startswith("api/")
                or catchall.startswith("docs")
                or catchall.startswith("redoc")
                or catchall.startswith("openapi.json")
            ):
                raise HTTPException(status_code=404, detail="Not Found")
            file_candidate = frontend_dist / catchall
            if file_candidate.is_file():
                return FileResponse(file_candidate)
            return FileResponse(frontend_dist / "index.html")

    return app


# Default ASGI application instance for Uvicorn
app = create_app()

if __name__ == "__main__":
    import uvicorn

    config = get_settings()
    uvicorn.run(
        "app.main:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
    )
