from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from ..core.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    currency = Column(String, default="USD", nullable=False)

    # Foreign Key to link to the User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to the User model
    owner = relationship("User", back_populates="portfolios")

    # Relationship to the Transaction model
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}')>"