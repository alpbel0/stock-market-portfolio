from fastapi import FastAPI, Depends, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from .core.config import get_settings, Settings
from .core.database import get_db
from .core.logger import setup_logging
from .middleware.logging_middleware import logging_middleware
from .middleware.error_handler import generic_error_handler
from .middleware.rate_limit import RateLimitMiddleware
from .api.v1 import auth, users, portfolio


# Setup logging
setup_logging()

# Initialize the FastAPI app
app = FastAPI(title="Stock Market Portfolio API")

# --- Middleware Configuration ---

# Note: Middleware is processed in the reverse order of how it's added.
# 1. Logging Middleware (runs first on request, last on response)
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

# 2. Rate Limiting Middleware (protects against abuse)
app.add_middleware(RateLimitMiddleware)

# 3. Error Handling Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=generic_error_handler)

# 4. CORS Middleware (runs last on request, first on response)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().ALLOWED_ORIGINS,  # Read directly for middleware
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["User Management"])
app.include_router(portfolio.router, prefix="/api/v1")

# --- API Endpoints ---

@app.get("/info", tags=["Information"])
def get_info(settings: Settings = Depends(get_settings)):
    """
    Returns basic information about the API, such as project name and version.
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "api_version": settings.API_VERSION,
    }


@app.get("/")
def read_root(settings: Settings = Depends(get_settings)):
    """A simple root endpoint to confirm the API is running."""
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health", tags=["Health Check"])
def health_check(db: Session = Depends(get_db)):
    """
    Checks the health of the application, including the database connection.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = "error"
        raise HTTPException(
            status_code=503,
            detail=f"Database connection error: {e}"
        )

    return {
        "status": "ok",
        "services": {
            "database": db_status
        }
    }
