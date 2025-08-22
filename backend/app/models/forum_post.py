from sqlalchemy import Column, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    category_id = Column(INTEGER(unsigned=True), ForeignKey('forum_categories.id', ondelete='RESTRICT'), nullable=False, index=True)
    user_id = Column(INTEGER(unsigned=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(LONGTEXT, nullable=False)
    is_pinned = Column(Boolean, nullable=False, server_default='0', index=True)
    is_locked = Column(Boolean, nullable=False, server_default='0', index=True)
    is_deleted = Column(Boolean, nullable=False, server_default='0', index=True)
    view_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    reply_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    last_reply_at = Column(TIMESTAMP, nullable=True, index=True)
    last_reply_user_id = Column(INTEGER(unsigned=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)

    # Relationships
    category = relationship("ForumCategory", backref="posts")
    author = relationship("User", foreign_keys=[user_id], backref="forum_posts")
    last_reply_user = relationship("User", foreign_keys=[last_reply_user_id])