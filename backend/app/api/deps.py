from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import verify_token
from ..crud.user import get_user_by_email
from ..models.user import User

# OAuth2 scheme for token authentication
# tokenUrl points to the login endpoint where clients can obtain tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.
    
    This function:
    1. Extracts the token from the Authorization header
    2. Validates the token and extracts the user identifier (email)
    3. Retrieves the user from the database
    4. Returns the user object
    
    Args:
        token: JWT access token from the Authorization header
        db: Database session
    
    Returns:
        User object if authentication is successful
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token and get user email
    email = verify_token(token, credentials_exception)
    
    # Get user from database
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current authenticated and active user.
    
    This function builds upon get_current_user by adding an additional
    check to ensure the user account is active.
    
    Args:
        current_user: User object from get_current_user dependency
    
    Returns:
        User object if user is active
    
    Raises:
        HTTPException: If user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return current_user