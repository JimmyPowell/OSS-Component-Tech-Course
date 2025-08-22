# -*- coding: utf-8 -*-
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import uuid as uuid_module

from app.models.qiniu_token import QiniuToken, TokenStatus, TokenType
from app.schemas.qiniu_token import QiniuTokenCreate, QiniuTokenApproval

class CRUDQiniuToken:
    def create_token_request(
        self, 
        db: Session, 
        *, 
        token_data: QiniuTokenCreate, 
        user_id: int,
        token: str,
        expires_at: datetime
    ) -> QiniuToken:
        """Create a new Qiniu token request"""
        db_obj = QiniuToken(
            uuid=str(uuid_module.uuid4()),
            user_id=user_id,
            token_type=token_data.token_type,
            bucket=token_data.bucket,
            file_key=token_data.file_key,
            token=token,
            expires_at=expires_at,
            purpose=token_data.purpose,
            status=TokenStatus.pending
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, *, token_id: int) -> Optional[QiniuToken]:
        """Get token by ID"""
        return db.query(QiniuToken).filter(QiniuToken.id == token_id).first()
    
    def get_by_uuid(self, db: Session, *, uuid: str) -> Optional[QiniuToken]:
        """Get token by UUID"""
        return db.query(QiniuToken).filter(QiniuToken.uuid == uuid).first()
    
    def get_user_tokens(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[QiniuToken]:
        """Get tokens for a specific user"""
        return (
            db.query(QiniuToken)
            .filter(QiniuToken.user_id == user_id)
            .order_by(QiniuToken.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_pending_tokens(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[QiniuToken]:
        """Get all pending tokens for admin approval"""
        return (
            db.query(QiniuToken)
            .filter(QiniuToken.status == TokenStatus.pending)
            .order_by(QiniuToken.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def approve_token(
        self, 
        db: Session, 
        *, 
        token_id: int, 
        approved_by: int, 
        approval_data: QiniuTokenApproval
    ) -> Optional[QiniuToken]:
        """Approve or reject a token request"""
        db_obj = self.get_by_id(db, token_id=token_id)
        if not db_obj:
            return None
        
        db_obj.status = approval_data.status
        db_obj.approved_by = approved_by
        db_obj.approved_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def mark_token_used(self, db: Session, *, token_id: int) -> Optional[QiniuToken]:
        """Mark a token as used"""
        db_obj = self.get_by_id(db, token_id=token_id)
        if not db_obj:
            return None
        
        db_obj.status = TokenStatus.used
        db_obj.used_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """Mark expired tokens as expired"""
        now = datetime.utcnow()
        result = (
            db.query(QiniuToken)
            .filter(
                and_(
                    QiniuToken.expires_at < now,
                    or_(
                        QiniuToken.status == TokenStatus.pending,
                        QiniuToken.status == TokenStatus.approved
                    )
                )
            )
            .update({QiniuToken.status: TokenStatus.expired})
        )
        db.commit()
        return result

crud_qiniu_token = CRUDQiniuToken()