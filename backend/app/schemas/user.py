from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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

# Schema for admin creating user directly
class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    real_name: str
    phone_number: str
    school: Optional[str] = None
    role: Optional[str] = "user"
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
    id: int
    created_at: datetime
    updated_at: datetime

# Simplified user response for embedding in other schemas
class UserSimpleResponse(BaseModel):
    username: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

# Schema for admin user management
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    real_name: Optional[str] = None
    phone_number: Optional[str] = None
    school: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for user search/filter
class UserSearchRequest(BaseModel):
    search: Optional[str] = None  # Search by username, email, or uuid
    role: Optional[str] = None
    is_active: Optional[bool] = None
    school: Optional[str] = None

# Paginated user response
class PaginatedUserResponse(BaseModel):
    total: int
    items: List[UserResponse]
