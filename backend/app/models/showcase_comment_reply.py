from sqlalchemy import Column, String, TIMESTAMP, TEXT, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class ShowcaseCommentReply(Base):
    __tablename__ = "showcase_comment_replies"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    comment_id = Column(INTEGER(unsigned=True), ForeignKey("showcase_comments.id"), nullable=False, index=True)
    user_id = Column(INTEGER(unsigned=True), ForeignKey("users.id"), nullable=False, index=True)
    reply_to_user_id = Column(INTEGER(unsigned=True), ForeignKey("users.id"), nullable=True, index=True)
    content = Column(TEXT, nullable=False)
    likes_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)

    user = relationship("User", foreign_keys=[user_id])
    reply_to_user = relationship("User", foreign_keys=[reply_to_user_id])
    comment = relationship("ShowcaseComment", back_populates="replies")
    likes = relationship("ShowcaseCommentReplyLike", back_populates="reply")
