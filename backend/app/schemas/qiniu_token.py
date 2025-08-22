# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TokenType(str, Enum):
    upload = "upload"
    download = "download"

class TokenStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"
    used = "used"

class QiniuTokenBase(BaseModel):
    token_type: TokenType
    bucket: Optional[str] = Field(None, max_length=100, description="Qiniu bucket name")
    file_key: Optional[str] = Field(None, max_length=512, description="File key for download token")
    purpose: Optional[str] = Field(None, max_length=255, description="Token usage purpose")

class QiniuTokenCreate(QiniuTokenBase):
    pass

class QiniuAdminUploadRequest(BaseModel):
    file_key: str = Field(..., max_length=512, description="File key for upload")
    purpose: Optional[str] = Field(None, max_length=255, description="Upload purpose description")

class QiniuTokenApproval(BaseModel):
    status: TokenStatus
    approval_note: Optional[str] = None

class QiniuTokenResponse(QiniuTokenBase):
    id: int
    uuid: str
    user_id: int
    token: str
    expires_at: datetime
    status: TokenStatus
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QiniuTokenListResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    token_type: TokenType
    bucket: str
    file_key: Optional[str]
    purpose: Optional[str]
    status: TokenStatus
    expires_at: datetime
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True