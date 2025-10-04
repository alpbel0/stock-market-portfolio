"""Asset model and related domain logic."""
from __future__ import annotations

import enum

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.database import Base


class AssetType(str, enum.Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    ETF = "etf"
    OTHER = "other"


class Asset(Base):
    """Represents a portfolio holding and derives metrics from transactions."""

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

    # Market data
    current_price = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="assets")
    transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")

    # --- Derived metrics -------------------------------------------------

    @property
    def total_quantity(self) -> float:
        """Net quantity (buys - sells) derived from related transactions."""
        from .transaction import TransactionType

        quantity = 0.0
        for tx in self.transactions:
            if tx.transaction_type == TransactionType.BUY:
                quantity += tx.quantity
            elif tx.transaction_type == TransactionType.SELL:
                quantity -= tx.quantity
        return quantity

    @property
    def total_cost(self) -> float:
        """Total acquisition cost computed from buy transactions."""
        from .transaction import TransactionType

        return sum(
            tx.quantity * tx.price
            for tx in self.transactions
            if tx.transaction_type == TransactionType.BUY
        )

    @property
    def average_purchase_price(self) -> float | None:
        """Weighted average price across buy transactions."""
        from .transaction import TransactionType

        buys = [tx for tx in self.transactions if tx.transaction_type == TransactionType.BUY]
        total_qty = sum(tx.quantity for tx in buys)
        if total_qty == 0:
            return None
        total_cost = sum(tx.quantity * tx.price for tx in buys)
        return total_cost / total_qty

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Asset(id={self.id}, symbol='{self.symbol}', portfolio_id={self.portfolio_id})>"
