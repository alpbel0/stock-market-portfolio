from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.deps import get_db
from ...core.security import create_access_token, verify_password
from ...core.config import get_settings
from ...schemas.auth import Token, UserCreate, User
from ...crud.user import create_user, authenticate_user, get_user_by_email
from ...utils.rate_limit import check_login_rate_limit, check_api_rate_limit
from ...utils.validation import validate_email_format, validate_password_strength, validate_name

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()

@router.post("/register", response_model=User, summary="Register a new user")
def register(
    request: Request,
    user_create: UserCreate,
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Register a new user account.
    
    Args:
        user_create: User registration data
        
    Returns:
        User: Created user information
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    # Apply rate limiting
    check_api_rate_limit(request)
    
    # Validate email format
    validated_email = validate_email_format(user_create.email)
    
    # Validate password strength
    validate_password_strength(user_create.password)
    
    # Validate name if provided
    if user_create.full_name:
        validated_name = validate_name(user_create.full_name, "Full name")
        user_create.full_name = validated_name
    
    # Check if user already exists
    existing_user = get_user_by_email(db, email=validated_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Update user_create with validated email
    user_create.email = validated_email
    
    # Create new user
    new_user = create_user(db=db, user=user_create)
    return User.model_validate(new_user)

@router.post("/login", response_model=Token, summary="User login")
def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
) -> Token:
    """
    Authenticate user and return access token.
    
    Args:
        form_data: OAuth2 password form with username (email) and password
        
    Returns:
        Token: JWT access token and token type
        
    Raises:
        HTTPException: If authentication fails or rate limit exceeded
    """
    # Apply login rate limiting
    check_login_rate_limit(request, form_data.username)
    
    # Validate email format
    try:
        validated_email = validate_email_format(form_data.username)
    except HTTPException:
        # Don't reveal email validation error during login for security
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Authenticate user
    user = authenticate_user(db, email=validated_email, password=form_data.password)
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
            detail="User account is deactivated"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/logout", summary="User logout")
def logout(
    request: Request
) -> dict:
    """
    Logout endpoint (client-side token invalidation).
    
    Note: Since we're using JWTs, actual token invalidation should be 
    handled on the client side by removing the token from storage.
    For enhanced security, consider implementing a token blacklist.
    
    Returns:
        dict: Logout confirmation message
    """
    # Apply rate limiting
    check_api_rate_limit(request)
    
    return {
        "message": "Successfully logged out",
        "detail": "Please remove the access token from your client storage"
    }