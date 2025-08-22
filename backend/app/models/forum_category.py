from sqlalchemy import Column, String, TIMESTAMP, TEXT, Boolean, Integer
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func

from app.config.database import Base


class ForumCategory(Base):
    __tablename__ = "forum_categories"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(TEXT, nullable=True)
    icon = Column(String(100), nullable=True)
    sort_order = Column(Integer, nullable=False, server_default='0', index=True)
    is_active = Column(Boolean, nullable=False, server_default='1', index=True)
    post_count = Column(INTEGER(unsigned=True), nullable=False, server_default='0')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)