from pydantic import BaseModel
from datetime import datetime


# Showcase likes
class ShowcaseLikeBase(BaseModel):
    pass


class ShowcaseLikeCreate(ShowcaseLikeBase):
    showcase_uuid: str


class ShowcaseLikeResponse(BaseModel):
    uuid: str
    showcase_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Comment likes
class ShowcaseCommentLikeBase(BaseModel):
    pass


class ShowcaseCommentLikeCreate(ShowcaseCommentLikeBase):
    comment_uuid: str


class ShowcaseCommentLikeResponse(BaseModel):
    uuid: str
    comment_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Reply likes
class ShowcaseCommentReplyLikeBase(BaseModel):
    pass


class ShowcaseCommentReplyLikeCreate(ShowcaseCommentReplyLikeBase):
    reply_uuid: str


class ShowcaseCommentReplyLikeResponse(BaseModel):
    uuid: str
    reply_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True