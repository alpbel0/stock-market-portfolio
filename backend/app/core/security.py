from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import get_settings

# Password Hashing Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Creates a new JWT access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain password.
    """
    return pwd_context.hash(password)


def verify_token(token: str, credentials_exception) -> Any:
    """
    Verifies a JWT token and returns the subject (e.g., user ID or email).
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception