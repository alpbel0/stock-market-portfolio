"""
API endpoints for managing portfolios and assets.
"""
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_db, get_current_active_user
from ...models.user import User
from ...schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioValue
from ...schemas.asset import Asset, AssetCreate, AssetUpdate
from ...models.asset import Asset as AssetModel
from ...crud import portfolio as crud_portfolio

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

@router.post("/", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
def create_new_portfolio(
    portfolio_in: PortfolioCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Portfolio:
    """Create a new portfolio for the current user."""
    return crud_portfolio.create_portfolio(db, portfolio=portfolio_in, user_id=current_user.id)

@router.get("/", response_model=List[Portfolio])
def get_user_portfolios(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[Portfolio]:
    """Get all portfolios for the current user."""
    return crud_portfolio.get_portfolios_by_user(db, user_id=current_user.id)

@router.get("/{portfolio_id}", response_model=Portfolio)
def get_portfolio_details(
    portfolio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Portfolio:
    """Get details of a specific portfolio."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio

@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio_details(
    portfolio_id: int,
    portfolio_in: PortfolioUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Portfolio:
    """Update a portfolio's details."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud_portfolio.update_portfolio(db, portfolio_id, portfolio_in)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_by_id(
    portfolio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Delete a portfolio."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    crud_portfolio.delete_portfolio(db, portfolio_id)

@router.get("/{portfolio_id}/value", response_model=PortfolioValue)
def get_portfolio_value(
    portfolio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> PortfolioValue:
    """Calculate and return the current value of a portfolio."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    
    calculated_values = crud_portfolio.calculate_portfolio_value(db, portfolio_id)
    return PortfolioValue(**calculated_values)

# --- Asset Endpoints --- #

@router.post("/{portfolio_id}/assets", response_model=Asset, status_code=status.HTTP_201_CREATED)
def add_new_asset_to_portfolio(
    portfolio_id: int,
    asset_in: AssetCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Asset:
    """Add a new asset to a specific portfolio."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud_portfolio.add_asset_to_portfolio(db, asset=asset_in, portfolio_id=portfolio_id)

@router.get("/{portfolio_id}/assets", response_model=List[Asset])
def get_portfolio_assets(
    portfolio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[Asset]:
    """Get all assets for a specific portfolio."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud_portfolio.get_assets_by_portfolio(db, portfolio_id=portfolio_id)

@router.put("/{portfolio_id}/assets/{asset_id}", response_model=Asset)
def update_asset_details(
    portfolio_id: int,
    asset_id: int,
    asset_in: AssetUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Asset:
    """Update an asset's details."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    asset = (
        db.query(AssetModel)
        .filter(AssetModel.id == asset_id, AssetModel.portfolio_id == portfolio_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found in portfolio")
    return crud_portfolio.update_asset(db, asset_id, asset_in)

@router.delete("/{portfolio_id}/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_asset_from_portfolio(
    portfolio_id: int,
    asset_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Remove an asset from a portfolio."""
    portfolio = crud_portfolio.get_portfolio_by_id(db, portfolio_id)
    if not portfolio or portfolio.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    asset = (
        db.query(AssetModel)
        .filter(AssetModel.id == asset_id, AssetModel.portfolio_id == portfolio_id)
        .first()
    )
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found in portfolio")
    crud_portfolio.remove_asset(db, asset_id)
