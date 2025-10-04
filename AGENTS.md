# Repository Guidelines

## Project Structure & Module Organization
- `backend/` holds the FastAPI service. Core code lives under `backend/app` with routers in `api/v1`, shared logic in `core`, persistence in `crud` and `models`, and reusable utilities in `services` and `utils`. Database migrations reside in `backend/alembic`.
- `frontend/` contains the Flutter client (`lib` widgets, `test` specs) with analyzer configuration in `analysis_options.yaml`.
- Infrastructure helpers are in `database/` (seed SQL), `nginx/` (reverse proxy), `monitoring/` (Prometheus config), and `scripts/` for shell automation.

## Build, Test, and Development Commands
- `docker-compose up --build` brings up the full stack (backend, frontend, Postgres, Redis, Nginx, Prometheus).
- `cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` launches the API for local development outside Docker.
- `cd frontend && flutter run -d web-server --web-port 8081` serves the Flutter client against the local backend.
- `cd backend && pytest` executes backend unit tests; add `-k` filters for targeted runs.
- `cd backend && alembic upgrade head` applies database migrations; generate new revisions with `alembic revision --autogenerate -m "short summary"`.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, concise docstrings, and type hints throughout `backend/app`. Name modules `snake_case.py` and route handlers `verb_noun`.
- Keep FastAPI routers under `api/v1` and expose dependencies through `core` to match the existing layering.
- In Flutter code, prefer lowerCamelCase for members and PascalCase for widgets; run `flutter format lib test` before committing.

## Testing Guidelines
- Backend tests live under `backend/app/tests/test_*.py`; mirror module names (e.g., `test_portfolio.py` for `portfolio.py`) and rely on shared fixtures for database or client setup.
- Frontend widget and integration tests belong in `frontend/test`; run `flutter test` before submitting changes.
- Aim for coverage on new endpoints, services, and stateful widgets, and include regression scenarios for bug fixes.

## Commit & Pull Request Guidelines
- Commit messages should stay imperative and reference issues when relevant (e.g., `Fix #12: Add portfolio summary endpoint`); keep logical changes isolated.
- Pull requests must summarize the impact, list test commands executed, link issues, and attach screenshots or curl snippets for UI or API changes.
- Ensure CI-critical commands (`pytest`, `flutter test`, `docker-compose config`) succeed locally before requesting review.

## Security & Configuration Tips
- Store secrets in a local `.env`; never commit credentials. Use `scripts/generate_secret.sh` to rotate tokens.
- Review `nginx/nginx.conf` and `monitoring/prometheus.yml` whenever backend routes or metrics change to keep observability accurate.
