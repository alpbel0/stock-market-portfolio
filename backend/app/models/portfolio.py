"""
Defines the Portfolio model for storing user portfolio information.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from ..core.database import Base

class Portfolio(Base):
    """
    Represents a user's investment portfolio.
    """
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Calculated fields
    total_value = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="portfolios")
    assets = relationship("Asset", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', user_id={self.user_id})>"
