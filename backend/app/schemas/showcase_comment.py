from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

from app.schemas.user import UserSimpleResponse

class ShowcaseCommentBase(BaseModel):
    content: str = Field(..., min_length=1)

class ShowcaseCommentCreate(ShowcaseCommentBase):
    showcase_uuid: str

class ShowcaseCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class ShowcaseCommentInDB(ShowcaseCommentBase):
    id: int
    uuid: str
    showcase_id: int
    user_id: int
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShowcaseCommentResponse(BaseModel):
    uuid: str
    showcase_id: int
    user: UserSimpleResponse
    content: str
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedShowcaseCommentResponse(BaseModel):
    total: int
    items: List[ShowcaseCommentResponse]
