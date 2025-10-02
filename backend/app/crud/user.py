from sqlalchemy.orm import Session

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
    return user

def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
    """
    Updates a user's information in the database.
    Only updates fields that are provided (not None).
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    # If password is being updated, hash it
    if 'password' in update_data and update_data['password'] is not None:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    # Update user fields
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User) -> None:
    """
    Deletes a user from the database.
    This is a soft delete that sets is_active to False.
    """
    user.is_active = False
    db.commit()

def hard_delete_user(db: Session, user: User) -> None:
    """
    Permanently deletes a user from the database.
    Warning: This action cannot be undone!
    """
    db.delete(user)
    db.commit()
