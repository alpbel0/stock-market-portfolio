"""
Pydantic models for Transaction data.
"""
from pydantic import BaseModel
from datetime import datetime

from ..models.transaction import TransactionType
from ..models.asset import AssetType

class TransactionBase(BaseModel):
    symbol: str
    asset_name: str
    asset_type: AssetType
    transaction_type: TransactionType
    quantity: float
    price: float

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    portfolio_id: int
    asset_id: int
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True
