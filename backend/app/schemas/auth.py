from pydantic import BaseModel, EmailStr, field_validator, Field
import re

# --- User Schemas ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str | None = Field(None, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        
        return v

class UserLogin(BaseModel):
    username: EmailStr # In our case, email is the username
    password: str

class User(UserBase):
    id: int
    is_active: bool
    full_name: str | None = None

    class Config:
        from_attributes = True  # Updated for Pydantic V2

# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None