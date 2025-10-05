"""
Pydantic models for Asset data.
"""
from pydantic import BaseModel
from typing import Optional

class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: str
    quantity: float
    purchase_price: float
    current_price: Optional[float] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    portfolio_id: int

    class Config:
        from_attributes = True
