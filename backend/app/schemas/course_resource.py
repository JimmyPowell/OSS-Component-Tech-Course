from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class CourseResourceStatus(str, Enum):
    draft = "draft"
    published = "published"


class CourseResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    resource_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: CourseResourceStatus = Field(default=CourseResourceStatus.draft, description="资源状态")

class CourseResourceCreate(CourseResourceBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

class CourseResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    resource_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: Optional[CourseResourceStatus] = None

class CourseResourceInDB(CourseResourceBase):
    id: int
    uuid: str
    creator_id: int
    created_at: datetime
    updated_at: datetime
    download_count: int

    class Config:
        from_attributes = True

class CourseResourceResponse(BaseModel):
    uuid: str
    name: str
    type: str
    description: Optional[str]
    cover_url: Optional[str]
    resource_url: str
    file_size: Optional[int]
    mime_type: Optional[str]
    status: CourseResourceStatus
    download_count: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedCourseResourceResponse(BaseModel):
    total: int
    items: List[CourseResourceResponse]

class CourseResourceDetailResponse(BaseModel):
    uuid: str
    name: str
    type: str
    description: Optional[str]
    cover_url: Optional[str]
    resource_url: str
    file_size: Optional[int]
    mime_type: Optional[str]
    status: CourseResourceStatus
    download_count: int
    created_at: datetime
    updated_at: datetime
    # 用户信息
    publisher_id: int
    publisher_name: str
    publisher_avatar: Optional[str]

    class Config:
        from_attributes = True


class CourseResourceStatusUpdate(BaseModel):
    status: CourseResourceStatus = Field(..., description="要更新的状态")
