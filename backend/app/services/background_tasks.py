"""
Background task servisi - Zamanlanmış görevler için.
APScheduler kullanarak periyodik görevleri yönetir.
"""
import logging
from typing import List, Optional
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.services.market_service import get_market_service
from app.services.cache_service import get_cache_service
from app.core.database import SessionLocal
from app.models.portfolio import Portfolio

logger = logging.getLogger(__name__)


class BackgroundTaskService:
    """
    Arka plan görevlerini yöneten servis.
    
    Görevler:
    - Zamanlanmış fiyat çekme
    - Portfolio değer yeniden hesaplama
    - Cache yenileme işleri
    """
    
    def __init__(self):
        """Background task servisini başlat"""
        self.scheduler = AsyncIOScheduler()
        self.market_service = get_market_service()
        self.cache_service = get_cache_service()
        logger.info("BackgroundTaskService initialized")
    
    def start(self):
        """Scheduler'ı başlat ve görevleri planla"""
        try:
            # Her 5 dakikada bir popüler hisse fiyatlarını güncelle
            self.scheduler.add_job(
                self.fetch_popular_stock_prices,
                trigger=IntervalTrigger(minutes=5),
                id="fetch_popular_prices",
                name="Fetch popular stock prices",
                replace_existing=True
            )
            
            # Her 15 dakikada bir portfolio değerlerini yeniden hesapla
            self.scheduler.add_job(
                self.recalculate_portfolio_values,
                trigger=IntervalTrigger(minutes=15),
                id="recalculate_portfolios",
                name="Recalculate portfolio values",
                replace_existing=True
            )
            
            # Her gece saat 02:00'de cache'i temizle
            self.scheduler.add_job(
                self.refresh_cache,
                trigger=CronTrigger(hour=2, minute=0),
                id="refresh_cache",
                name="Refresh cache",
                replace_existing=True
            )
            
            # Her saat başı trend hisseleri güncelle
            self.scheduler.add_job(
                self.update_trending_stocks,
                trigger=CronTrigger(minute=0),
                id="update_trending",
                name="Update trending stocks",
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("Background tasks scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error starting background tasks scheduler: {str(e)}")
            raise
    
    def shutdown(self):
        """Scheduler'ı kapat"""
        try:
            self.scheduler.shutdown()
            logger.info("Background tasks scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")
    
    async def fetch_popular_stock_prices(self):
        """
        Popüler hisse senetlerinin fiyatlarını çeker ve cache'e kaydeder.
        Rate limit'e takılmamak için dikkatli çalışır.
        """
        popular_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "WMT"]
        
        try:
            logger.info(f"Fetching prices for {len(popular_symbols)} popular stocks...")
            
            # Toplu fiyat çekme
            prices = self.market_service.get_bulk_stock_prices(popular_symbols)
            
            # Cache'e kaydet
            pipe = self.cache_service.redis_client.pipeline()
            for symbol, price_data in prices.items():
                if price_data:
                    cache_key = self.cache_service._generate_cache_key(symbol, price_data.get("provider"))
                    pipe.setex(cache_key, 300, json.dumps(price_data))
            pipe.execute()
            
            logger.info(f"Successfully fetched and cached prices for {len(prices)} stocks")
            
        except Exception as e:
            logger.error(f"Error fetching popular stock prices: {str(e)}")
    
    async def recalculate_portfolio_values(self):
        """
        Tüm portfolio'ların güncel değerlerini yeniden hesaplar.
        Her bir portfolio için güncel fiyatları çekerek toplam değeri günceller.
        """
        db = SessionLocal()
        try:
            logger.info("Starting portfolio value recalculation...")
            
            # Tüm aktif portfolio'ları getir
            portfolios = db.query(Portfolio).all()
            
            updated_count = 0
            
            for portfolio in portfolios:
                try:
                    # Portfolio'daki tüm asset'leri al
                    total_value = 0.0
                    
                    for asset in portfolio.assets:
                        # Asset için güncel fiyat çek
                        price_data = self.market_service.get_stock_price(
                            asset.symbol, 
                            provider="yahoo"
                        )
                        
                        if price_data:
                            current_price = price_data.get('price', 0.0)
                            asset_value = current_price * asset.quantity
                            total_value += asset_value
                    
                    # Portfolio'nun toplam değerini güncelle
                    portfolio.total_value = total_value
                    portfolio.updated_at = datetime.utcnow()
                    updated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error recalculating portfolio {portfolio.id}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"Successfully recalculated {updated_count} portfolios")
            
        except Exception as e:
            logger.error(f"Error in portfolio recalculation: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    async def refresh_cache(self):
        """
        Cache'i temizler ve yeni verilerle yeniler.
        Eski ve kullanılmayan cache girdilerini temizler.
        """
        try:
            logger.info("Starting cache refresh...")
            
            # Tüm cache'i temizle (veya sadece eski girdileri)
            # Bu implementasyon cache servisinizin yapısına bağlı
            # Örnek: self.cache_service.clear_expired()
            
            # Kritik verileri yeniden cache'e yükle
            await self.fetch_popular_stock_prices()
            await self.update_trending_stocks()
            
            logger.info("Cache refresh completed successfully")
            
        except Exception as e:
            logger.error(f"Error refreshing cache: {str(e)}")
    
    async def update_trending_stocks(self):
        """
        Trend hisse senetlerini günceller ve cache'e kaydeder.
        """
        try:
            logger.info("Updating trending stocks...")
            
            trending_data = self.market_service.get_trending_stocks()
            
            # Cache'e kaydet (sembol bazlı)
            data_list = [
                {
                    'symbol': symbol,
                    'data': data,
                    'source': data.get('provider', 'yahoo_finance') if isinstance(data, dict) else 'yahoo_finance'
                }
                for symbol, data in (trending_data.items() if isinstance(trending_data, dict) else [])
                if data
            ]
            if data_list:
                self.cache_service.bulk_cache_update(data_list, ttl=3600)
            
            logger.info("Trending stocks updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating trending stocks: {str(e)}")


# Singleton instance
_background_task_service_instance: Optional[BackgroundTaskService] = None


def get_background_task_service() -> BackgroundTaskService:
    """BackgroundTaskService singleton instance'ını döner"""
    global _background_task_service_instance
    if _background_task_service_instance is None:
        _background_task_service_instance = BackgroundTaskService()
    return _background_task_service_instance


def start_background_tasks():
    """Background task'ları başlatır - startup event'te çağrılmalı"""
    service = get_background_task_service()
    service.start()
    logger.info("Background tasks started")


def shutdown_background_tasks():
    """Background task'ları durdurur - shutdown event'te çağrılmalı"""
    service = get_background_task_service()
    service.shutdown()
    logger.info("Background tasks shut down")
