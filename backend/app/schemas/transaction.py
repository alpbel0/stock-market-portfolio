"""
Pydantic modeller for Transaction verileri.
"""
from datetime import datetime

from pydantic import BaseModel, Field

from ..models.transaction import TransactionType
from ..models.asset import AssetType
from .asset import Asset


class TransactionBase(BaseModel):
    """İşlemlerin ortak alanları."""

    transaction_type: TransactionType
    quantity: float
    price: float


class TransactionCreate(TransactionBase):
    """Yeni işlem oluştururken kullanılan alanlar."""

    symbol: str
    asset_name: str
    asset_type: AssetType


class Transaction(TransactionBase):
    """API yanıtlarında dönen işlem modeli."""

    id: int
    portfolio_id: int
    asset_id: int
    total_amount: float = Field(..., description="İşlemin toplam tutarı (quantity * price).")
    created_at: datetime
    asset: Asset

    class Config:
        from_attributes = True
