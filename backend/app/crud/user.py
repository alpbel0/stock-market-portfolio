from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..core.security import get_password_hash, verify_password
from ..models.user import User
from ..schemas.auth import UserCreate
from ..schemas.user import UserUpdate

def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieves a user by their email address.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Creates a new user in the database.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Authenticates a user by email and password.
    Returns the user object if authentication is successful, otherwise None.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login time
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    return user

def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieves a user by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User | None:
    """
    Updates a user's profile information.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Soft delete a user (set is_active to False).
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = False
    db.commit()
    return True

def is_user_active(db: Session, user_id: int) -> bool:
    """
    Check if a user is active.
    """
    user = get_user_by_id(db, user_id)
    return user is not None and user.is_active
