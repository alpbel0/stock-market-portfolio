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
