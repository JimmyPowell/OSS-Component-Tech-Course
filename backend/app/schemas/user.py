from pydantic import BaseModel, EmailStr, validator
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
    student_id: Optional[str] = None
    student_class: Optional[str] = None

# Schema for user login
class UserLogin(BaseModel):
    identifier: str  # Can be username or email
    password: str

# Base schema for user response
class UserBase(BaseModel):
    uuid: str
    username: str
    email: str  # 改为普通字符串，避免严格的EmailStr验证
    role: str
    is_active: bool
    real_name: Optional[str] = None
    phone_number: Optional[str] = None
    school: Optional[str] = None
    avatar_url: Optional[str] = None
    student_id: Optional[str] = None
    student_class: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        # 对于临时邮箱，允许 .local 域名
        if v.endswith('@temp.local') or v.endswith('@example.com'):
            return v
        # 对于其他邮箱，进行基本格式检查
        if '@' in v and '.' in v.split('@')[-1]:
            return v
        raise ValueError('Invalid email format')

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
    real_name: Optional[str] = None
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
    student_id: Optional[str] = None
    student_class: Optional[str] = None

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

# Batch import related schemas
class BatchImportUserData(BaseModel):
    student_id: str
    real_name: str
    student_class: str

class BatchImportRequest(BaseModel):
    users: List[BatchImportUserData]
    conflict_resolution: str = "cancel"  # cancel, overwrite, modify

class ConflictUser(BaseModel):
    row_index: int
    student_id: str
    real_name: str
    student_class: str
    conflict_type: str  # student_id, real_name, username
    existing_user: Optional[UserSimpleResponse] = None

class BatchImportPreviewResponse(BaseModel):
    total_users: int
    valid_users: List[BatchImportUserData]
    conflicts: List[ConflictUser]
    errors: List[str]

class BatchImportResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[str]
    created_users: List[UserResponse]
