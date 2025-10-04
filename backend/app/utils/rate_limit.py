"""
Rate limiting utilities with Redis backend support.
"""
import redis
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request
from ..core.config import get_settings

settings = get_settings()

# Redis client setup (fallback to in-memory dict if Redis not available)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    # Fallback to in-memory storage (not recommended for production)
    _memory_store = {}

class RateLimiter:
    """Rate limiting class with Redis backend."""
    
    def __init__(self, max_attempts: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_attempts: Maximum number of attempts allowed
            time_window: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.time_window = time_window
    
    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed and return remaining time if blocked.
        
        Args:
            key: Unique identifier for the request (e.g., IP address, user ID)
            
        Returns:
            Tuple of (is_allowed, remaining_seconds_if_blocked)
        """
        if REDIS_AVAILABLE:
            return self._redis_check(key)
        else:
            return self._memory_check(key)
    
    def _redis_check(self, key: str) -> tuple[bool, Optional[int]]:
        """Redis-based rate limiting."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        
        # Remove old entries
        redis_client.zremrangebyscore(f"rate_limit:{key}", 0, window_start.timestamp())
        
        # Count current attempts
        current_attempts = redis_client.zcard(f"rate_limit:{key}")
        
        if current_attempts >= self.max_attempts:
            # Get oldest entry to calculate remaining time
            oldest_entries = redis_client.zrange(f"rate_limit:{key}", 0, 0, withscores=True)
            if oldest_entries:
                oldest_timestamp = oldest_entries[0][1]
                oldest_time = datetime.fromtimestamp(oldest_timestamp)
                reset_time = oldest_time + timedelta(seconds=self.time_window)
                remaining_seconds = int((reset_time - now).total_seconds())
                return False, max(remaining_seconds, 0)
            return False, self.time_window
        
        # Add current attempt
        redis_client.zadd(f"rate_limit:{key}", {str(now.timestamp()): now.timestamp()})
        redis_client.expire(f"rate_limit:{key}", self.time_window + 60)  # Add buffer
        
        return True, None
    
    def _memory_check(self, key: str) -> tuple[bool, Optional[int]]:
        """Memory-based rate limiting (fallback)."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        
        if key not in _memory_store:
            _memory_store[key] = []
        
        # Remove old entries
        _memory_store[key] = [
            timestamp for timestamp in _memory_store[key] 
            if timestamp > window_start
        ]
        
        if len(_memory_store[key]) >= self.max_attempts:
            # Calculate remaining time based on oldest entry
            oldest_time = min(_memory_store[key])
            reset_time = oldest_time + timedelta(seconds=self.time_window)
            remaining_seconds = int((reset_time - now).total_seconds())
            return False, max(remaining_seconds, 0)
        
        # Add current attempt
        _memory_store[key].append(now)
        
        return True, None

# Pre-configured rate limiters
login_limiter = RateLimiter(max_attempts=5, time_window=300)  # 5 attempts per 5 minutes
api_limiter = RateLimiter(max_attempts=100, time_window=60)   # 100 requests per minute

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Try to get real IP from proxy headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client IP
    return request.client.host

def check_login_rate_limit(request: Request, identifier: str = None):
    """Check login rate limit and raise exception if exceeded."""
    key = identifier or get_client_ip(request)
    is_allowed, remaining_time = login_limiter.is_allowed(f"login:{key}")
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {remaining_time} seconds.",
            headers={"Retry-After": str(remaining_time)}
        )

def check_api_rate_limit(request: Request, identifier: str = None):
    """Check API rate limit and raise exception if exceeded."""
    key = identifier or get_client_ip(request)
    is_allowed, remaining_time = api_limiter.is_allowed(f"api:{key}")
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {remaining_time} seconds.",
            headers={"Retry-After": str(remaining_time)}
        )