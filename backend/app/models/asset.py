"""
Defines the Asset model for storing assets within a portfolio.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship

from ..core.database import Base

class Asset(Base):
    """
    Represents a single asset (e.g., stock, crypto) held in a portfolio.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    asset_type = Column(Enum("stock", "crypto", "etf", "other", name="asset_types"), nullable=False)
    
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="assets")

    def __repr__(self):
        return f"<Asset(id={self.id}, symbol='{self.symbol}', portfolio_id={self.portfolio_id})>"

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # e.g., 'stock', 'crypto', 'etf'

    # Relationship to the Transaction model
    transactions = relationship("Transaction", back_populates="asset")

    def __repr__(self):
        return f"<Asset(id={self.id}, symbol='{self.symbol}')>"
