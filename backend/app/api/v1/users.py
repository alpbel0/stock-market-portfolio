from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...crud.user import update_user, delete_user, get_user_by_email
from ...models.user import User
from ...schemas.user import UserResponse, UserUpdate, UserDelete
from ..deps import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile.
    
    Returns the authenticated user's profile information including:
    - User ID
    - Email
    - Full name
    - Account active status
    
    Requires authentication via JWT token.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    
    Allows updating:
    - Email address (must be unique)
    - Full name
    - Password (will be validated for strength)
    
    All fields are optional - only provided fields will be updated.
    
    Password requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Requires authentication via JWT token.
    """
    # If email is being updated, check if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user
    updated_user = update_user(db=db, user=current_user, user_update=user_update)
    return updated_user


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_current_user_account(
    user_delete: UserDelete,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account (soft delete).
    
    This is a soft delete operation that deactivates the account
    rather than permanently removing it from the database.
    
    The user will no longer be able to log in, but their data
    is preserved for potential account recovery.
    
    Requires:
    - Authentication via JWT token
    - Confirmation field set to true in request body
    
    Example request body:
    ```json
    {
        "confirm": true
    }
    ```
    """
    # Soft delete the user
    delete_user(db=db, user=current_user)
    
    return {
        "message": f"User account {current_user.email} has been deactivated.",
        "detail": "Your account has been deactivated. Contact support if you wish to reactivate it."
    }