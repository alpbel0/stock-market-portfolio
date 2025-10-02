from pydantic import BaseModel, EmailStr, field_validator, Field
import re


class UserBase(BaseModel):
    """Base user schema with email."""
    email: EmailStr


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    All fields are optional to allow partial updates.
    """
    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=1, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        """
        Validate password strength:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if v is None:
            return v
            
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


class UserResponse(UserBase):
    """
    Schema for user response.
    Excludes sensitive information like password.
    """
    id: int
    full_name: str | None = None
    is_active: bool
    
    class Config:
        from_attributes = True


class UserDelete(BaseModel):
    """
    Schema for user deletion confirmation.
    """
    confirm: bool = Field(..., description="Must be true to confirm deletion")
    
    @field_validator('confirm')
    @classmethod
    def validate_confirmation(cls, v: bool) -> bool:
        if not v:
            raise ValueError('You must confirm deletion by setting confirm=true')
        return v