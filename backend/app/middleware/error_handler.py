from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def generic_error_handler(request: Request, call_next):
    """
    Catches any unhandled exceptions that occur during request processing
    and returns a generic 500 Internal Server Error response.
    This prevents sensitive error details from leaking to the client.
    """
    try:
        return await call_next(request)
    except Exception as e:
        # Log the full exception for debugging purposes on the server
        logger.exception(f"Unhandled exception for request {request.method} {request.url}: {e}")
        
        # Return a generic error response to the client
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected internal server error occurred."}
        )