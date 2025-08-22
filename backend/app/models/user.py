from sqlalchemy import Column, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    real_name = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    school = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), nullable=False, default='user')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    showcase_comments = relationship("ShowcaseComment", back_populates="user")
    showcase_comment_replies = relationship("ShowcaseCommentReply", foreign_keys="ShowcaseCommentReply.user_id")
    qiniu_tokens = relationship("QiniuToken", foreign_keys="QiniuToken.user_id", back_populates="user")
    
    # Likes relationships
    showcase_likes = relationship("ShowcaseLike", back_populates="user")
    showcase_comment_likes = relationship("ShowcaseCommentLike", back_populates="user")
    showcase_comment_reply_likes = relationship("ShowcaseCommentReplyLike", back_populates="user")
    
    # Notification relationships
    notifications_received = relationship("Notification", foreign_keys="Notification.recipient_id", back_populates="recipient")
    notifications_sent = relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender")
