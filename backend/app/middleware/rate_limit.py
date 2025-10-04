"""Rate limiting middleware that delegates to the shared utility helpers."""
import json

from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ..utils.rate_limit import check_api_rate_limit, check_login_rate_limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply rate limits to sensitive authentication and API routes."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            path = request.url.path

            if path.startswith("/api/v1/auth/login"):
                check_login_rate_limit(request)
            elif path.startswith("/api/"):
                check_api_rate_limit(request)

            if path.startswith("/api/v1/users") and not request.headers.get("Authorization"):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Not authenticated"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            response = await call_next(request)

            if (
                response.status_code == status.HTTP_403_FORBIDDEN
                and not request.headers.get("Authorization")
            ):
                try:
                    payload = json.loads(response.body.decode())
                except Exception:
                    payload = {}
                if payload.get("detail") == "Not authenticated":
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content=payload,
                        headers={"WWW-Authenticate": "Bearer"},
                    )

            return response

        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers,
            )
