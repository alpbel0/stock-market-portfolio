"""
CRUD operations for Portfolio, Asset, and Transaction models.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..models.portfolio import Portfolio
from ..models.asset import Asset
from ..models.transaction import Transaction
from ..schemas.portfolio import PortfolioCreate, PortfolioUpdate
from ..schemas.asset import AssetCreate, AssetUpdate

# --- Portfolio CRUD --- #

def create_portfolio(db: Session, portfolio: PortfolioCreate, user_id: int) -> Portfolio:
    """Create a new portfolio for a user."""
    db_portfolio = Portfolio(**portfolio.model_dump(), user_id=user_id)
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def get_portfolios_by_user(db: Session, user_id: int) -> List[Portfolio]:
    """Get all portfolios for a specific user."""
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

def get_portfolio_by_id(db: Session, portfolio_id: int) -> Optional[Portfolio]:
    """Get a single portfolio by its ID."""
    return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

def update_portfolio(db: Session, portfolio_id: int, portfolio_update: PortfolioUpdate) -> Optional[Portfolio]:
    """Update a portfolio's details."""
    db_portfolio = get_portfolio_by_id(db, portfolio_id)
    if not db_portfolio:
        return None
    
    update_data = portfolio_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_portfolio, key, value)
        
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def delete_portfolio(db: Session, portfolio_id: int) -> bool:
    """Delete a portfolio."""
    db_portfolio = get_portfolio_by_id(db, portfolio_id)
    if not db_portfolio:
        return False
        
    db.delete(db_portfolio)
    db.commit()
    return True

# --- Asset CRUD --- #

def add_asset_to_portfolio(db: Session, asset: AssetCreate, portfolio_id: int) -> Asset:
    """Add a new asset to a portfolio."""
    db_asset = Asset(**asset.model_dump(), portfolio_id=portfolio_id)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def get_assets_by_portfolio(db: Session, portfolio_id: int) -> List[Asset]:
    """Get all assets for a specific portfolio."""
    return db.query(Asset).filter(Asset.portfolio_id == portfolio_id).all()

def update_asset(db: Session, asset_id: int, asset_update: AssetUpdate) -> Optional[Asset]:
    """Update an asset's details."""
    db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not db_asset:
        return None
    
    update_data = asset_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_asset, key, value)
        
    db.commit()
    db.refresh(db_asset)
    return db_asset

def remove_asset(db: Session, asset_id: int) -> bool:
    """Remove an asset from a portfolio."""
    db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not db_asset:
        return False
        
    db.delete(db_asset)
    db.commit()
    return True

# --- Calculation Logic --- #

def calculate_portfolio_value(db: Session, portfolio_id: int) -> dict:
    """
    Dynamically calculate the total value, cost, and profit/loss of a portfolio.
    This is a simplified calculation. Real-world scenarios would involve fetching live prices.
    """
    total_value = 0.0
    total_cost = 0.0

    assets = get_assets_by_portfolio(db, portfolio_id)

    for asset in assets:
        # For simplicity, current_price is used. In a real app, this would be fetched live.
        current_price = asset.current_price or asset.purchase_price
        
        asset_value = asset.quantity * current_price
        asset_cost = asset.quantity * asset.purchase_price
        
        total_value += asset_value
        total_cost += asset_cost

    profit_loss = total_value - total_cost
    
    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "profit_loss": profit_loss
    }