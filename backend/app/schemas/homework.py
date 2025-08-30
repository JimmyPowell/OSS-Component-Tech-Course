from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
import uuid

class HomeworkStatus(str, Enum):
    draft = "draft"
    published = "published"

class HomeworkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    cover_url: Optional[str] = None
    resource_urls: Optional[List[str]] = None
    lasting_time: Optional[int] = None
    status: HomeworkStatus = Field(default=HomeworkStatus.draft)

class HomeworkCreate(HomeworkBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

class HomeworkUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    cover_url: Optional[str] = None
    resource_urls: Optional[List[str]] = None
    lasting_time: Optional[int] = None
    status: Optional[HomeworkStatus] = None

class HomeworkInDB(HomeworkBase):
    id: int
    uuid: str
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HomeworkResponse(BaseModel):
    uuid: str
    name: str
    description: Optional[str]
    content: Optional[str]
    cover_url: Optional[str]
    resource_urls: Optional[List[Any]]
    lasting_time: Optional[int]
    status: HomeworkStatus
    creator_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HomeworkDetailResponse(BaseModel):
    uuid: str
    name: str
    description: Optional[str]
    content: Optional[str]
    cover_url: Optional[str]
    resource_urls: Optional[List[Any]]
    lasting_time: Optional[int]
    status: HomeworkStatus
    creator_id: int
    publisher_name: Optional[str] = None
    publisher_avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedHomeworkResponse(BaseModel):
    total: int
    items: List[HomeworkResponse]

class HomeworkStatusUpdate(BaseModel):
    status: HomeworkStatus
