from sqlalchemy import Column, String, TIMESTAMP, TEXT, Enum
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func

from app.config.database import Base


class CourseResource(Base):
    __tablename__ = "course_resources"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(Enum('ppt', 'video', 'attachment', 'other'), nullable=False, index=True)
    description = Column(TEXT, nullable=True)
    creator_id = Column(INTEGER(unsigned=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)
    cover_url = Column(String(512), nullable=True)
    resource_url = Column(String(512), nullable=False)
    file_size = Column(INTEGER(unsigned=True), nullable=True)
    mime_type = Column(String(100), nullable=True)
    download_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
