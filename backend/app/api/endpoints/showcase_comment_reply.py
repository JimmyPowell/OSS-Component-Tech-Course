from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api import deps
from app.crud import crud_showcase_comment_reply, crud_showcase_comment
from app.models import User
from app.schemas.showcase_comment_reply import (
    ShowcaseCommentReplyCreate,
    ShowcaseCommentReplyUpdate,
    ShowcaseCommentReplyResponse,
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()


@router.post("/")
def create_showcase_comment_reply(
    *,
    db: Session = Depends(deps.get_mysql_db),
    reply_in: ShowcaseCommentReplyCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create new showcase comment reply.
    """
    comment = crud_showcase_comment.get_showcase_comment_by_uuid(db=db, uuid=reply_in.comment_uuid)
    if not comment:
        return NotFound(message="Showcase comment not found")
        
    reply = crud_showcase_comment_reply.create_showcase_comment_reply(db=db, reply_in=reply_in, user_id=current_user.id, comment_id=comment.id)
    return Success(data=ShowcaseCommentReplyResponse.from_orm(reply).model_dump())


@router.get("/")
def read_showcase_comment_replies(
    db: Session = Depends(deps.get_mysql_db),
    comment_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Retrieve showcase comment replies with pagination.
    """
    total, replies = crud_showcase_comment_reply.get_multi_by_comment_id(
        db,
        comment_id=comment_id,
        skip=skip,
        limit=limit,
    )
    return Success(data={"total": total, "items": [ShowcaseCommentReplyResponse.from_orm(r).model_dump() for r in replies]})


@router.get("/{uuid}")
def read_showcase_comment_reply(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
):
    """
    Get showcase comment reply by UUID.
    """
    reply = crud_showcase_comment_reply.get_showcase_comment_reply_by_uuid(db=db, uuid=uuid)
    if not reply:
        return NotFound(message="Showcase comment reply not found")
    return Success(data=ShowcaseCommentReplyResponse.from_orm(reply).model_dump())


@router.put("/{uuid}")
def update_showcase_comment_reply(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
    reply_in: ShowcaseCommentReplyUpdate,
):
    """
    Update a showcase comment reply.
    """
    reply = crud_showcase_comment_reply.get_showcase_comment_reply_by_uuid(db=db, uuid=uuid)
    if not reply:
        return NotFound(message="Showcase comment reply not found")
    reply = crud_showcase_comment_reply.update_showcase_comment_reply(db=db, db_obj=reply, obj_in=reply_in)
    return Success(data=ShowcaseCommentReplyResponse.from_orm(reply).model_dump())


@router.delete("/{uuid}")
def delete_showcase_comment_reply(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
):
    """
    Delete a showcase comment reply.
    """
    reply = crud_showcase_comment_reply.get_showcase_comment_reply_by_uuid(db=db, uuid=uuid)
    if not reply:
        return NotFound(message="Showcase comment reply not found")
    reply = crud_showcase_comment_reply.remove_showcase_comment_reply(db=db, db_obj=reply)
    return Success(data=ShowcaseCommentReplyResponse.from_orm(reply).model_dump())
