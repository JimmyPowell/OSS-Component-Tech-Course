from sqlalchemy import Column, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class ForumReply(Base):
    __tablename__ = "forum_replies"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    post_id = Column(INTEGER(unsigned=True), ForeignKey('forum_posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(INTEGER(unsigned=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    parent_id = Column(INTEGER(unsigned=True), ForeignKey('forum_replies.id', ondelete='CASCADE'), nullable=True, index=True)
    content = Column(LONGTEXT, nullable=False)
    reply_to_user_id = Column(INTEGER(unsigned=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    is_deleted = Column(Boolean, nullable=False, server_default='0', index=True)
    floor_number = Column(INTEGER(unsigned=True), nullable=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)

    # Relationships
    post = relationship("ForumPost", backref="replies")
    author = relationship("User", foreign_keys=[user_id], backref="forum_replies")
    parent_reply = relationship("ForumReply", remote_side=[id], backref="child_replies")
    reply_to_user = relationship("User", foreign_keys=[reply_to_user_id])