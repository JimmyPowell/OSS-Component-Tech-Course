from sqlalchemy import Column, String, TIMESTAMP, TEXT, INTEGER
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.sql import func

from app.config.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    summary = Column(String(512), nullable=True)
    detail_info = Column(LONGTEXT, nullable=True)
    cover_url = Column(String(512), nullable=True)
    publisher_id = Column(INTEGER(unsigned=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)