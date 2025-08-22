from sqlalchemy import Column, String, TIMESTAMP, TEXT, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum

from app.config.database import Base


class NotificationType(str, Enum):
    like_showcase = "like_showcase"
    like_comment = "like_comment"
    comment_showcase = "comment_showcase"
    reply_comment = "reply_comment"
    showcase_approved = "showcase_approved"
    showcase_rejected = "showcase_rejected"
    system_announcement = "system_announcement"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    recipient_id = Column(INTEGER(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="通知接收者")
    sender_id = Column(INTEGER(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="通知发起人")
    admin_id = Column(INTEGER(unsigned=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="管理员（如果是系统通知）")
    type = Column(String(50), nullable=False, index=True, comment="通知类型")
    title = Column(String(255), nullable=False, comment="通知标题")
    content = Column(TEXT, nullable=True, comment="通知内容")
    related_id = Column(INTEGER(unsigned=True), nullable=True, comment="相关对象ID（如作品ID、评论ID等）")
    related_uuid = Column(String(36), nullable=True, comment="相关对象UUID")
    is_read = Column(Boolean, nullable=False, server_default='0', index=True, comment="是否已读")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    read_at = Column(TIMESTAMP, nullable=True, comment="阅读时间")

    # 关系
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="notifications_received")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="notifications_sent")
    admin = relationship("User", foreign_keys=[admin_id])