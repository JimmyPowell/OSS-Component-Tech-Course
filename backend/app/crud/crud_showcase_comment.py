from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.showcase_comment import ShowcaseComment
from app.schemas.showcase_comment import ShowcaseCommentCreate, ShowcaseCommentUpdate


def create_showcase_comment(db: Session, *, comment_in: ShowcaseCommentCreate, user_id: int, showcase_id: int) -> ShowcaseComment:
    db_obj = ShowcaseComment(**comment_in.dict(exclude={"uuid", "showcase_uuid"}), uuid=str(uuid.uuid4()), user_id=user_id, showcase_id=showcase_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_showcase_comment_by_uuid(db: Session, *, uuid: str) -> Optional[ShowcaseComment]:
    return db.query(ShowcaseComment).options(joinedload(ShowcaseComment.user)).filter(ShowcaseComment.uuid == uuid, ShowcaseComment.deleted_at.is_(None)).first()


def get_multi_by_showcase_id(
    db: Session,
    *,
    showcase_id: int,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Tuple[int, list[ShowcaseComment]]:
    query = db.query(ShowcaseComment).options(joinedload(ShowcaseComment.user)).filter(ShowcaseComment.showcase_id == showcase_id, ShowcaseComment.deleted_at.is_(None))

    # Add sorting
    if sort_by == "created_at":
        if sort_order == "desc":
            query = query.order_by(ShowcaseComment.created_at.desc())
        else:
            query = query.order_by(ShowcaseComment.created_at.asc())
    elif sort_by == "likes_count":
        if sort_order == "desc":
            query = query.order_by(ShowcaseComment.likes_count.desc())
        else:
            query = query.order_by(ShowcaseComment.likes_count.asc())

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return total, items


def update_showcase_comment(db: Session, *, db_obj: ShowcaseComment, obj_in: ShowcaseCommentUpdate) -> ShowcaseComment:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_showcase_comment(db: Session, *, db_obj: ShowcaseComment) -> ShowcaseComment:
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
