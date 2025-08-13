from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import uuid

class ShowcaseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=512)
    detailed_introduction: Optional[str] = None
    avatar_url: Optional[str] = None
    project_url: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = 'draft'

class ShowcaseCreate(ShowcaseBase):
    pass

class ShowcaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=512)
    detailed_introduction: Optional[str] = None
    avatar_url: Optional[str] = None
    project_url: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class ShowcaseInDB(ShowcaseBase):
    id: int
    uuid: str
    author_id: int
    views_count: int
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShowcaseResponse(BaseModel):
    uuid: str
    name: str
    summary: Optional[str]
    detailed_introduction: Optional[str]
    avatar_url: Optional[str]
    project_url: Optional[str]
    author_id: int
    tags: Optional[List[Any]]
    status: str
    views_count: int
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedShowcaseResponse(BaseModel):
    total: int
    items: List[ShowcaseResponse]
