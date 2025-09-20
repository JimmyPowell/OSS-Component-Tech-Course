from sqlalchemy import Column, String, TIMESTAMP, TEXT, Enum, Index
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func
import enum

from app.config.database import Base


class CourseResourceStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class CourseResource(Base):
    __tablename__ = "course_resources"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    summary = Column(String(512), nullable=True)
    type = Column(Enum('ppt', 'video', 'attachment', 'other'), nullable=False, index=True)
    description = Column(TEXT, nullable=True)
    creator_id = Column(INTEGER(unsigned=True), nullable=False, index=True)
    status = Column(
        Enum(CourseResourceStatus),
        default=CourseResourceStatus.draft,
        nullable=False,
        comment="状态：草稿/已发布"
    )
    # 全局排序（越小越靠前，NULL 表示默认在最后）
    sort_order = Column(INTEGER(), nullable=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)
    cover_url = Column(String(512), nullable=True)
    resource_url = Column(String(512), nullable=False)
    # 转载相关：是否转载、转载来源平台
    is_repost = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    source_platform = Column(String(50), nullable=True)
    file_size = Column(INTEGER(unsigned=True), nullable=True)
    mime_type = Column(String(100), nullable=True)
    download_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')

    # 索引
    __table_args__ = (
        Index('idx_course_resource_status', 'status'),
        Index('idx_course_resource_creator', 'creator_id'),
        Index('idx_course_resource_published', 'status', 'created_at'),
        {'comment': '课程资源表'}
    )
