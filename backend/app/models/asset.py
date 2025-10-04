"""
Defines the Asset model for storing assets within a portfolio.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum, UniqueConstraint
import enum
from sqlalchemy.orm import relationship

from ..core.database import Base

class AssetType(str, enum.Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    ETF = "etf"
    OTHER = "other"


class Asset(Base):
    """
    Represents a single asset (e.g., stock, crypto) held in a portfolio.
    """
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "symbol", name="uq_portfolio_symbol"),
    )

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    asset_type = Column(
        Enum(AssetType, name="asset_types", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="assets")
    transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Asset(id={self.id}, symbol='{self.symbol}', portfolio_id={self.portfolio_id})>"
