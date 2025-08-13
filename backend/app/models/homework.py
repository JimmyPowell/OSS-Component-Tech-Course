from sqlalchemy import Column, String, TIMESTAMP, TEXT, JSON
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT
from sqlalchemy.sql import func

from app.config.database import Base


class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(TEXT, nullable=True)
    content = Column(LONGTEXT, nullable=True)
    cover_url = Column(String(512), nullable=True)
    resource_urls = Column(JSON, nullable=True)
    creator_id = Column(INTEGER(unsigned=True), nullable=False, index=True)
    lasting_time = Column(INTEGER(unsigned=True), nullable=True, comment='Lasting time in minutes')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)
