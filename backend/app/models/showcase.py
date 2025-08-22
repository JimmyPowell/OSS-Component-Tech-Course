from sqlalchemy import Column, String, TIMESTAMP, TEXT, JSON, Enum, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class Showcase(Base):
    __tablename__ = "showcases"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    summary = Column(String(512), nullable=True)
    detailed_introduction = Column(LONGTEXT, nullable=True)
    avatar_url = Column(String(512), nullable=True)
    project_url = Column(String(512), nullable=True)
    author_id = Column(INTEGER(unsigned=True), ForeignKey('users.id'), nullable=False, index=True)
    tags = Column(JSON, nullable=True)
    status = Column(Enum('draft', 'pending_review', 'published', 'rejected', 'archived'), nullable=False, server_default='draft')
    views_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    likes_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    reviewer_id = Column(INTEGER(unsigned=True), nullable=True, index=True)
    review_comment = Column(TEXT, nullable=True)
    reviewed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)

    # Relationships
    author = relationship("User", back_populates="showcases")
    comments = relationship("ShowcaseComment", back_populates="showcase")
    likes = relationship("ShowcaseLike", back_populates="showcase")
