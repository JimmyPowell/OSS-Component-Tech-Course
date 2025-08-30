from sqlalchemy import Column, String, TIMESTAMP, TEXT, INTEGER, Enum, Index
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.sql import func
import enum

from app.config.database import Base


class AnnouncementStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    summary = Column(String(512), nullable=True)
    detail_info = Column(LONGTEXT, nullable=True)
    cover_url = Column(String(512), nullable=True)
    publisher_id = Column(INTEGER(unsigned=True), nullable=False, index=True)
    status = Column(
        Enum(AnnouncementStatus),
        default=AnnouncementStatus.draft,
        nullable=False,
        comment="状态：草稿/已发布"
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)

    # 索引
    __table_args__ = (
        Index('idx_announcement_status', 'status'),
        Index('idx_announcement_publisher', 'publisher_id'),
        Index('idx_announcement_published', 'status', 'created_at'),
        {'comment': '公告表'}
    )