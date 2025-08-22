import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.showcase_like import ShowcaseLike
from app.models.showcase_comment_like import ShowcaseCommentLike
from app.models.showcase_comment_reply_like import ShowcaseCommentReplyLike
from app.models.showcase import Showcase
from app.models.showcase_comment import ShowcaseComment
from app.models.showcase_comment_reply import ShowcaseCommentReply
from app.schemas.like import ShowcaseLikeCreate, ShowcaseCommentLikeCreate, ShowcaseCommentReplyLikeCreate


class CRUDShowcaseLike:
    
    def create_showcase_like(self, db: Session, *, like_in: ShowcaseLikeCreate, user_id: int, showcase_id: int) -> ShowcaseLike:
        """创建作品点赞"""
        db_obj = ShowcaseLike(
            uuid=str(uuid.uuid4()),
            showcase_id=showcase_id,
            user_id=user_id
        )
        db.add(db_obj)
        
        try:
            db.commit()
            # 更新作品点赞数
            db.query(Showcase).filter(Showcase.id == showcase_id).update(
                {Showcase.likes_count: Showcase.likes_count + 1}
            )
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise ValueError("Already liked")
    
    def remove_showcase_like(self, db: Session, *, user_id: int, showcase_id: int) -> bool:
        """删除作品点赞"""
        like_obj = db.query(ShowcaseLike).filter(
            ShowcaseLike.user_id == user_id,
            ShowcaseLike.showcase_id == showcase_id
        ).first()
        
        if like_obj:
            db.delete(like_obj)
            # 更新作品点赞数
            db.query(Showcase).filter(Showcase.id == showcase_id).update(
                {Showcase.likes_count: Showcase.likes_count - 1}
            )
            db.commit()
            return True
        return False
    
    def get_showcase_like(self, db: Session, *, user_id: int, showcase_id: int) -> Optional[ShowcaseLike]:
        """获取用户对作品的点赞"""
        return db.query(ShowcaseLike).filter(
            ShowcaseLike.user_id == user_id,
            ShowcaseLike.showcase_id == showcase_id
        ).first()


class CRUDShowcaseCommentLike:
    
    def create_comment_like(self, db: Session, *, like_in: ShowcaseCommentLikeCreate, user_id: int, comment_id: int) -> ShowcaseCommentLike:
        """创建评论点赞"""
        db_obj = ShowcaseCommentLike(
            uuid=str(uuid.uuid4()),
            comment_id=comment_id,
            user_id=user_id
        )
        db.add(db_obj)
        
        try:
            db.commit()
            # 更新评论点赞数
            db.query(ShowcaseComment).filter(ShowcaseComment.id == comment_id).update(
                {ShowcaseComment.likes_count: ShowcaseComment.likes_count + 1}
            )
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise ValueError("Already liked")
    
    def remove_comment_like(self, db: Session, *, user_id: int, comment_id: int) -> bool:
        """删除评论点赞"""
        like_obj = db.query(ShowcaseCommentLike).filter(
            ShowcaseCommentLike.user_id == user_id,
            ShowcaseCommentLike.comment_id == comment_id
        ).first()
        
        if like_obj:
            db.delete(like_obj)
            # 更新评论点赞数
            db.query(ShowcaseComment).filter(ShowcaseComment.id == comment_id).update(
                {ShowcaseComment.likes_count: ShowcaseComment.likes_count - 1}
            )
            db.commit()
            return True
        return False
    
    def get_comment_like(self, db: Session, *, user_id: int, comment_id: int) -> Optional[ShowcaseCommentLike]:
        """获取用户对评论的点赞"""
        return db.query(ShowcaseCommentLike).filter(
            ShowcaseCommentLike.user_id == user_id,
            ShowcaseCommentLike.comment_id == comment_id
        ).first()


class CRUDShowcaseCommentReplyLike:
    
    def create_reply_like(self, db: Session, *, like_in: ShowcaseCommentReplyLikeCreate, user_id: int, reply_id: int) -> ShowcaseCommentReplyLike:
        """创建回复点赞"""
        db_obj = ShowcaseCommentReplyLike(
            uuid=str(uuid.uuid4()),
            reply_id=reply_id,
            user_id=user_id
        )
        db.add(db_obj)
        
        try:
            db.commit()
            # 更新回复点赞数
            db.query(ShowcaseCommentReply).filter(ShowcaseCommentReply.id == reply_id).update(
                {ShowcaseCommentReply.likes_count: ShowcaseCommentReply.likes_count + 1}
            )
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise ValueError("Already liked")
    
    def remove_reply_like(self, db: Session, *, user_id: int, reply_id: int) -> bool:
        """删除回复点赞"""
        like_obj = db.query(ShowcaseCommentReplyLike).filter(
            ShowcaseCommentReplyLike.user_id == user_id,
            ShowcaseCommentReplyLike.reply_id == reply_id
        ).first()
        
        if like_obj:
            db.delete(like_obj)
            # 更新回复点赞数
            db.query(ShowcaseCommentReply).filter(ShowcaseCommentReply.id == reply_id).update(
                {ShowcaseCommentReply.likes_count: ShowcaseCommentReply.likes_count - 1}
            )
            db.commit()
            return True
        return False
    
    def get_reply_like(self, db: Session, *, user_id: int, reply_id: int) -> Optional[ShowcaseCommentReplyLike]:
        """获取用户对回复的点赞"""
        return db.query(ShowcaseCommentReplyLike).filter(
            ShowcaseCommentReplyLike.user_id == user_id,
            ShowcaseCommentReplyLike.reply_id == reply_id
        ).first()


# 实例化CRUD对象
crud_showcase_like = CRUDShowcaseLike()
crud_showcase_comment_like = CRUDShowcaseCommentLike()
crud_showcase_comment_reply_like = CRUDShowcaseCommentReplyLike()