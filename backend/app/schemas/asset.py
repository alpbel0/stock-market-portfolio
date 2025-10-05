"""
Pydantic models for Asset data, including derived metrics.
"""
from pydantic import BaseModel, Field
from typing import Optional

from ..models.asset import AssetType

class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: AssetType

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    asset_type: Optional[AssetType] = None

class Asset(AssetBase):
    id: int
    portfolio_id: int
    current_price: Optional[float] = Field(None, description="Current market price of the asset.")

    class Config:
        from_attributes = True

class AssetSummary(Asset):
    total_quantity: float = Field(..., description="Net quantity of the asset held.")
    total_cost: float = Field(..., description="Total acquisition cost of the asset.")
    average_purchase_price: Optional[float] = Field(None, description="Weighted average purchase price.")
