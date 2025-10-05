"""
Özel exception sınıfları - API hata yönetimi için.
"""
from typing import Optional, Any, Dict


class AppException(Exception):
    """Temel uygulama exception sınıfı"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class APIRateLimitException(AppException):
    """API rate limit aşıldığında fırlatılır"""
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        message = f"API rate limit exceeded for provider: {provider}"
        details = {"provider": provider}
        if retry_after:
            details["retry_after"] = retry_after
            message += f". Retry after {retry_after} seconds."
        super().__init__(message, status_code=429, details=details)


class DataSourceUnavailableException(AppException):
    """Veri kaynağı kullanılamadığında fırlatılır"""
    def __init__(self, source: str, reason: Optional[str] = None):
        message = f"Data source '{source}' is unavailable"
        if reason:
            message += f": {reason}"
        super().__init__(message, status_code=503, details={"source": source, "reason": reason})


class MarketDataNotFoundException(AppException):
    """Market verisi bulunamadığında fırlatılır"""
    def __init__(self, symbol: str, asset_type: str = "stock"):
        message = f"Market data not found for {asset_type}: {symbol}"
        super().__init__(message, status_code=404, details={"symbol": symbol, "asset_type": asset_type})


class InvalidSymbolException(AppException):
    """Geçersiz sembol belirtildiğinde fırlatılır"""
    def __init__(self, symbol: str):
        message = f"Invalid symbol: {symbol}"
        super().__init__(message, status_code=400, details={"symbol": symbol})


class ExternalAPIException(AppException):
    """Harici API hatası"""
    def __init__(self, provider: str, error_message: str):
        message = f"External API error from {provider}: {error_message}"
        super().__init__(message, status_code=502, details={"provider": provider, "error": error_message})