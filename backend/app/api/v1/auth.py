from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ...core.deps import get_db
from ...core.security import create_access_token
from ...crud.user import authenticate_user, create_user, get_user_by_email
from ...models.user import User as UserModel
from ...schemas.auth import Token, User, UserCreate
from ...utils.rate_limit import check_api_rate_limit, check_login_rate_limit
from ...utils.validation import validate_email_format, validate_name, validate_password_strength
from ..deps import get_current_active_user

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(
    request: Request,
    user_in: UserCreate,
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """Register a new user account with validation and rate limiting."""
    check_api_rate_limit(request)

    validated_email = validate_email_format(user_in.email)
    validate_password_strength(user_in.password)

    if user_in.full_name:
        user_in.full_name = validate_name(user_in.full_name, "Full name")

    existing_user = get_user_by_email(db, email=validated_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_in.email = validated_email
    new_user = create_user(db=db, user=user_in)
    return User.model_validate(new_user)


@router.post("/login", response_model=Token, summary="User login")
def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
) -> Token:
    """Authenticate user credentials, enforce rate limits, and return a JWT token."""
    check_login_rate_limit(request, form_data.username)

    try:
        validated_email = validate_email_format(form_data.username)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = authenticate_user(db, email=validated_email, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires,
    )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=Token, summary="Refresh access token")
def refresh_token(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
) -> Token:
    """Create a new access token for an authenticated user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.email,
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_200_OK, summary="User logout")
def logout(
    request: Request,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
) -> dict:
    """Acknowledge logout and optionally rate limit the endpoint."""
    check_api_rate_limit(request)

    return {
        "message": f"User {current_user.email} successfully logged out.",
        "detail": "Please remove the access token from the client. Token blacklisting not yet implemented.",
    }
