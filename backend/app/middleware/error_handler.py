from fastapi import Request
from fastapi.responses import JSONResponse
import logging

from app.utils.exceptions import (
    AppException,
    APIRateLimitException,
    DataSourceUnavailableException,
    MarketDataNotFoundException,
    InvalidSymbolException,
    ExternalAPIException
)

logger = logging.getLogger(__name__)

async def generic_error_handler(request: Request, call_next):
    """
    Özel exception'ları yakalar ve uygun HTTP yanıtlarını döndürür.
    Hassas hata detaylarının istemciye sızmasını engeller.
    Graceful degradation ile kullanıcı dostu hata mesajları sağlar.
    """
    try:
        return await call_next(request)
    
    except AppException as e:
        # Özel uygulama exception'larını yakala
        logger.warning(
            f"App exception for {request.method} {request.url}: "
            f"{e.message} (status: {e.status_code})"
        )
        
        response_content = {
            "detail": e.message,
            "status_code": e.status_code
        }
        
        # Ek detaylar varsa ekle
        if e.details:
            response_content["details"] = e.details
        
        # Rate limit exception'ları için özel header ekle
        headers = {}
        if isinstance(e, APIRateLimitException) and "retry_after" in e.details:
            headers["Retry-After"] = str(e.details["retry_after"])
        
        return JSONResponse(
            status_code=e.status_code,
            content=response_content,
            headers=headers
        )
    
    except Exception as e:
        # Beklenmeyen tüm diğer exception'lar için
        logger.exception(f"Unhandled exception for request {request.method} {request.url}: {e}")
        
        # Genel bir hata yanıtı döndür (güvenlik için detaylar gizli)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Beklenmeyen bir sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.",
                "status_code": 500
            }
        )
