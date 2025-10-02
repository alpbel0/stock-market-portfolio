from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    Tracks requests per IP address and enforces rate limits.
    In production, this should be replaced with Redis-based solution
    for better scalability and persistence across server restarts.
    
    Rate limits:
    - Login endpoint: 5 requests per 15 minutes
    - All other endpoints: 100 requests per minute
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Store request timestamps per (client_ip, bucket) pair
        # Buckets isolate login attempts from general traffic so their
        # respective rate limit windows do not interfere with each other.
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)
        
        # Rate limit configurations
        self.login_rate_limit = 5  # 5 attempts
        self.login_window = 900  # 15 minutes in seconds
        
        self.general_rate_limit = 100  # 100 requests
        self.general_window = 60  # 1 minute in seconds
    
    def _clean_old_requests(self, key: Tuple[str, str], window: int):
        """Remove request timestamps outside of the given time window for a bucket."""
        current_time = time.time()
        self.requests[key] = [
            ts for ts in self.requests[key]
            if current_time - ts < window
        ]

    def _is_rate_limited(self, key: Tuple[str, str], limit: int, window: int) -> Tuple[bool, int]:
        """
        Check if the bucket is rate limited for a specific endpoint.
        Returns (is_limited, remaining_requests)
        """
        self._clean_old_requests(key, window)

        requests_count = len(self.requests[key])
        remaining = max(0, limit - requests_count)

        return requests_count >= limit, remaining

    async def dispatch(self, request: Request, call_next):
        """Process each request and apply rate limiting."""
        
        # Get client IP
        client_ip = request.client.host
        path = request.url.path
        
        # Skip rate limiting for health check and info endpoints
        if path in ["/", "/health", "/info"]:
            return await call_next(request)
        
        current_time = time.time()
        
        # Check if this is a login attempt
        is_login = path == "/api/v1/auth/login" and request.method == "POST"
        
        if is_login:
            bucket = (client_ip, "login")
            # Apply stricter rate limit for login attempts
            is_limited, remaining = self._is_rate_limited(
                bucket, self.login_rate_limit, self.login_window
            )

            if is_limited:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many login attempts. Please try again in 15 minutes.",
                        "rate_limit": {
                            "limit": self.login_rate_limit,
                            "window": f"{self.login_window // 60} minutes",
                            "retry_after": "15 minutes"
                        }
                    }
                )
        else:
            bucket = (client_ip, "general")
            # Apply general rate limit
            is_limited, remaining = self._is_rate_limited(
                bucket, self.general_rate_limit, self.general_window
            )

            if is_limited:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Please try again later.",
                        "rate_limit": {
                            "limit": self.general_rate_limit,
                            "window": f"{self.general_window} seconds",
                            "retry_after": f"{self.general_window} seconds"
                        }
                    }
                )
        
        # Record this request
        self.requests[bucket].append(current_time)

        # Continue processing the request
        response = await call_next(request)

        # Add rate limit headers
        if is_login:
            _, remaining = self._is_rate_limited(
                bucket, self.login_rate_limit, self.login_window
            )
            response.headers["X-RateLimit-Limit"] = str(self.login_rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Window"] = f"{self.login_window}s"
        else:
            _, remaining = self._is_rate_limited(
                bucket, self.general_rate_limit, self.general_window
            )
            response.headers["X-RateLimit-Limit"] = str(self.general_rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Window"] = f"{self.general_window}s"

        return response
