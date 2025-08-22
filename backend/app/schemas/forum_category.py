from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ForumCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[int] = Field(0, ge=0)
    is_active: Optional[bool] = True


class ForumCategoryCreate(ForumCategoryBase):
    pass


class ForumCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ForumCategoryInDB(ForumCategoryBase):
    id: int
    uuid: str
    post_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumCategoryResponse(BaseModel):
    id: int
    uuid: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    sort_order: int
    is_active: bool
    post_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedForumCategoryResponse(BaseModel):
    total: int
    items: List[ForumCategoryResponse]