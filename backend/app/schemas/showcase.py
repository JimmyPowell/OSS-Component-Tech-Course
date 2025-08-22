from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
import uuid

class ShowcaseStatus(str, Enum):
    draft = "draft"
    pending_review = "pending_review"
    published = "published"
    rejected = "rejected"
    archived = "archived"

class ShowcaseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=512)
    detailed_introduction: Optional[str] = None
    avatar_url: Optional[str] = None
    project_url: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ShowcaseStatus] = ShowcaseStatus.draft

class ShowcaseCreate(ShowcaseBase):
    pass

class ShowcaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=512)
    detailed_introduction: Optional[str] = None
    avatar_url: Optional[str] = None
    project_url: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ShowcaseStatus] = None

class ShowcaseInDB(ShowcaseBase):
    id: int
    uuid: str
    author_id: int
    reviewer_id: Optional[int] = None
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
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
    reviewer_id: Optional[int] = None
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    views_count: int
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShowcaseReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    review_comment: Optional[str] = None

    def model_validate(self, v):
        if self.action == "reject" and (not self.review_comment or not self.review_comment.strip()):
            raise ValueError("Review comment is required when rejecting a showcase")
        return self

class PaginatedShowcaseResponse(BaseModel):
    total: int
    items: List[ShowcaseResponse]
