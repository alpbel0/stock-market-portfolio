"""
API endpoints for managing portfolios, assets, and transactions.
"""
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_db, get_current_active_user
from ...models.user import User
from ...schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioSummary
from ...schemas.asset import Asset
from ...schemas.transaction import Transaction, TransactionCreate
from ...crud import portfolio as crud_portfolio

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# --- Portfolio Endpoints --- #

@router.post("/", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
def create_new_portfolio(
    portfolio_in: PortfolioCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Portfolio:
    """Create a new portfolio for the current user."""
    return crud_portfolio.create_portfolio(db, portfolio_in=portfolio_in, user_id=current_user.id)

@router.get("/", response_model=List[Portfolio])
def get_user_portfolios(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[Portfolio]:
    """Get all portfolios for the current user."""
    return crud_portfolio.get_portfolios_by_user(db, user_id=current_user.id)

@router.get("/{portfolio_id}/summary", response_model=PortfolioSummary)
def get_portfolio_summary(
    portfolio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> PortfolioSummary:
    """Get a comprehensive summary of a portfolio, including calculated values and assets."""
    portfolio = crud_portfolio.get_portfolio_summary(db, portfolio_id=portfolio_id)
    if not portfolio or portfolio.owner.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return PortfolioSummary.model_validate(portfolio)

@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio_details(
    portfolio_id: int,
    portfolio_in: PortfolioUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Portfolio:
    """Update a portfolio's name or description."""
    portfolio = crud_portfolio.get_portfolio_summary(db, portfolio_id=portfolio_id)
    if not portfolio or portfolio.owner.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud_portfolio.update_portfolio(db, portfolio_id=portfolio_id, portfolio_update=portfolio_in)

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_by_id(
    portfolio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Delete a portfolio and all its associated data."""
    portfolio = crud_portfolio.get_portfolio_summary(db, portfolio_id=portfolio_id)
    if not portfolio or portfolio.owner.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    crud_portfolio.delete_portfolio(db, portfolio_id=portfolio_id)

# --- Transaction Endpoints --- #

@router.post("/{portfolio_id}/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def add_new_transaction(
    portfolio_id: int,
    transaction_in: TransactionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Transaction:
    """Add a new transaction to a portfolio. The asset will be created if it doesn't exist."""
    portfolio = crud_portfolio.get_portfolio_summary(db, portfolio_id=portfolio_id)
    if not portfolio or portfolio.owner.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud_portfolio.add_transaction(db, portfolio_id=portfolio_id, transaction_in=transaction_in)

@router.get("/{portfolio_id}/transactions", response_model=List[Transaction])
def get_portfolio_transactions(
    portfolio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[Transaction]:
    """Get all transactions for a specific portfolio."""
    portfolio = crud_portfolio.get_portfolio_summary(db, portfolio_id=portfolio_id)
    if not portfolio or portfolio.owner.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return crud_portfolio.get_transactions_by_portfolio(db, portfolio_id=portfolio_id)
