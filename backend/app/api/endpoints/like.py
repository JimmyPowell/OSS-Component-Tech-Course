from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_showcase, crud_showcase_comment
from app.crud.crud_like import crud_showcase_like, crud_showcase_comment_like, crud_showcase_comment_reply_like
from app.crud.crud_showcase_comment_reply import crud_showcase_comment_reply
from app.crud.crud_notification import crud_notification
from app.models import User
from app.schemas.notification import NotificationCreate
from app.schemas.like import (
    ShowcaseLikeCreate,
    ShowcaseCommentLikeCreate,
    ShowcaseCommentReplyLikeCreate,
    ShowcaseLikeResponse,
    ShowcaseCommentLikeResponse,
    ShowcaseCommentReplyLikeResponse
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()


# Showcase likes
@router.post("/showcase/", response_model=dict)
def toggle_showcase_like(
    *,
    db: Session = Depends(deps.get_db),
    like_in: ShowcaseLikeCreate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    切换作品点赞状态
    """
    # 验证作品是否存在
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=like_in.showcase_uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    
    # 检查是否已点赞
    existing_like = crud_showcase_like.get_showcase_like(
        db=db, user_id=current_user.id, showcase_id=showcase.id
    )
    
    if existing_like:
        # 取消点赞
        success = crud_showcase_like.remove_showcase_like(
            db=db, user_id=current_user.id, showcase_id=showcase.id
        )
        return Success(data={"liked": False, "message": "Like removed"})
    else:
        # 添加点赞
        try:
            like = crud_showcase_like.create_showcase_like(
                db=db, like_in=like_in, user_id=current_user.id, showcase_id=showcase.id
            )
            
            # 如果点赞者不是作品作者，则创建点赞通知给作品作者
            if current_user.id != showcase.author_id:
                notification_in = NotificationCreate(
                    recipient_id=showcase.author_id,
                    sender_id=current_user.id,
                    type="like_showcase",
                    title=f"{current_user.username} 赞了您的作品",
                    content=f"在作品《{showcase.name}》中获得了一个赞",
                    related_id=showcase.id,
                    related_uuid=showcase.uuid
                )
                crud_notification.create_notification(db=db, notification_in=notification_in)
            
            return Success(data={"liked": True, "message": "Like added", "like": ShowcaseLikeResponse.from_orm(like).model_dump()})
        except ValueError as e:
            return BadRequest(message=str(e))


@router.get("/showcase/{showcase_uuid}/status")
def get_showcase_like_status(
    *,
    db: Session = Depends(deps.get_db),
    showcase_uuid: str,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    获取用户对作品的点赞状态
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=showcase_uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    
    like = crud_showcase_like.get_showcase_like(
        db=db, user_id=current_user.id, showcase_id=showcase.id
    )
    
    return Success(data={"liked": like is not None})


# Comment likes
@router.post("/comment/", response_model=dict)
def toggle_comment_like(
    *,
    db: Session = Depends(deps.get_db),
    like_in: ShowcaseCommentLikeCreate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    切换评论点赞状态
    """
    # 验证评论是否存在
    comment = crud_showcase_comment.get_showcase_comment_by_uuid(db=db, uuid=like_in.comment_uuid)
    if not comment:
        return NotFound(message="Comment not found")
    
    # 检查是否已点赞
    existing_like = crud_showcase_comment_like.get_comment_like(
        db=db, user_id=current_user.id, comment_id=comment.id
    )
    
    if existing_like:
        # 取消点赞
        success = crud_showcase_comment_like.remove_comment_like(
            db=db, user_id=current_user.id, comment_id=comment.id
        )
        return Success(data={"liked": False, "message": "Like removed"})
    else:
        # 添加点赞
        try:
            like = crud_showcase_comment_like.create_comment_like(
                db=db, like_in=like_in, user_id=current_user.id, comment_id=comment.id
            )
            
            # 如果点赞者不是评论作者，则创建点赞通知给评论作者
            if current_user.id != comment.user_id:
                notification_in = NotificationCreate(
                    recipient_id=comment.user_id,
                    sender_id=current_user.id,
                    type="like_comment",
                    title=f"{current_user.username} 赞了您的评论",
                    content=f"评论内容：{comment.content[:50]}{'...' if len(comment.content) > 50 else ''}",
                    related_id=comment.id,
                    related_uuid=comment.uuid
                )
                crud_notification.create_notification(db=db, notification_in=notification_in)
            
            return Success(data={"liked": True, "message": "Like added", "like": ShowcaseCommentLikeResponse.from_orm(like).model_dump()})
        except ValueError as e:
            return BadRequest(message=str(e))


@router.get("/comment/{comment_uuid}/status")
def get_comment_like_status(
    *,
    db: Session = Depends(deps.get_db),
    comment_uuid: str,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    获取用户对评论的点赞状态
    """
    comment = crud_showcase_comment.get_showcase_comment_by_uuid(db=db, uuid=comment_uuid)
    if not comment:
        return NotFound(message="Comment not found")
    
    like = crud_showcase_comment_like.get_comment_like(
        db=db, user_id=current_user.id, comment_id=comment.id
    )
    
    return Success(data={"liked": like is not None})


# Reply likes
@router.post("/reply/", response_model=dict)
def toggle_reply_like(
    *,
    db: Session = Depends(deps.get_db),
    like_in: ShowcaseCommentReplyLikeCreate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    切换回复点赞状态
    """
    # 验证回复是否存在
    reply = crud_showcase_comment_reply.get_showcase_comment_reply_by_uuid(db=db, uuid=like_in.reply_uuid)
    if not reply:
        return NotFound(message="Reply not found")
    
    # 检查是否已点赞
    existing_like = crud_showcase_comment_reply_like.get_reply_like(
        db=db, user_id=current_user.id, reply_id=reply.id
    )
    
    if existing_like:
        # 取消点赞
        success = crud_showcase_comment_reply_like.remove_reply_like(
            db=db, user_id=current_user.id, reply_id=reply.id
        )
        return Success(data={"liked": False, "message": "Like removed"})
    else:
        # 添加点赞
        try:
            like = crud_showcase_comment_reply_like.create_reply_like(
                db=db, like_in=like_in, user_id=current_user.id, reply_id=reply.id
            )
            
            # 如果点赞者不是回复作者，则创建点赞通知给回复作者
            if current_user.id != reply.user_id:
                notification_in = NotificationCreate(
                    recipient_id=reply.user_id,
                    sender_id=current_user.id,
                    type="like_comment",
                    title=f"{current_user.username} 赞了您的回复",
                    content=f"回复内容：{reply.content[:50]}{'...' if len(reply.content) > 50 else ''}",
                    related_id=reply.id,
                    related_uuid=reply.uuid
                )
                crud_notification.create_notification(db=db, notification_in=notification_in)
            
            return Success(data={"liked": True, "message": "Like added", "like": ShowcaseCommentReplyLikeResponse.from_orm(like).model_dump()})
        except ValueError as e:
            return BadRequest(message=str(e))


@router.get("/reply/{reply_uuid}/status")
def get_reply_like_status(
    *,
    db: Session = Depends(deps.get_db),
    reply_uuid: str,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    获取用户对回复的点赞状态
    """
    reply = crud_showcase_comment_reply.get_showcase_comment_reply_by_uuid(db=db, uuid=reply_uuid)
    if not reply:
        return NotFound(message="Reply not found")
    
    like = crud_showcase_comment_reply_like.get_reply_like(
        db=db, user_id=current_user.id, reply_id=reply.id
    )
    
    return Success(data={"liked": like is not None})