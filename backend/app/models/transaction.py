"""
Defines the Transaction model for recording buy/sell transactions.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
import enum
from sqlalchemy.orm import relationship

from ..core.database import Base

class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Transaction(Base):
    """
    Represents a buy or sell transaction for an asset.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    transaction_type = Column(
        Enum(TransactionType, name="transaction_types", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type}', asset_id={self.asset_id})>"
