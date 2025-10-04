from pydantic import BaseModel

# --- User Schemas ---

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    username: str  # In our case, email is the username
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
