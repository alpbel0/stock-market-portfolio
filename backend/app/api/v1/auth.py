from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ...core.database import get_db
from ...core.security import create_access_token
from ...crud.user import authenticate_user, create_user, get_user_by_email
from ...schemas.auth import Token, UserCreate, User
from ...models.user import User as UserModel
from ..deps import get_current_active_user

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: User's email address (used as username)
    - **password**: User's password (will be hashed)
    - **full_name**: User's full name (optional)
    
    Returns the created user object without password.
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = create_user(db=db, user=user_in)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get an access token.
    
    - **username**: User's email address
    - **password**: User's password
    
    Returns an access token for authenticated requests.
    """
    # Authenticate user
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )
    
    # Update last login timestamp
    from datetime import datetime, timezone
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Refresh the access token.
    
    This endpoint will create a new access token for the authenticated user.
    The current implementation uses the existing access token to generate a new one.
    
    In a production environment, you should:
    1. Use separate refresh tokens with longer expiration
    2. Store refresh tokens in database for revocation capability
    3. Implement refresh token rotation for enhanced security
    
    Returns a new access token.
    """
    # FastAPI will automatically inject current_user through the Depends mechanism
    # No need to manually call get_current_active_user()
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.email,
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Logout the current user.
    
    Since JWT tokens are stateless, logout is handled client-side by removing the token.
    This endpoint can be used for logging purposes or token blacklisting in future.
    
    The endpoint verifies that the user is authenticated before logging them out.
    
    Returns a success message.
    """
    # FastAPI will automatically inject current_user through the Depends mechanism
    # No need to manually call get_current_active_user()
    
    # In a stateless JWT setup, logout is primarily client-side
    # The client should delete/clear the access token
    # This endpoint can be used for:
    # 1. Logging the logout event (implemented below)
    # 2. Token blacklisting (if implemented in future with Redis/database)
    # 3. Clearing any server-side session data
    
    # Log the logout event (optional, for audit purposes)
    # In production, you might want to log this to a separate audit table
    
    return {
        "message": f"User {current_user.email} successfully logged out.",
        "detail": "Please remove the access token from the client. Token blacklisting not yet implemented."
    }
