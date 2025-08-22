from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.forum_post import ForumPost
from app.schemas.forum_post import ForumPostCreate, ForumPostUpdate


def create_forum_post(db: Session, *, post_in: ForumPostCreate, user_id: int) -> ForumPost:
    db_obj = ForumPost(
        **post_in.dict(exclude={"uuid"}), 
        uuid=str(uuid.uuid4()), 
        user_id=user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 更新分类的帖子计数
    from app.crud.crud_forum_category import update_post_count
    update_post_count(db, category_id=db_obj.category_id)
    
    return db_obj


def get_forum_post_by_uuid(db: Session, *, uuid: str) -> Optional[ForumPost]:
    return db.query(ForumPost).options(
        joinedload(ForumPost.author),
        joinedload(ForumPost.category),
        joinedload(ForumPost.last_reply_user)
    ).filter(
        ForumPost.uuid == uuid, 
        ForumPost.is_deleted == False,
        ForumPost.deleted_at.is_(None)
    ).first()


def get_forum_post_by_id(db: Session, *, post_id: int) -> Optional[ForumPost]:
    return db.query(ForumPost).filter(
        ForumPost.id == post_id, 
        ForumPost.is_deleted == False,
        ForumPost.deleted_at.is_(None)
    ).first()


def get_by_title(db: Session, *, title: str, category_id: Optional[int] = None) -> Optional[ForumPost]:
    query = db.query(ForumPost).filter(
        ForumPost.title == title, 
        ForumPost.is_deleted == False,
        ForumPost.deleted_at.is_(None)
    )
    
    if category_id:
        query = query.filter(ForumPost.category_id == category_id)
    
    return query.first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    user_id: Optional[int] = None,
    title: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    is_locked: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[ForumPost]]:
    query = db.query(ForumPost).options(
        joinedload(ForumPost.author),
        joinedload(ForumPost.category),
        joinedload(ForumPost.last_reply_user)
    ).filter(
        ForumPost.is_deleted == False,
        ForumPost.deleted_at.is_(None)
    )

    filters = []
    if category_id:
        filters.append(ForumPost.category_id == category_id)
    if user_id:
        filters.append(ForumPost.user_id == user_id)
    if title:
        filters.append(ForumPost.title.ilike(f"%{title}%"))
    if is_pinned is not None:
        filters.append(ForumPost.is_pinned == is_pinned)
    if is_locked is not None:
        filters.append(ForumPost.is_locked == is_locked)
    if start_time:
        filters.append(ForumPost.created_at >= start_time)
    if end_time:
        filters.append(ForumPost.created_at <= end_time)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    
    # 置顶帖在前，然后按最后回复时间排序
    items = query.order_by(
        desc(ForumPost.is_pinned),
        desc(ForumPost.last_reply_at),
        desc(ForumPost.created_at)
    ).offset(skip).limit(limit).all()

    return total, items


def get_hot_posts(db: Session, *, limit: int = 10, days: int = 7) -> list[ForumPost]:
    """获取热门帖子（按回复数和浏览数排序）"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    return db.query(ForumPost).options(
        joinedload(ForumPost.author),
        joinedload(ForumPost.category),
        joinedload(ForumPost.last_reply_user)
    ).filter(
        ForumPost.is_deleted == False,
        ForumPost.deleted_at.is_(None),
        ForumPost.created_at >= cutoff_date
    ).order_by(
        desc(ForumPost.reply_count),
        desc(ForumPost.view_count)
    ).limit(limit).all()


def update_forum_post(db: Session, *, db_obj: ForumPost, obj_in: ForumPostUpdate) -> ForumPost:
    update_data = obj_in.dict(exclude_unset=True)
    old_category_id = db_obj.category_id
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 如果分类发生变化，更新相关分类的帖子计数
    if old_category_id != db_obj.category_id:
        from app.crud.crud_forum_category import update_post_count
        update_post_count(db, category_id=old_category_id)
        update_post_count(db, category_id=db_obj.category_id)
    
    return db_obj


def increment_view_count(db: Session, *, db_obj: ForumPost) -> ForumPost:
    """增加浏览数"""
    db_obj.view_count += 1
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_reply_info(db: Session, *, post_id: int, user_id: int, increment: bool = True) -> Optional[ForumPost]:
    """更新帖子回复信息"""
    post = get_forum_post_by_id(db, post_id=post_id)
    if not post:
        return None
    
    if increment:
        post.reply_count += 1
    else:
        post.reply_count = max(0, post.reply_count - 1)
    
    post.last_reply_at = datetime.utcnow()
    post.last_reply_user_id = user_id
    
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def pin_post(db: Session, *, db_obj: ForumPost, pinned: bool = True) -> ForumPost:
    """置顶/取消置顶帖子"""
    db_obj.is_pinned = pinned
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def lock_post(db: Session, *, db_obj: ForumPost, locked: bool = True) -> ForumPost:
    """锁定/解锁帖子"""
    db_obj.is_locked = locked
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_forum_post(db: Session, *, db_obj: ForumPost) -> ForumPost:
    """软删除帖子"""
    db_obj.is_deleted = True
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 更新分类的帖子计数
    from app.crud.crud_forum_category import update_post_count
    update_post_count(db, category_id=db_obj.category_id)
    
    return db_obj