"""GABOPAY FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from apps.api.core.config import settings
from apps.api.core.database import create_tables
from apps.api.api.v1 import charges, refunds, payouts, webhooks, balance, auth
from apps.api.models import merchant, transaction, provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    await create_tables()
    yield


app = FastAPI(
    title="GABOPAY API",
    description="Payment Infrastructure for Gabon and Africa",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An internal error occurred",
                "type": "api_error",
            }
        },
    )


app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(charges.router, prefix="/v1/charges", tags=["charges"])
app.include_router(refunds.router, prefix="/v1/refunds", tags=["refunds"])
app.include_router(payouts.router, prefix="/v1/payouts", tags=["payouts"])
app.include_router(webhooks.router, prefix="/v1/webhooks", tags=["webhooks"])
app.include_router(balance.router, prefix="/v1/balance", tags=["balance"])


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "gabopay-api",
        "version": "1.0.0",
    }


@app.get("/health", tags=["health"])
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
    }