"""
External API entegrasyonları için Market Data Service.
Alpha Vantage, CoinGecko, TCMB ve Yahoo Finance API'lerini kullanır.
"""
import logging
from typing import Optional, Dict, Any, List
import xml.etree.ElementTree as ET
import time

import requests
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.symbol_search import SymbolSearch
from pycoingecko import CoinGeckoAPI

from ..core.config import get_settings
from ..utils.exceptions import (
    APIRateLimitException,
    DataSourceUnavailableException,
    MarketDataNotFoundException,
    ExternalAPIException
)

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Farklı kaynaklardan piyasa verilerini çeken servis sınıfı.
    
    Desteklenen veri kaynakları:
    - Alpha Vantage: Hisse senedi fiyatları ve sembol arama
    - CoinGecko: Kripto para fiyatları
    - TCMB: Döviz kurları
    - Yahoo Finance: Genel finans verileri
    """
    
    def __init__(self):
        """Market Data Service'i başlat ve API client'larını yapılandır."""
        settings = get_settings()
        
        # Alpha Vantage API key yapılandırmadan alınmalı
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        if not self.alpha_vantage_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY ayarlanmalı ve boş bırakılamaz.")
        self.ts = TimeSeries(key=self.alpha_vantage_key, output_format='json')
        self.ss = SymbolSearch(key=self.alpha_vantage_key, output_format='json')

        
        # CoinGecko API key yapılandırmadan alınmalı
        self.coingecko_key = getattr(settings, 'COINGECKO_API_KEY', None)
        if not self.coingecko_key:
            raise ValueError("COINGECKO_API_KEY ayarlanmalı ve boş bırakılamaz.")
        self.cg = CoinGeckoAPI(api_key=self.coingecko_key)
        
        # TCMB XML URL
        self.tcmb_url = 'https://www.tcmb.gov.tr/kurlar/today.xml'
        
        logger.info("MarketDataService initialized successfully")

    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """
        Alpha Vantage kullanarak hisse senedi sembollerini arar.
        
        Args:
            query: Aranacak anahtar kelime.
            
        Returns:
            Aramayla eşleşen sembollerin listesi.
        """
        try:
            data, _ = self.ss.get_symbol_search(keywords=query)
            return data
        except Exception as e:
            logger.error(f"Alpha Vantage symbol search error for query '{query}': {str(e)}")
            raise

    def get_trending_stocks(self) -> List[Dict[str, Any]]:
        """
        Yahoo Finance'dan popüler veya en çok işlem gören hisseleri çeker.
        Şimdilik popüler hisselerden oluşan statik bir liste döndüreceğiz.
        TODO: Dinamik bir trending endpoint'i bulunup entegre edilebilir (örn: Yahoo Finance screener'lar).
        """
        # For now, returning a static list of popular tech stocks.
        trending_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        return self.get_bulk_stock_prices(trending_symbols)

    def get_bulk_stock_prices(self, symbols: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Verilen sembol listesi için toplu hisse senedi fiyatlarını çeker.
        
        Args:
            symbols: Fiyatları alınacak hisse senedi sembollerinin listesi.
            
        Returns:
            Her sembol için fiyat bilgilerini içeren bir sözlük.
        """
        prices = {}
        for symbol in symbols:
            try:
                prices[symbol] = self.get_stock_price(symbol, provider="yahoo")
            except Exception as e:
                logger.warning(f"Could not fetch price for symbol {symbol}: {e}")
                prices[symbol] = None
        return prices
        logger.info("MarketDataService initialized successfully")
    
    def get_stock_price(self, symbol: str, provider: str = "alpha_vantage", use_fallback: bool = True) -> Optional[Dict[str, Any]]:
        """
        Hisse senedi fiyatını çeker. Fallback mekanizması ile alternatif kaynaklara geçiş yapar.
        
        Args:
            symbol: Hisse senedi sembolü (örn: 'AAPL', 'GOOGL')
            provider: Veri kaynağı ('alpha_vantage' veya 'yahoo')
            use_fallback: Birincil kaynak başarısız olursa alternatif kaynaklara geçiş yap
            
        Returns:
            Dict: {
                'symbol': str,
                'price': float,
                'currency': str,
                'timestamp': str,
                'provider': str,
                'is_fallback': bool  # Fallback kullanıldıysa True
            }
            
        Raises:
            MarketDataNotFoundException: Veri bulunamazsa
            DataSourceUnavailableException: Tüm veri kaynakları kullanılamazsa
        """
        providers_to_try = [provider]
        
        # Fallback aktifse alternatif provider'ları ekle
        if use_fallback:
            if provider == "alpha_vantage":
                providers_to_try.append("yahoo")
            else:  # yahoo
                providers_to_try.append("alpha_vantage")
        
        last_exception = None
        
        for idx, current_provider in enumerate(providers_to_try):
            try:
                is_fallback = idx > 0  # İlk provider değilse fallback
                
                if current_provider == "alpha_vantage":
                    result = self._get_stock_price_alpha_vantage(symbol)
                elif current_provider == "yahoo":
                    result = self._get_stock_price_yahoo(symbol)
                else:
                    continue
                
                # Fallback kullanıldıysa işaretle
                if result:
                    result['is_fallback'] = is_fallback
                    if is_fallback:
                        logger.info(f"Using fallback provider '{current_provider}' for {symbol}")
                    return result
                    
            except Exception as e:
                last_exception = e
                logger.warning(f"Provider '{current_provider}' failed for {symbol}: {str(e)}")
                
                # Rate limit hatası ise bekle ve tekrar dene
                if "rate limit" in str(e).lower() or "429" in str(e):
                    if use_fallback and idx < len(providers_to_try) - 1:
                        logger.info(f"Rate limit hit for '{current_provider}', trying fallback...")
                        continue
                    else:
                        raise APIRateLimitException(provider=current_provider, retry_after=60)
                
                # Son provider da başarısız olursa exception fırlat
                if idx == len(providers_to_try) - 1:
                    if "not found" in str(e).lower() or "404" in str(e):
                        raise MarketDataNotFoundException(symbol=symbol, asset_type="stock")
                    raise DataSourceUnavailableException(
                        source="all_providers",
                        reason=f"All providers failed. Last error: {str(last_exception)}"
                    )
        
        # Hiçbir provider çalışmadıysa
        raise DataSourceUnavailableException(
            source="all_providers",
            reason=f"Could not fetch data from any provider. Last error: {str(last_exception)}"
        )
    
    def _get_stock_price_alpha_vantage(self, symbol: str) -> Dict[str, Any]:
        """Alpha Vantage'den hisse senedi fiyatı çeker."""
        try:
            data, meta_data = self.ts.get_quote_endpoint(symbol=symbol)
            
            return {
                'symbol': symbol,
                'price': float(data['05. price']),
                'currency': 'USD',
                'timestamp': data['07. latest trading day'],
                'change': float(data['09. change']),
                'change_percent': data['10. change percent'],
                'provider': 'alpha_vantage'
            }
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {str(e)}")
            raise
    
    def _get_stock_price_yahoo(self, symbol: str) -> Dict[str, Any]:
        """Yahoo Finance'den hisse senedi fiyatı çeker."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='1d')
            
            if hist.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
            
            current_price = hist['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'price': float(current_price),
                'currency': info.get('currency', 'USD'),
                'timestamp': str(hist.index[-1]),
                'market_cap': info.get('marketCap'),
                'provider': 'yahoo_finance'
            }
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {str(e)}")
            raise
    
    def get_crypto_price(self, symbol: str, vs_currency: str = "usd") -> Optional[Dict[str, Any]]:
        """
        Kripto para fiyatını CoinGecko'dan çeker.
        
        Args:
            symbol: Kripto para sembolü (örn: 'bitcoin', 'ethereum')
            vs_currency: Karşılaştırma para birimi (default: 'usd')
            
        Returns:
            Dict: {
                'symbol': str,
                'price': float,
                'currency': str,
                'market_cap': float,
                'volume_24h': float,
                'change_24h': float,
                'provider': str
            }
            
        Raises:
            Exception: API hatası durumunda
        """
        try:
            # CoinGecko API kullanarak fiyat bilgisi al
            data = self.cg.get_price(
                ids=symbol.lower(),
                vs_currencies=vs_currency,
                include_market_cap=True,
                include_24hr_vol=True,
                include_24hr_change=True
            )
            
            if not data or symbol.lower() not in data:
                raise ValueError(f"Crypto not found: {symbol}")
            
            crypto_data = data[symbol.lower()]
            
            return {
                'symbol': symbol,
                'price': crypto_data[vs_currency],
                'currency': vs_currency.upper(),
                'market_cap': crypto_data.get(f'{vs_currency}_market_cap'),
                'volume_24h': crypto_data.get(f'{vs_currency}_24h_vol'),
                'change_24h': crypto_data.get(f'{vs_currency}_24h_change'),
                'provider': 'coingecko'
            }
            
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {str(e)}")
            raise
    
    def get_currency_rate(self, currency_code: str, base_currency: str = "TRY") -> Optional[Dict[str, Any]]:
        """
        Döviz kurunu TCMB'den çeker.
        
        Args:
            currency_code: Döviz kodu (örn: 'USD', 'EUR', 'GBP')
            base_currency: Temel para birimi (default: 'TRY')
            
        Returns:
            Dict: {
                'currency_code': str,
                'base_currency': str,
                'buying_rate': float,
                'selling_rate': float,
                'effective_buying': float,
                'effective_selling': float,
                'timestamp': str,
                'provider': str
            }
            
        Raises:
            Exception: API hatası durumunda
        """
        try:
            response = requests.get(self.tcmb_url, timeout=10)
            response.raise_for_status()
            
            # XML'i parse et
            root = ET.fromstring(response.content)
            
            # İlgili dövizi bul
            for currency in root.findall('Currency'):
                kod = currency.get('Kod')
                if kod == currency_code:
                    return {
                        'currency_code': currency_code,
                        'base_currency': base_currency,
                        'currency_name': currency.find('CurrencyName').text if currency.find('CurrencyName') is not None else None,
                        'buying_rate': float(currency.find('ForexBuying').text) if currency.find('ForexBuying') is not None and currency.find('ForexBuying').text else None,
                        'selling_rate': float(currency.find('ForexSelling').text) if currency.find('ForexSelling') is not None and currency.find('ForexSelling').text else None,
                        'effective_buying': float(currency.find('BanknoteBuying').text) if currency.find('BanknoteBuying') is not None and currency.find('BanknoteBuying').text else None,
                        'effective_selling': float(currency.find('BanknoteSelling').text) if currency.find('BanknoteSelling') is not None and currency.find('BanknoteSelling').text else None,
                        'timestamp': root.get('Tarih') + ' ' + root.get('Date'),
                        'provider': 'tcmb'
                    }
            
            raise ValueError(f"Currency not found: {currency_code}")
            
        except Exception as e:
            logger.error(f"Error fetching currency rate for {currency_code}: {str(e)}")
            raise
    
    def get_commodity_price(self, commodity: str) -> Optional[Dict[str, Any]]:
        """
        Emtia fiyatını Yahoo Finance'den çeker.
        
        Args:
            commodity: Emtia sembolü (örn: 'GC=F' for Gold, 'CL=F' for Crude Oil)
            
        Yaygın emtia sembolleri:
            - GC=F: Altın (Gold)
            - SI=F: Gümüş (Silver)
            - CL=F: Ham Petrol (Crude Oil)
            - NG=F: Doğal Gaz (Natural Gas)
            
        Returns:
            Dict: {
                'commodity': str,
                'price': float,
                'currency': str,
                'timestamp': str,
                'change': float,
                'change_percent': float,
                'provider': str
            }
            
        Raises:
            Exception: API hatası durumunda
        """
        try:
            ticker = yf.Ticker(commodity)
            hist = ticker.history(period='2d')
            
            if hist.empty:
                raise ValueError(f"No data found for commodity: {commodity}")
            
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - previous_price
            change_percent = (change / previous_price * 100) if previous_price != 0 else 0
            
            return {
                'commodity': commodity,
                'price': float(current_price),
                'currency': 'USD',
                'timestamp': str(hist.index[-1]),
                'change': float(change),
                'change_percent': float(change_percent),
                'provider': 'yahoo_finance'
            }
            
        except Exception as e:
            logger.error(f"Error fetching commodity price for {commodity}: {str(e)}")
            raise


# Singleton instance
_market_service_instance = None


def get_market_service() -> MarketDataService:
    """MarketDataService singleton instance'ını döner."""
    global _market_service_instance
    if _market_service_instance is None:
        _market_service_instance = MarketDataService()
    return _market_service_instance
