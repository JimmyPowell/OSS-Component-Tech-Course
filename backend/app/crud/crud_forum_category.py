from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.forum_category import ForumCategory
from app.schemas.forum_category import ForumCategoryCreate, ForumCategoryUpdate


def create_forum_category(db: Session, *, category_in: ForumCategoryCreate) -> ForumCategory:
    db_obj = ForumCategory(**category_in.dict(exclude={"uuid"}), uuid=str(uuid.uuid4()))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_forum_category_by_uuid(db: Session, *, uuid: str) -> Optional[ForumCategory]:
    return db.query(ForumCategory).filter(
        ForumCategory.uuid == uuid, 
        ForumCategory.deleted_at.is_(None)
    ).first()


def get_forum_category_by_id(db: Session, *, category_id: int) -> Optional[ForumCategory]:
    return db.query(ForumCategory).filter(
        ForumCategory.id == category_id, 
        ForumCategory.deleted_at.is_(None)
    ).first()


def get_by_name(db: Session, *, name: str) -> Optional[ForumCategory]:
    return db.query(ForumCategory).filter(
        ForumCategory.name == name, 
        ForumCategory.deleted_at.is_(None)
    ).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_inactive: bool = False
) -> Tuple[int, list[ForumCategory]]:
    query = db.query(ForumCategory).filter(ForumCategory.deleted_at.is_(None))

    filters = []
    if name:
        filters.append(ForumCategory.name.ilike(f"%{name}%"))
    if is_active is not None:
        filters.append(ForumCategory.is_active == is_active)
    elif not include_inactive:
        filters.append(ForumCategory.is_active == True)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = query.order_by(ForumCategory.sort_order.asc(), ForumCategory.id.asc()).offset(skip).limit(limit).all()

    return total, items


def get_active_categories(db: Session) -> list[ForumCategory]:
    """获取所有激活的分类，按排序顺序"""
    return db.query(ForumCategory).filter(
        ForumCategory.deleted_at.is_(None),
        ForumCategory.is_active == True
    ).order_by(ForumCategory.sort_order.asc(), ForumCategory.id.asc()).all()


def update_forum_category(db: Session, *, db_obj: ForumCategory, obj_in: ForumCategoryUpdate) -> ForumCategory:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_post_count(db: Session, *, category_id: int) -> Optional[ForumCategory]:
    """更新分类的帖子数量统计"""
    from app.models.forum_post import ForumPost
    
    category = get_forum_category_by_id(db, category_id=category_id)
    if not category:
        return None
    
    post_count = db.query(func.count(ForumPost.id)).filter(
        ForumPost.category_id == category_id,
        ForumPost.is_deleted == False,
        ForumPost.deleted_at.is_(None)
    ).scalar()
    
    category.post_count = post_count or 0
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def remove_forum_category(db: Session, *, db_obj: ForumCategory) -> ForumCategory:
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj