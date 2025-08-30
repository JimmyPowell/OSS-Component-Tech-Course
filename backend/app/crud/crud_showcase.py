from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, case
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.showcase import Showcase
from app.models.user import User
from app.schemas.showcase import ShowcaseCreate, ShowcaseUpdate


def create_showcase(db: Session, *, showcase_in: ShowcaseCreate, author_id: int) -> Showcase:
    db_obj = Showcase(**showcase_in.dict(), uuid=str(uuid.uuid4()), author_id=author_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_showcase_by_uuid(db: Session, *, uuid: str) -> Optional[Showcase]:
    return db.query(Showcase).options(joinedload(Showcase.author)).filter(Showcase.uuid == uuid, Showcase.deleted_at.is_(None)).first()


def get_by_name(db: Session, *, name: str) -> Optional[Showcase]:
    return db.query(Showcase).filter(Showcase.name == name, Showcase.deleted_at.is_(None)).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[Showcase]]:
    query = db.query(Showcase).options(joinedload(Showcase.author)).filter(Showcase.deleted_at.is_(None))

    filters = []
    if name:
        filters.append(Showcase.name.ilike(f"%{name}%"))
    if status:
        filters.append(Showcase.status == status)
    if start_time:
        filters.append(Showcase.created_at >= start_time)
    if end_time:
        filters.append(Showcase.created_at <= end_time)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return total, items


def update_showcase(db: Session, *, db_obj: Showcase, obj_in: ShowcaseUpdate) -> Showcase:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_showcase(db: Session, *, db_obj: Showcase) -> Showcase:
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def approve_showcase(db: Session, *, db_obj: Showcase, reviewer_id: int, review_comment: Optional[str] = None) -> Showcase:
    """审核通过：pending -> published"""
    db_obj.status = 'published'
    db_obj.reviewer_id = reviewer_id
    db_obj.review_comment = review_comment
    db_obj.reviewed_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def reject_showcase(db: Session, *, db_obj: Showcase, reviewer_id: int, review_comment: str) -> Showcase:
    """审核拒绝：pending -> reject"""
    db_obj.status = 'reject'
    db_obj.reviewer_id = reviewer_id
    db_obj.review_comment = review_comment
    db_obj.reviewed_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def promote_to_excellent(db: Session, *, db_obj: Showcase, reviewer_id: int, review_comment: Optional[str] = None) -> Showcase:
    """设为优秀作品：published -> excellent"""
    db_obj.status = 'excellent'
    db_obj.reviewer_id = reviewer_id
    db_obj.review_comment = review_comment
    db_obj.reviewed_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def archive_showcase(db: Session, *, db_obj: Showcase) -> Showcase:
    """下架作品：published/excellent -> draft"""
    if db_obj.status in ['published', 'excellent']:
        db_obj.previous_status = db_obj.status
        db_obj.status = 'draft'
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj


def restore_showcase(db: Session, *, db_obj: Showcase) -> Showcase:
    """恢复作品：draft -> published/excellent"""
    if db_obj.status == 'draft' and db_obj.previous_status:
        db_obj.status = db_obj.previous_status
        db_obj.previous_status = None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj


def get_showcases_for_frontend(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[Showcase]]:
    """获取前端展示的作品 - 只显示优秀作品"""
    query = db.query(Showcase).options(joinedload(Showcase.author)).filter(
        Showcase.deleted_at.is_(None),
        Showcase.status == 'excellent'
    )

    filters = []
    if name:
        filters.append(Showcase.name.ilike(f"%{name}%"))
    if start_time:
        filters.append(Showcase.created_at >= start_time)
    if end_time:
        filters.append(Showcase.created_at <= end_time)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = query.order_by(
        Showcase.created_at.desc()
    ).offset(skip).limit(limit).all()

    return total, items
