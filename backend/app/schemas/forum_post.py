from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ForumPostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category_id: Optional[int] = None


class ForumPostCreate(ForumPostBase):
    category_id: int = Field(..., gt=0)


class ForumPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = Field(None, gt=0)


class ForumPostInDB(ForumPostBase):
    id: int
    uuid: str
    user_id: int
    is_pinned: bool
    is_locked: bool
    is_deleted: bool
    view_count: int
    reply_count: int
    last_reply_at: Optional[datetime]
    last_reply_user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumPostResponse(BaseModel):
    uuid: str
    title: str
    content: str
    category_id: int
    user_id: int
    is_pinned: bool
    is_locked: bool
    is_deleted: bool
    view_count: int
    reply_count: int
    last_reply_at: Optional[datetime]
    last_reply_user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumPostListResponse(BaseModel):
    """用于列表显示的简化版本"""
    uuid: str
    title: str
    category_id: int
    user_id: int
    is_pinned: bool
    is_locked: bool
    view_count: int
    reply_count: int
    last_reply_at: Optional[datetime]
    last_reply_user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedForumPostResponse(BaseModel):
    total: int
    items: List[ForumPostListResponse]