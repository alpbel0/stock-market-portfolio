"""
Pydantic models for Portfolio data, including summaries.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .asset import Asset, AssetSummary

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PortfolioSummary(Portfolio):
    total_value: float = Field(..., description="Total current market value of all assets.")
    total_cost: float = Field(..., description="Total acquisition cost of all assets.")
    profit_loss: float = Field(..., description="Total profit or loss (total_value - total_cost).")
    assets: List[AssetSummary] = Field([], description="List of assets with their derived metrics.")
