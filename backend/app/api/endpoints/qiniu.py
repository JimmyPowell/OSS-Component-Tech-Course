# -*- coding: utf-8 -*-
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api import deps
from app.crud.crud_qiniu_token import crud_qiniu_token
from app.schemas.qiniu_token import (
    QiniuTokenCreate, QiniuTokenResponse, QiniuTokenListResponse, 
    QiniuTokenApproval, TokenStatus, TokenType, QiniuAdminUploadRequest
)
from app.schemas.response import UnifiedResponse
from app.services.qiniu_service import qiniu_service
from app.models.user import User

router = APIRouter()

@router.post("/upload-token")
def request_upload_token(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    token_request: QiniuTokenCreate
):
    """
    Request an upload token for Qiniu Cloud Storage
    """
    if token_request.token_type != TokenType.upload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type for upload request"
        )
    
    try:
        # Generate upload token (expires in 1 hour by default)
        expires_seconds = 3600
        bucket = token_request.bucket or qiniu_service.bucket
        upload_token = qiniu_service.generate_upload_token(
            bucket=bucket,
            key=token_request.file_key,
            expires=expires_seconds
        )
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_seconds)
        
        # Create token record in database
        # Update token_request with actual bucket if not provided
        if not token_request.bucket:
            token_request.bucket = bucket
        
        token_record = crud_qiniu_token.create_token_request(
            db=db,
            token_data=token_request,
            user_id=current_user.id,
            token=upload_token,
            expires_at=expires_at
        )
        
        return UnifiedResponse(
            code=201,
            message="Upload token generated successfully",
            data=QiniuTokenResponse.from_orm(token_record)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload token: {str(e)}"
        )

@router.post("/download-token", )
def request_download_token(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    token_request: QiniuTokenCreate,
    file_url: str
):
    """
    Request a download token for private Qiniu resources
    """
    if token_request.token_type != TokenType.download:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type for download request"
        )
    
    if not token_request.file_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File key is required for download token"
        )
    
    try:
        # Generate download token (expires in 1 hour by default)
        expires_seconds = 3600
        download_url = qiniu_service.generate_download_token(
            url=file_url,
            expires=expires_seconds
        )
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_seconds)
        
        # Create token record in database
        token_record = crud_qiniu_token.create_token_request(
            db=db,
            token_data=token_request,
            user_id=current_user.id,
            token=download_url,
            expires_at=expires_at
        )
        
        return UnifiedResponse(
            code=201,
            message="Download token generated successfully",
            data=QiniuTokenResponse.from_orm(token_record)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download token: {str(e)}"
        )

@router.get("/my-tokens", )
def get_my_tokens(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 20
):
    """
    Get current user's token requests
    """
    tokens = crud_qiniu_token.get_user_tokens(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return UnifiedResponse(
        code=200,
        message="Tokens retrieved successfully",
        data=[QiniuTokenListResponse.from_orm(token) for token in tokens]
    )

@router.get("/pending-tokens", )
def get_pending_tokens(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    skip: int = 0,
    limit: int = 20
):
    """
    Get pending tokens for admin approval (Manager only)
    """
    tokens = crud_qiniu_token.get_pending_tokens(
        db=db, skip=skip, limit=limit
    )
    
    return UnifiedResponse(
        code=200,
        message="Pending tokens retrieved successfully",
        data=[QiniuTokenListResponse.from_orm(token) for token in tokens]
    )

@router.post("/tokens/{token_id}/approve", )
def approve_token(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    token_id: int,
    approval_data: QiniuTokenApproval
):
    """
    Approve or reject a token request (Manager only)
    """
    token_record = crud_qiniu_token.get_by_id(db=db, token_id=token_id)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    if token_record.status != TokenStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is not in pending status"
        )
    
    updated_token = crud_qiniu_token.approve_token(
        db=db,
        token_id=token_id,
        approved_by=current_user.id,
        approval_data=approval_data
    )
    
    return UnifiedResponse(
        code=200,
        message=f"Token {approval_data.status.value} successfully",
        data=QiniuTokenResponse.from_orm(updated_token)
    )

@router.post("/tokens/{token_id}/mark-used", )
def mark_token_used(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    token_id: int
):
    """
    Mark a token as used
    """
    token_record = crud_qiniu_token.get_by_id(db=db, token_id=token_id)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # Check if user owns the token or is a manager
    if token_record.user_id != current_user.id and current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if token_record.status not in [TokenStatus.pending, TokenStatus.approved]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token cannot be marked as used"
        )
    
    updated_token = crud_qiniu_token.mark_token_used(db=db, token_id=token_id)
    
    return UnifiedResponse(
        code=200,
        message="Token marked as used successfully",
        data=QiniuTokenResponse.from_orm(updated_token)
    )

@router.post("/cleanup-expired", )
def cleanup_expired_tokens(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user)
):
    """
    Cleanup expired tokens (Manager only)
    """
    cleaned_count = crud_qiniu_token.cleanup_expired_tokens(db=db)
    
    return UnifiedResponse(
        code=200,
        message="Expired tokens cleaned up successfully",
        data={"cleaned_count": cleaned_count}
    )

@router.get("/bucket-info", )
def get_bucket_info(
    current_user: User = Depends(deps.get_current_manager_user)
):
    """
    Get Qiniu bucket configuration info (Manager only)
    """
    bucket_info = qiniu_service.get_bucket_info()
    
    return UnifiedResponse(
        code=200,
        message="Bucket info retrieved successfully",
        data=bucket_info
    )

@router.post("/admin/upload-token")
def request_admin_upload_token(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    upload_request: QiniuAdminUploadRequest
):
    """
    Request an upload token for managers (auto-approved)
    """
    try:
        # Generate upload token (expires in 1 hour by default)
        expires_seconds = 3600
        upload_token = qiniu_service.generate_upload_token(
            bucket=qiniu_service.bucket,  # Use default bucket from env
            key=upload_request.file_key,
            expires=expires_seconds
        )
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_seconds)
        
        # Create approved token record directly for managers
        token_data = QiniuTokenCreate(
            token_type=TokenType.upload,
            bucket=qiniu_service.bucket,
            file_key=upload_request.file_key,
            purpose=upload_request.purpose
        )
        
        token_record = crud_qiniu_token.create_token_request(
            db=db,
            token_data=token_data,
            user_id=current_user.id,
            token=upload_token,
            expires_at=expires_at
        )
        
        # Auto-approve for managers
        approved_token = crud_qiniu_token.approve_token(
            db=db,
            token_id=token_record.id,
            approved_by=current_user.id,
            approval_data=QiniuTokenApproval(status=TokenStatus.approved)
        )
        
        return UnifiedResponse(
            code=201,
            message="Upload token generated and approved successfully",
            data={
                **QiniuTokenResponse.from_orm(approved_token).dict(),
                "upload_domain": qiniu_service.upload_domain,
                "download_domain": qiniu_service.download_domain
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload token: {str(e)}"
        )