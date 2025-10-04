from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ...core.deps import get_db, get_current_active_user
from ...models.user import User
from ...schemas.user import UserResponse, UserUpdate, UserProfile
from ...crud.user import get_user_by_id, update_user, delete_user
from ...utils.rate_limit import check_api_rate_limit
from ...utils.validation import validate_json_payload, validate_email_format, validate_name

router = APIRouter(tags=["users"])

@router.get("/me", response_model=UserProfile, summary="Get current user profile")
def get_current_user_profile(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
) -> UserProfile:
    """
    Get the current authenticated user's profile.
    
    Returns:
        UserProfile: Current user's profile information
    """
    # Apply rate limiting
    check_api_rate_limit(request, f"user:{current_user.id}")
    
    return UserProfile.model_validate(current_user)

@router.put("/me", response_model=UserResponse, summary="Update current user profile")
def update_current_user_profile(
    request: Request,
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """
    Update the current authenticated user's profile.
    
    Args:
        user_update: Updated user information
        
    Returns:
        UserResponse: Updated user profile
        
    Raises:
        HTTPException: If user not found or update fails
    """
    # Apply rate limiting
    check_api_rate_limit(request, f"user:{current_user.id}")
    
    # Validate input data
    update_data = validate_json_payload(user_update.model_dump(exclude_unset=True))
    if "email" in update_data:
        update_data["email"] = validate_email_format(update_data["email"])
    if "full_name" in update_data and update_data["full_name"] is not None:
        update_data["full_name"] = validate_name(update_data["full_name"], "Full name")
    
    # Create new UserUpdate object with validated data
    validated_update = UserUpdate(**update_data)
    
    # Update user in database
    updated_user = update_user(db, current_user.id, validated_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(updated_user)

@router.delete("/me", summary="Delete current user account")
def delete_current_user_account(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """
    Delete (deactivate) the current authenticated user's account.
    This performs a soft delete by setting is_active to False.
    
    Returns:
        dict: Confirmation message
        
    Raises:
        HTTPException: If deletion fails
    """
    # Apply rate limiting
    check_api_rate_limit(request, f"user:{current_user.id}")
    
    # Perform soft delete
    if not delete_user(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )
    
    return {
        "message": "User account has been successfully deleted",
        "detail": "Your account has been deactivated. Contact support if you need to recover it."
    }

@router.get("/me/status", summary="Check user account status")
def get_user_status(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
) -> dict:
    """
    Get current user's account status and activity information.
    
    Returns:
        dict: User status information
    """
    # Apply rate limiting
    check_api_rate_limit(request, f"user:{current_user.id}")
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login_at": current_user.last_login_at,
        "total_portfolios": len(current_user.portfolios) if current_user.portfolios else 0
    }
