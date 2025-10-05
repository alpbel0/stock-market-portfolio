"""
CRUD operations for Portfolio, Asset, and Transaction models, with dynamic calculations.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List, Optional

from ..models.portfolio import Portfolio
from ..models.asset import Asset, AssetType
from ..models.transaction import Transaction, TransactionType
from ..schemas.portfolio import PortfolioCreate, PortfolioUpdate
from ..schemas.asset import AssetCreate
from ..schemas.transaction import TransactionCreate

# --- Portfolio CRUD --- #

def create_portfolio(db: Session, portfolio_in: PortfolioCreate, user_id: int) -> Portfolio:
    """Create a new portfolio for a user."""
    db_portfolio = Portfolio(**portfolio_in.model_dump(), user_id=user_id)
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def get_portfolios_by_user(db: Session, user_id: int) -> List[Portfolio]:
    """Get all portfolios for a specific user."""
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

def get_portfolio_by_id(db: Session, portfolio_id: int) -> Optional[Portfolio]:
    """Get a single portfolio by ID."""
    return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

def get_portfolio_summary(db: Session, portfolio_id: int) -> Optional[Portfolio]:
    """Get a portfolio and eager load its assets and their transactions."""
    return (
        db.query(Portfolio)
        .filter(Portfolio.id == portfolio_id)
        .options(joinedload(Portfolio.assets).joinedload(Asset.transactions))
        .first()
    )

def update_portfolio(db: Session, portfolio_id: int, portfolio_update: PortfolioUpdate) -> Optional[Portfolio]:
    """Update a portfolio's name or description."""
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not db_portfolio:
        return None
    
    update_data = portfolio_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_portfolio, key, value)
        
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

def delete_portfolio(db: Session, portfolio_id: int) -> bool:
    """Delete a portfolio and its associated assets and transactions."""
    db_portfolio = get_portfolio_summary(db, portfolio_id)
    if not db_portfolio:
        return False
        
    db.delete(db_portfolio)
    db.commit()
    return True

# --- Asset & Transaction --- #

def get_or_create_asset(
    db: Session,
    portfolio_id: int,
    *,
    symbol: str,
    name: str,
    asset_type: AssetType,
) -> Asset:
    """Get or create an asset matching the provided metadata."""

    asset = db.query(Asset).filter(and_(Asset.portfolio_id == portfolio_id, Asset.symbol == symbol)).first()
    if asset:
        updated = False
        if asset.name != name:
            asset.name = name
            updated = True
        if asset.asset_type != asset_type:
            asset.asset_type = asset_type
            updated = True
        if updated:
            db.commit()
            db.refresh(asset)
        return asset

    asset_create = AssetCreate(symbol=symbol, name=name, asset_type=asset_type)
    asset = Asset(**asset_create.model_dump(), portfolio_id=portfolio_id)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

def add_transaction(db: Session, portfolio_id: int, transaction_in: TransactionCreate) -> Transaction:
    """Add a new transaction, creating the asset if it doesn't exist."""

    asset = get_or_create_asset(
        db,
        portfolio_id=portfolio_id,
        symbol=transaction_in.symbol,
        name=transaction_in.asset_name,
        asset_type=transaction_in.asset_type,
    )

    transaction = Transaction(
        portfolio_id=portfolio_id,
        asset_id=asset.id,
        transaction_type=transaction_in.transaction_type,
        quantity=transaction_in.quantity,
        price=transaction_in.price,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    db.refresh(transaction, attribute_names=["asset"])
    return transaction

def get_transactions_by_portfolio(db: Session, portfolio_id: int) -> List[Transaction]:
    """Get all transactions for a specific portfolio."""
    return (
        db.query(Transaction)
        .options(joinedload(Transaction.asset))
        .filter(Transaction.portfolio_id == portfolio_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )


def get_assets_by_portfolio(db: Session, portfolio_id: int) -> List[Asset]:
    """Get all assets for a specific portfolio."""
    return db.query(Asset).filter(Asset.portfolio_id == portfolio_id).all()

def create_asset(db: Session, portfolio_id: int, asset_in: AssetCreate) -> Asset:
    """Create a new asset for a portfolio."""
    asset = Asset(**asset_in.model_dump(), portfolio_id=portfolio_id)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

def update_asset(db: Session, portfolio_id: int, asset_id: int, asset_data: dict) -> Optional[Asset]:
    """Update an existing asset."""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.portfolio_id == portfolio_id)
        .first()
    )
    if not asset:
        return None
    
    for key, value in asset_data.items():
        setattr(asset, key, value)
    
    db.commit()
    db.refresh(asset)
    return asset

def remove_asset(db: Session, portfolio_id: int, asset_id: int) -> bool:
    """Remove an asset and its transactions from a portfolio."""
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.portfolio_id == portfolio_id)
        .first()
    )
    if not asset:
        return False

    db.delete(asset)
    db.commit()
    return True
