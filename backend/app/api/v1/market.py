from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.services.market_service import get_market_service, MarketDataService

router = APIRouter()


class BulkPricesRequest(BaseModel):
    """Toplu fiyat sorgulama için request modeli"""
    symbols: List[str]


@router.get("/")
async def get_market_data():
    """Market API'sinin ana endpoint'i"""
    return {
        "message": "Market Data API",
        "version": "v1",
        "endpoints": {
            "price": "/price/{symbol}",
            "search": "/search/{query}",
            "trending": "/trending",
            "bulk_prices": "/bulk-prices"
        }
    }


@router.get("/price/{symbol}")
async def get_price(
    symbol: str,
    provider: str = Query(default="yahoo", description="Veri sağlayıcı: 'alpha_vantage' veya 'yahoo'")
):
    """
    Belirtilen sembol için hisse senedi fiyatını getirir.
    
    Args:
        symbol: Hisse senedi sembolü (örn: AAPL, GOOGL)
        provider: Veri sağlayıcı (alpha_vantage veya yahoo)
        
    Returns:
        Fiyat bilgilerini içeren dict
    """
    try:
        market_service = get_market_service()
        price_data = market_service.get_stock_price(symbol, provider=provider)
        return price_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fiyat bilgisi alınırken hata oluştu: {str(e)}"
        )


@router.get("/search/{query}")
async def search_market(query: str):
    """
    Hisse senedi sembollerini arar.
    
    Args:
        query: Aranacak anahtar kelime
        
    Returns:
        Eşleşen sembollerin listesi
    """
    try:
        market_service = get_market_service()
        results = market_service.search_symbols(query)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sembol araması yapılırken hata oluştu: {str(e)}"
        )


@router.get("/trending")
async def get_trending():
    """
    Popüler ve trend olan hisse senetlerini getirir.
    
    Returns:
        Trend hisse senetlerinin fiyat bilgileri
    """
    try:
        market_service = get_market_service()
        trending_data = market_service.get_trending_stocks()
        return {"trending": trending_data}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trend verileri alınırken hata oluştu: {str(e)}"
        )


@router.post("/bulk-prices")
async def get_bulk_prices(request: BulkPricesRequest):
    """
    Birden fazla sembol için toplu fiyat bilgisi getirir.
    
    Args:
        request: Sembol listesini içeren request body
        
    Returns:
        Her sembol için fiyat bilgilerini içeren dict
    """
    try:
        if not request.symbols:
            raise HTTPException(status_code=400, detail="En az bir sembol belirtilmelidir")
        
        market_service = get_market_service()
        prices = market_service.get_bulk_stock_prices(request.symbols)
        return {"prices": prices}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Toplu fiyat bilgisi alınırken hata oluştu: {str(e)}"
        )
