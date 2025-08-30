from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from app.models.announcement import AnnouncementStatus

class AnnouncementBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=512)
    detail_info: Optional[str] = None
    cover_url: Optional[str] = Field(None, max_length=512)

class AnnouncementCreate(AnnouncementBase):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

class AnnouncementUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=512)
    detail_info: Optional[str] = None
    cover_url: Optional[str] = Field(None, max_length=512)

class AnnouncementInDB(AnnouncementBase):
    id: int
    uuid: str
    publisher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnnouncementStatusUpdate(BaseModel):
    status: AnnouncementStatus

class AnnouncementResponse(BaseModel):
    uuid: str
    name: str
    summary: Optional[str]
    detail_info: Optional[str]
    cover_url: Optional[str]
    publisher_id: int
    status: AnnouncementStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedAnnouncementResponse(BaseModel):
    total: int
    items: list[AnnouncementResponse]