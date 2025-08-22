from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class ShowcaseCommentReplyLike(Base):
    __tablename__ = "showcase_comment_reply_likes"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    reply_id = Column(INTEGER(unsigned=True), ForeignKey("showcase_comment_replies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(INTEGER(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # 确保每个用户对每个回复只能点赞一次
    __table_args__ = (
        UniqueConstraint('reply_id', 'user_id', name='unique_reply_like'),
    )

    # 关系
    user = relationship("User", back_populates="showcase_comment_reply_likes")
    reply = relationship("ShowcaseCommentReply", back_populates="likes")