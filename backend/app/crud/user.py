from sqlalchemy.orm import Session

from ..core.security import get_password_hash, verify_password
from ..models.user import User
from ..schemas.auth import UserCreate

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