import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import settings
from .api.router import api_router, ws_api_router
from .auth.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from .nlp.extractor import ClaimExtractionError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    # Startup
    logger.info("FactAnchor API starting up...")
    logger.info(f"Environment: {settings.APP_ENV}")
    
    # Warm up spaCy model
    try:
        from .nlp.pipeline import get_pipeline
        get_pipeline()
        logger.info("spaCy pipeline loaded successfully")
    except Exception as e:
        logger.warning(f"spaCy pipeline not available at startup: {e}")

    # Initial Admin Creation
    if settings.INITIAL_ADMIN_EMAIL and settings.INITIAL_ADMIN_PASSWORD:
        from .db.session import AsyncSessionLocal
        from .db.models import User
        from .auth.jwt import hash_password
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.email == settings.INITIAL_ADMIN_EMAIL)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                logger.info(f"Creating initial admin user: {settings.INITIAL_ADMIN_EMAIL}")
                admin_user = User(
                    email=settings.INITIAL_ADMIN_EMAIL,
                    hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                    is_active=True,
                    is_superuser=True
                )
                session.add(admin_user)
                await session.commit()
                logger.info("Initial admin user created successfully")
            else:
                logger.info(f"Initial admin user ({settings.INITIAL_ADMIN_EMAIL}) already exists")

    logger.info("FactAnchor API ready")
    yield
    # Shutdown
    logger.info("FactAnchor API shutting down...")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="FactAnchor API",
        version="1.0.0",
        description="Reverse-RAG Factual Verification Pipeline",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        lifespan=lifespan,
    )

    # Middleware (outermost first)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"], # Allow all hosts for deployment stability on Render
    )
    # CORS configuration
    # Note: Using regex to dynamically allow and reflect origins. 
    # This is standard practice when allow_credentials=True is required across multiple environments.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex="https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    # Routers
    app.include_router(api_router)
    app.include_router(ws_api_router)

    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error_code": "VALIDATION_ERROR", "detail": exc.errors()},
        )

    @app.exception_handler(ClaimExtractionError)
    async def extraction_error_handler(request: Request, exc: ClaimExtractionError):
        return JSONResponse(
            status_code=500,
            content={"error_code": "EXTRACTION_FAILED", "detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"error_code": "INTERNAL_ERROR", "detail": "An internal error occurred"},
        )

    return app


app = create_app()
