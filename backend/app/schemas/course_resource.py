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
    summary: Optional[str] = Field(None, max_length=50, description="简短摘要，50字以内")
    description: Optional[str] = None
    cover_url: Optional[str] = None
    resource_url: str
    is_repost: bool = Field(default=False, description="是否转载")
    source_platform: Optional[str] = Field(default=None, max_length=50, description="转载来源平台")
    sort_order: Optional[int] = Field(default=None, description="排序值：越小越靠前，未设置(Null)排在最后")
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: CourseResourceStatus = Field(default=CourseResourceStatus.draft, description="资源状态")

class CourseResourceCreate(CourseResourceBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

class CourseResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=50, description="简短摘要，50字以内")
    description: Optional[str] = None
    cover_url: Optional[str] = None
    resource_url: Optional[str] = None
    # 更新时可选字段：与创建保持一致
    is_repost: Optional[bool] = Field(default=None, description="是否转载（仅视频有效）")
    source_platform: Optional[str] = Field(default=None, max_length=50, description="转载来源平台（仅视频有效）")
    sort_order: Optional[int] = Field(default=None, description="排序值：越小越靠前，未设置(Null)排在最后")
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
    summary: Optional[str]
    description: Optional[str]
    cover_url: Optional[str]
    resource_url: str
    is_repost: bool
    source_platform: Optional[str]
    sort_order: Optional[int]
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
    summary: Optional[str]
    description: Optional[str]
    cover_url: Optional[str]
    resource_url: str
    is_repost: bool
    source_platform: Optional[str]
    sort_order: Optional[int]
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
