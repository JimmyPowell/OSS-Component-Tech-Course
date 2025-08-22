from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from app.schemas.user import UserSimpleResponse


class ForumReplyBase(BaseModel):
    content: str = Field(..., min_length=1)
    post_id: Optional[int] = None
    parent_id: Optional[int] = None
    reply_to_user_id: Optional[int] = None


class ForumReplyCreate(ForumReplyBase):
    post_id: int = Field(..., gt=0)


class ForumReplyUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)


class ForumReplyInDB(ForumReplyBase):
    id: int
    uuid: str
    user_id: int
    is_deleted: bool
    floor_number: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumReplyResponse(BaseModel):
    uuid: str
    content: str
    post_id: int
    user_id: int
    author: Optional[UserSimpleResponse] = None
    parent_id: Optional[int]
    reply_to_user_id: Optional[int]
    reply_to_user: Optional[UserSimpleResponse] = None
    is_deleted: bool
    floor_number: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumReplyWithChildren(ForumReplyResponse):
    """带子回复的回复对象"""
    children: List['ForumReplyWithChildren'] = []


class PaginatedForumReplyResponse(BaseModel):
    total: int
    items: List[ForumReplyResponse]


# 更新模型以支持递归引用
ForumReplyWithChildren.model_rebuild()