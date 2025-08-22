from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api import deps
from app.crud import crud_showcase_comment, crud_showcase
from app.models import User
from app.schemas.showcase_comment import (
    ShowcaseCommentCreate,
    ShowcaseCommentUpdate,
    ShowcaseCommentResponse,
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()


@router.post("/")
def create_showcase_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_in: ShowcaseCommentCreate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    Create new showcase comment.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=comment_in.showcase_uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
        
    comment = crud_showcase_comment.create_showcase_comment(db=db, comment_in=comment_in, user_id=current_user.id, showcase_id=showcase.id)
    return Success(data=ShowcaseCommentResponse.from_orm(comment).model_dump())


@router.get("/")
def read_showcase_comments(
    db: Session = Depends(deps.get_db),
    showcase_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|likes_count)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """
    Retrieve showcase comments with pagination.
    """
    total, comments = crud_showcase_comment.get_multi_by_showcase_id(
        db,
        showcase_id=showcase_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return Success(data={"total": total, "items": [ShowcaseCommentResponse.from_orm(c).model_dump() for c in comments]})


@router.get("/{uuid}")
def read_showcase_comment(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    Get showcase comment by UUID.
    """
    comment = crud_showcase_comment.get_showcase_comment_by_uuid(db=db, uuid=uuid)
    if not comment:
        return NotFound(message="Showcase comment not found")
    return Success(data=ShowcaseCommentResponse.from_orm(comment).model_dump())


@router.put("/{uuid}")
def update_showcase_comment(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    comment_in: ShowcaseCommentUpdate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    Update a showcase comment. Users can only update their own comments.
    """
    comment = crud_showcase_comment.get_showcase_comment_by_uuid(db=db, uuid=uuid)
    if not comment:
        return NotFound(message="Showcase comment not found")
    
    # Check if user is the author of the comment
    if comment.user_id != current_user.id:
        return BadRequest(message="You can only update your own comments")
    
    comment = crud_showcase_comment.update_showcase_comment(db=db, db_obj=comment, obj_in=comment_in)
    return Success(data=ShowcaseCommentResponse.from_orm(comment).model_dump())


@router.delete("/{uuid}")
def delete_showcase_comment(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    Delete a showcase comment. Users can only delete their own comments.
    """
    comment = crud_showcase_comment.get_showcase_comment_by_uuid(db=db, uuid=uuid)
    if not comment:
        return NotFound(message="Showcase comment not found")
    
    # Check if user is the author of the comment
    if comment.user_id != current_user.id:
        return BadRequest(message="You can only delete your own comments")
    
    comment = crud_showcase_comment.remove_showcase_comment(db=db, db_obj=comment)
    return Success(data=ShowcaseCommentResponse.from_orm(comment).model_dump())
