from sqlalchemy import Column, String, TIMESTAMP, TEXT, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class ShowcaseComment(Base):
    __tablename__ = "showcase_comments"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    showcase_id = Column(INTEGER(unsigned=True), ForeignKey("showcases.id"), nullable=False, index=True)
    user_id = Column(INTEGER(unsigned=True), ForeignKey("users.id"), nullable=False, index=True)
    content = Column(TEXT, nullable=False)
    likes_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)

    user = relationship("User", back_populates="showcase_comments")
    showcase = relationship("Showcase", back_populates="comments")
    replies = relationship("ShowcaseCommentReply", back_populates="comment")
    likes = relationship("ShowcaseCommentLike", back_populates="comment")
