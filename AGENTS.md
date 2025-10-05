# Repository Guidelines

## Project Structure & Module Organization
- `backend/` hosts the FastAPI service: routers in `app/api/v1`, configuration in `app/core`, persistence in `app/crud` and `app/models`, and shared helpers in `app/services` and `app/utils`. Database migrations live in `backend/alembic`.
- `frontend/` delivers the Flutter client with widgets under `lib/`, tests under `test/`, and analyzer settings in `analysis_options.yaml`.
- Operational assets sit in `database/` for seed SQL, `nginx/` for reverse proxy rules, `monitoring/` for Prometheus metrics, and `scripts/` for repeatable tooling.

## Build, Test, and Development Commands
- `docker-compose up --build` assembles the full stack (API, Flutter web, Postgres, Redis, Nginx, Prometheus).
- `cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` runs the API locally with hot reload.
- `cd frontend && flutter run -d web-server --web-port 8081` serves the web client against the local backend.
- `cd backend && pytest` executes backend tests; add `-k "pattern"` to target subsets.
- `cd backend && alembic upgrade head` applies migrations after schema changes; create revisions with `alembic revision --autogenerate -m "summary"`.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, type hints, and concise docstrings across `backend/app`.
- Name Python modules `snake_case.py`, route handlers `verb_noun`, and keep router registrations under `api/v1`.
- For Flutter, use PascalCase for widgets, lowerCamelCase for members, and run `flutter format lib test` prior to commits.

## Testing Guidelines
- Mirror backend modules with `backend/app/tests/test_*.py`, reusing shared fixtures for database and client setup.
- Keep Flutter tests in `frontend/test` and run `flutter test` before opening PRs.
- Target regression coverage for new endpoints, services, and stateful widgets to prevent tombstone bugs.

## Commit & Pull Request Guidelines
- Write imperative commit messages and reference issues when relevant (e.g., `Fix #12: Add portfolio summary endpoint`).
- Each PR should summarize impact, list executed test commands, link issues, and include screenshots or curl snippets for UI/API updates.
- Confirm CI-critical commands (`pytest`, `flutter test`, `docker-compose config`) succeed locally before requesting review.

## Security & Configuration Tips
- Keep secrets in a local `.env` and rotate tokens with `scripts/generate_secret.sh`.
- Revisit `nginx/nginx.conf` and `monitoring/prometheus.yml` whenever routes or metrics change to maintain accurate observability.
