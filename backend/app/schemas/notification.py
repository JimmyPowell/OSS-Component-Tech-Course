from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.schemas.user import UserSimpleResponse


class NotificationType(str, Enum):
    like_showcase = "like_showcase"
    like_comment = "like_comment"
    comment_showcase = "comment_showcase"
    reply_comment = "reply_comment"
    showcase_approved = "showcase_approved"
    showcase_rejected = "showcase_rejected"
    system_announcement = "system_announcement"


class NotificationBase(BaseModel):
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    related_id: Optional[int] = None
    related_uuid: Optional[str] = None


class NotificationCreate(NotificationBase):
    recipient_id: int
    sender_id: Optional[int] = None
    admin_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationInDB(NotificationBase):
    id: int
    uuid: str
    recipient_id: int
    sender_id: Optional[int] = None
    admin_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    uuid: str
    type: str
    title: str
    content: Optional[str]
    related_id: Optional[int]
    related_uuid: Optional[str]
    sender: Optional[UserSimpleResponse] = None
    admin: Optional[UserSimpleResponse] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedNotificationResponse(BaseModel):
    total: int
    unread_count: int
    items: List[NotificationResponse]


class NotificationMarkAllReadRequest(BaseModel):
    pass