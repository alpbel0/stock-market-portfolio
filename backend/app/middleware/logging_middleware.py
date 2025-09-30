import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    """
    Logs incoming requests and outgoing responses.
    Calculates the processing time for each request.
    """
    start_time = time.time()
    
    # Log the incoming request
    logger.info(f"Request:  {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"
    
    # Log the outgoing response
    logger.info(f"Response: {response.status_code} (took {formatted_process_time})")
    
    return response
