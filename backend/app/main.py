from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

from app.config import get_settings
from app.api import claims, knowledge, runs, audit, health, fraud, fast_lane, intake, search, export, websocket, decisions

settings = get_settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Humain DecisionOps API",
    description="Insurance Claims Decision Console API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - configurable via CORS_ALLOW_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2)
    )
    
    return response


# API key authentication middleware (optional)
@app.middleware("http")
async def authenticate(request: Request, call_next):
    if settings.auth_enabled:
        # Skip auth for health and docs endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"}
            )
    
    return await call_next(request)


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(claims.router, prefix="/api/claims", tags=["Claims"])
app.include_router(runs.router, prefix="/api/runs", tags=["Runs"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge"])
app.include_router(fraud.router, prefix="/api/fraud", tags=["Fraud"])
app.include_router(fast_lane.router, prefix="/api/fast-lane", tags=["Fast Lane"])
app.include_router(intake.router, prefix="/api/intake", tags=["Intake"])
app.include_router(search.router, tags=["Search"])
app.include_router(export.router, tags=["Export"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(decisions.router, prefix="/decisions", tags=["Decisions"])


@app.on_event("startup")
async def startup_event():
    effective_mode = settings.effective_mode
    logger.info(
        "application_started",
        effective_mode=effective_mode,
        heuristic_mode_forced=settings.heuristic_mode,
        openai_configured=settings.use_openai,
        langsmith_enabled=settings.use_langsmith,
        auth_enabled=settings.auth_enabled,
        cors_origins=settings.cors_origins_list,
        seed_on_startup=settings.seed_on_startup
    )
    
    # Create database tables from ORM models
    try:
        from app.models.database import engine, Base
        from app.models import orm  # Import all models
        Base.metadata.create_all(bind=engine)
        logger.info("database_tables_created", message="Database tables created successfully")
    except Exception as e:
        logger.error("database_tables_creation_failed", error=str(e))
    
    # Run seed if SEED_ON_STARTUP is true
    if settings.seed_on_startup:
        logger.info("seed_on_startup_enabled", message="Running database seed...")
        try:
            from app.seed_orm import run_seed
            run_seed()
        except Exception as e:
            logger.error("seed_failed", error=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("application_shutdown")
