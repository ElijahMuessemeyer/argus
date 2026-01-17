"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.router import router as api_router
from app.api.middleware import RequestLoggingMiddleware
from app.db.session import init_db
from app.services.cache import cache_service
from app.services.scheduler import setup_scheduler, start_scheduler, shutdown_scheduler
from app.errors.handlers import setup_exception_handlers
from app.utils.logging import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()

    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Connect to Redis
    await cache_service.connect()

    # Initialize universe if needed
    from app.db.session import AsyncSessionLocal
    from app.core.universe import UniverseManager

    async with AsyncSessionLocal() as db:
        universe = await UniverseManager.get_universe(db)
        if not universe:
            count = await UniverseManager.initialize_universe(db)
            logger.info(f"Initialized stock universe with {count} stocks")

    # Setup and start scheduler
    setup_scheduler()
    start_scheduler()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")

    shutdown_scheduler()
    await cache_service.disconnect()

    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Stock screening web application for finding stocks near moving averages",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    setup_exception_handlers(app)

    # API routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
