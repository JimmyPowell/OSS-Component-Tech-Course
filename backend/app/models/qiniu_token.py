# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
from enum import Enum as PyEnum

class TokenType(PyEnum):
    upload = "upload"
    download = "download"

class TokenStatus(PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"
    used = "used"

class QiniuToken(Base):
    __tablename__ = "qiniu_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_type = Column(Enum(TokenType), nullable=False)
    bucket = Column(String(100), nullable=False)
    file_key = Column(String(512), nullable=True)
    token = Column(String(1024), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    purpose = Column(String(255), nullable=True, comment="Token usage purpose description")
    status = Column(Enum(TokenStatus), nullable=False, default=TokenStatus.pending)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)
    used_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="qiniu_tokens")
    approver = relationship("User", foreign_keys=[approved_by])