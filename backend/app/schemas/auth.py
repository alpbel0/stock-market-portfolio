from pydantic import BaseModel, EmailStr

# --- User Schemas ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    username: EmailStr # In our case, email is the username
    password: str

class User(UserBase):
    id: int
    is_active: bool
    full_name: str | None = None

    class Config:
        orm_mode = True # Deprecated, use from_attributes=True in Pydantic V2

# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None