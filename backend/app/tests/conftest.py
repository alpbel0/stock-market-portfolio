"""Shared pytest fixtures for FastAPI backend tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from ..core.database import Base, engine


@pytest.fixture(autouse=True)
def clean_test_database():
    """Reset the SQLite test database before each test function."""
    # Resolve the SQLite file path if applicable
    db_path: Path | None = None
    if engine.url.drivername.startswith("sqlite"):
        raw_path = Path(engine.url.database)
        if raw_path.is_absolute():
            db_path = raw_path
        else:
            # tests/ -> app/ -> backend/
            db_path = Path(__file__).resolve().parents[2] / raw_path
        engine.dispose()
        if db_path.exists():
            db_path.unlink()

    # Recreate schema for a clean state
    import app.models  # noqa: F401  # Ensure all models are registered with the metadata

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
    if db_path and db_path.exists():
        engine.dispose()
        db_path.unlink()
