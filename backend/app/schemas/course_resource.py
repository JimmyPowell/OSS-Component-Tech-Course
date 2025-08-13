from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class CourseResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    resource_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

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
    download_count: int
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedCourseResourceResponse(BaseModel):
    total: int
    items: List[CourseResourceResponse]
