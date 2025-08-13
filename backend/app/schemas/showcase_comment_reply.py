from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from app.schemas.user import UserSimpleResponse

class ShowcaseCommentReplyBase(BaseModel):
    content: str = Field(..., min_length=1)

class ShowcaseCommentReplyCreate(ShowcaseCommentReplyBase):
    comment_uuid: str
    reply_to_user_id: Optional[int] = None

class ShowcaseCommentReplyUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class ShowcaseCommentReplyInDB(ShowcaseCommentReplyBase):
    id: int
    uuid: str
    comment_id: int
    user_id: int
    reply_to_user_id: Optional[int]
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShowcaseCommentReplyResponse(BaseModel):
    uuid: str
    comment_id: int
    user: UserSimpleResponse
    reply_to_user_id: Optional[int]
    content: str
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedShowcaseCommentReplyResponse(BaseModel):
    total: int
    items: List[ShowcaseCommentReplyResponse]
