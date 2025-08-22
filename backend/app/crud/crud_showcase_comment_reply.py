from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.showcase_comment_reply import ShowcaseCommentReply
from app.schemas.showcase_comment_reply import ShowcaseCommentReplyCreate, ShowcaseCommentReplyUpdate


class CRUDShowcaseCommentReply:
    pass


def create_showcase_comment_reply(db: Session, *, reply_in: ShowcaseCommentReplyCreate, user_id: int, comment_id: int) -> ShowcaseCommentReply:
    db_obj = ShowcaseCommentReply(**reply_in.dict(exclude={"comment_uuid"}), uuid=str(uuid.uuid4()), user_id=user_id, comment_id=comment_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_showcase_comment_reply_by_uuid(db: Session, *, uuid: str) -> Optional[ShowcaseCommentReply]:
    return db.query(ShowcaseCommentReply).options(joinedload(ShowcaseCommentReply.user)).filter(ShowcaseCommentReply.uuid == uuid, ShowcaseCommentReply.deleted_at.is_(None)).first()


def get_multi_by_comment_id(
    db: Session,
    *,
    comment_id: int,
    skip: int = 0,
    limit: int = 10
) -> Tuple[int, list[ShowcaseCommentReply]]:
    query = db.query(ShowcaseCommentReply).options(joinedload(ShowcaseCommentReply.user)).filter(ShowcaseCommentReply.comment_id == comment_id, ShowcaseCommentReply.deleted_at.is_(None))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return total, items


def update_showcase_comment_reply(db: Session, *, db_obj: ShowcaseCommentReply, obj_in: ShowcaseCommentReplyUpdate) -> ShowcaseCommentReply:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_showcase_comment_reply(db: Session, *, db_obj: ShowcaseCommentReply) -> ShowcaseCommentReply:
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


crud_showcase_comment_reply = CRUDShowcaseCommentReply()
