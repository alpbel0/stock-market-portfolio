from fastapi import FastAPI, Depends, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from .core.config import get_settings
from .core.database import get_db
from .core.logger import setup_logging
from .middleware.logging_middleware import logging_middleware
from .middleware.error_handler import generic_error_handler

# Setup logging
setup_logging()

# Get settings instance
settings = get_settings()

# Initialize the FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# --- Middleware Configuration ---

# Note: Middleware is processed in the reverse order of how it's added.
# 1. Logging Middleware (runs first on request, last on response)
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

# 2. Error Handling Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=generic_error_handler)

# 3. CORS Middleware (runs last on request, first on response)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/info", tags=["Information"])
def get_info(app_settings: Settings = Depends(get_settings)):
    """
    Returns basic information about the API, such as project name and version.
    """
    return {
        "project_name": app_settings.PROJECT_NAME,
        "api_version": app_settings.API_VERSION,
    }


@app.get("/")
def read_root():
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
