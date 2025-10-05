"""
Redis Cache Service - Piyasa verilerini cache'lemek için.
API çağrılarını azaltmak ve performansı artırmak için Redis kullanır.
"""
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import redis
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..models.market_data import MarketData

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis tabанlı cache servisi.
    
    Piyasa verilerini Redis'te cache'leyerek API çağrılarını optimize eder.
    TTL (Time To Live) mekanizması ile cache'in otomatik yenilenmesini sağlar.
    
    Attributes:
        redis_client: Redis bağlantısı
        default_ttl: Varsayılan cache süresi (saniye)
    """
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 300):
        """
        CacheService'i başlat.
        
        Args:
            redis_url: Redis bağlantı URL'i (None ise config'den alınır)
            default_ttl: Varsayılan cache süresi (saniye, default: 300 = 5 dakika)
        """
        settings = get_settings()
        
        # Redis bağlantısını kur
        if redis_url is None:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Bağlantıyı test et
            self.redis_client.ping()
            logger.info(f"Redis connection established: {redis_url}")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {str(e)}")
            # Fallback: Redis olmadan çalışabilir (cache disabled)
            self.redis_client = None
        
        self.default_ttl = default_ttl
        logger.info(f"CacheService initialized with TTL: {default_ttl}s")
    
    def _generate_cache_key(self, symbol: str, source: Optional[str] = None) -> str:
        """
        Cache key oluşturur.
        
        Args:
            symbol: Varlık sembolü
            source: Veri kaynağı (optional)
            
        Returns:
            str: Cache key (format: market_data:SYMBOL veya market_data:SYMBOL:source)
        """
        if source:
            return f"market_data:{symbol.upper()}:{source}"
        return f"market_data:{symbol.upper()}"
    
    def cache_market_data(
        self,
        symbol: str,
        data: Dict[str, Any],
        source: str,
        ttl: Optional[int] = None,
        db: Optional[Session] = None
    ) -> bool:
        """
        Piyasa verisini Redis'e cache'ler ve isteğe bağlı olarak veritabanına kaydeder.
        
        Args:
            symbol: Varlık sembolü
            data: Cache'lenecek veri (dict)
            source: Veri kaynağı (alpha_vantage, coingecko, tcmb, yahoo_finance)
            ttl: Cache süresi (saniye), None ise default_ttl kullanılır
            db: SQLAlchemy session (veritabanına kaydetmek için)
            
        Returns:
            bool: Başarılıysa True
            
        Example:
            >>> cache_service.cache_market_data(
            ...     symbol='AAPL',
            ...     data={'price': 180.5, 'change': 2.5, 'change_percent': 1.4},
            ...     source='alpha_vantage'
            ... )
            True
        """
        if self.redis_client is None:
            logger.warning("Redis not available, cache disabled")
            return False
        
        try:
            cache_key = self._generate_cache_key(symbol, source)
            ttl = ttl or self.default_ttl
            
            # Timestamp ekle
            data['cached_at'] = datetime.utcnow().isoformat()
            data['symbol'] = symbol.upper()
            data['source'] = source
            
            # Redis'e kaydet
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data)
            )
            
            logger.info(f"Cached market data for {symbol} from {source} (TTL: {ttl}s)")
            
            # Veritabanına da kaydet (optional)
            if db is not None:
                self._save_to_database(symbol, data, source, db)
            
            return True
            
        except Exception as e:
            logger.error(f"Error caching market data for {symbol}: {str(e)}")
            return False
    
    def get_cached_price(
        self,
        symbol: str,
        source: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Cache'lenmiş fiyat verisini getirir.
        
        Args:
            symbol: Varlık sembolü
            source: Veri kaynağı (optional, belirtilmezse source'suz key kullanılır)
            
        Returns:
            Optional[Dict]: Cache'lenmiş veri veya None
            
        Example:
            >>> price_data = cache_service.get_cached_price('AAPL', 'alpha_vantage')
            >>> if price_data:
            ...     print(f"Price: {price_data['price']}")
        """
        if self.redis_client is None:
            logger.warning("Redis not available, cache disabled")
            return None
        
        try:
            cache_key = self._generate_cache_key(symbol, source)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.info(f"Cache hit for {symbol} from {source or 'any'}")
                return data
            
            logger.debug(f"Cache miss for {symbol} from {source or 'any'}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached price for {symbol}: {str(e)}")
            return None
    
    def invalidate_cache(
        self,
        symbol: Optional[str] = None,
        source: Optional[str] = None,
        pattern: Optional[str] = None
    ) -> int:
        """
        Cache'i geçersiz kılar (siler).
        
        Args:
            symbol: Varlık sembolü (None ise tüm semboller)
            source: Veri kaynağı (optional)
            pattern: Redis key pattern'i (custom pattern için)
            
        Returns:
            int: Silinen key sayısı
            
        Examples:
            >>> # Belirli bir sembolü sil
            >>> cache_service.invalidate_cache(symbol='AAPL')
            
            >>> # Belirli bir sembol ve kaynağı sil
            >>> cache_service.invalidate_cache(symbol='AAPL', source='alpha_vantage')
            
            >>> # Tüm cache'i temizle
            >>> cache_service.invalidate_cache(pattern='market_data:*')
        """
        if self.redis_client is None:
            logger.warning("Redis not available, cache disabled")
            return 0
        
        try:
            deleted_count = 0
            
            if pattern:
                # Custom pattern kullan
                keys = self.redis_client.keys(pattern)
            elif symbol:
                # Belirli sembol için
                if source:
                    keys = [self._generate_cache_key(symbol, source)]
                else:
                    # Tüm source'lar için
                    keys = self.redis_client.keys(f"market_data:{symbol.upper()}*")
            else:
                # Tüm market_data cache'i
                keys = self.redis_client.keys("market_data:*")
            
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted_count} cache entries")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return 0
    
    def bulk_cache_update(
        self,
        data_list: List[Dict[str, Any]],
        ttl: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, int]:
        """
        Birden fazla piyasa verisini toplu olarak cache'ler.
        
        Args:
            data_list: Cache'lenecek veri listesi
                Her eleman: {'symbol': str, 'data': dict, 'source': str}
            ttl: Cache süresi (saniye)
            db: SQLAlchemy session (veritabanına kaydetmek için)
            
        Returns:
            Dict[str, int]: {'success': int, 'failed': int}
            
        Example:
            >>> data_list = [
            ...     {'symbol': 'AAPL', 'data': {...}, 'source': 'alpha_vantage'},
            ...     {'symbol': 'GOOGL', 'data': {...}, 'source': 'alpha_vantage'},
            ... ]
            >>> result = cache_service.bulk_cache_update(data_list)
            >>> print(f"Success: {result['success']}, Failed: {result['failed']}")
        """
        if self.redis_client is None:
            logger.warning("Redis not available, cache disabled")
            return {'success': 0, 'failed': len(data_list)}
        
        success_count = 0
        failed_count = 0
        
        try:
            # Pipeline kullanarak toplu işlem (performance optimization)
            pipe = self.redis_client.pipeline()
            
            for item in data_list:
                try:
                    symbol = item['symbol']
                    data = item['data']
                    source = item['source']
                    
                    cache_key = self._generate_cache_key(symbol, source)
                    cache_ttl = ttl or self.default_ttl
                    
                    # Timestamp ekle
                    data['cached_at'] = datetime.utcnow().isoformat()
                    data['symbol'] = symbol.upper()
                    data['source'] = source
                    
                    # Pipeline'a ekle
                    pipe.setex(cache_key, cache_ttl, json.dumps(data))
                    
                    # Veritabanına kaydet (optional)
                    if db is not None:
                        self._save_to_database(symbol, data, source, db)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error preparing bulk cache for {item.get('symbol')}: {str(e)}")
                    failed_count += 1
            
            # Pipeline'i çalıştır
            if success_count > 0:
                pipe.execute()
                logger.info(f"Bulk cached {success_count} market data entries")
            
        except Exception as e:
            logger.error(f"Error in bulk cache update: {str(e)}")
            failed_count = len(data_list)
            success_count = 0
        
        return {'success': success_count, 'failed': failed_count}
    
    def _save_to_database(
        self,
        symbol: str,
        data: Dict[str, Any],
        source: str,
        db: Session
    ) -> None:
        """
        Piyasa verisini veritabanına kaydeder.
        
        Args:
            symbol: Varlık sembolü
            data: Kaydedilecek veri
            source: Veri kaynağı
            db: SQLAlchemy session
        """
        try:
            market_data = MarketData(
                symbol=symbol.upper(),
                price=data.get('price'),
                change=data.get('change'),
                change_percent=data.get('change_percent'),
                volume=data.get('volume'),
                timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
                source=source
            )
            
            db.add(market_data)
            db.commit()
            logger.debug(f"Saved market data to database: {symbol}")
            
        except Exception as e:
            logger.error(f"Error saving to database for {symbol}: {str(e)}")
            db.rollback()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Cache istatistiklerini getirir.
        
        Returns:
            Dict: Cache istatistikleri
        """
        if self.redis_client is None:
            return {'status': 'disabled', 'keys': 0}
        
        try:
            keys = self.redis_client.keys("market_data:*")
            info = self.redis_client.info('stats')
            
            return {
                'status': 'active',
                'total_keys': len(keys),
                'total_connections': info.get('total_connections_received', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'status': 'error', 'error': str(e)}


# Singleton instance
_cache_service_instance = None


def get_cache_service() -> CacheService:
    """CacheService singleton instance'ını döner."""
    global _cache_service_instance
    if _cache_service_instance is None:
        _cache_service_instance = CacheService()
    return _cache_service_instance