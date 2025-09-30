from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

settings = get_settings()

# The connect_args are specific to SQLite. They are not needed for PostgreSQL.
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# Create the SQLAlchemy engine
# pool_pre_ping=True ensures that the connection is alive before being used.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args
)

# Create a sessionmaker instance
# This is the factory for creating new Session objects.
# autocommit=False and autoflush=False are recommended for modern SQLAlchemy.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base()

# Dependency to get a DB session
def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    It ensures that the session is always closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()