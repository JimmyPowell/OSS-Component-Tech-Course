from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for requesting verification code
class EmailRequest(BaseModel):
    email: EmailStr

# Schema for verifying code
class CodeVerify(BaseModel):
    email: EmailStr
    code: str

# Schema for user registration
class UserCreate(BaseModel):
    session: str
    username: str
    password: str
    real_name: str
    phone_number: str
    school: str
    avatar_url: Optional[str] = None

# Schema for user login
class UserLogin(BaseModel):
    identifier: str  # Can be username or email
    password: str

# Base schema for user response
class UserBase(BaseModel):
    uuid: str
    username: str
    email: EmailStr
    role: str
    is_active: bool
    real_name: Optional[str] = None
    phone_number: Optional[str] = None
    school: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

# Schema for user response
class UserResponse(UserBase):
    pass
