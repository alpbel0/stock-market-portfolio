"""
MarketData model - Piyasa verilerini veritabanında saklamak için.
Symbol, fiyat, değişim, hacim gibi piyasa bilgilerini içerir.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, func, Index
from sqlalchemy.sql import text

from ..core.database import Base


class MarketData(Base):
    """
    Piyasa verilerini saklayan model.
    
    Bu model, farklı kaynaklardan (Alpha Vantage, CoinGecko, TCMB, Yahoo Finance)
    gelen piyasa verilerini veritabanında saklar. Cache mekanizması ile birlikte
    çalışarak API çağrılarını optimize eder.
    
    Attributes:
        id: Primary key
        symbol: Varlık sembolü (örn: 'AAPL', 'BTC', 'USD')
        price: Güncel fiyat
        change: Fiyat değişimi (mutlak)
        change_percent: Fiyat değişimi (yüzde)
        volume: İşlem hacmi (varsa)
        timestamp: Veri zamanı (UTC)
        source: Veri kaynağı (alpha_vantage, coingecko, tcmb, yahoo_finance)
        created_at: Kayıt oluşturma zamanı
        updated_at: Son güncelleme zamanı
    """
    
    __tablename__ = "market_data"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Market Data Fields
    symbol = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String, nullable=False)  # alpha_vantage, coingecko, tcmb, yahoo_finance
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('ix_market_data_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_market_data_symbol_source', 'symbol', 'source'),
    )
    
    def __repr__(self) -> str:
        """String representation of MarketData."""
        return f"<MarketData(symbol='{self.symbol}', price={self.price}, source='{self.source}')>"
    
    def to_dict(self) -> dict:
        """
        Model nesnesini dictionary'ye çevirir.
        
        Returns:
            dict: Model verilerini içeren dictionary
        """
        return {
            'id': self.id,
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
