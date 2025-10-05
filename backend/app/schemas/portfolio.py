"""
Pydantic models for Portfolio data.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from .asset import Asset

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
    assets: List[Asset] = Field(default_factory=list)

    class Config:
        from_attributes = True

class PortfolioValue(BaseModel):
    total_value: float
    total_cost: float
    profit_loss: float
