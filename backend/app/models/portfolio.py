"""
Defines the Portfolio model for storing user portfolio information.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
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
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="portfolios")
    assets = relationship("Asset", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    # --- Calculated Properties ---

    @property
    def total_value(self) -> float:
        """Aggregate current market value of all assets in this portfolio."""
        value = 0.0
        for asset in self.assets:
            if asset.current_price is not None:
                value += asset.current_price * asset.quantity
        return value

    @property
    def total_cost(self) -> float:
        """Aggregate acquisition cost based on purchase price of assets."""
        return sum(asset.purchase_price * asset.quantity for asset in self.assets)

    @property
    def profit_loss(self) -> float:
        """Difference between current value and total cost."""
        return self.total_value - self.total_cost
