from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api import deps
from app.crud import crud_forum_reply, crud_forum_post
from app.models import User
from app.schemas.forum_reply import (
    ForumReplyCreate,
    ForumReplyUpdate,
    ForumReplyResponse,
    ForumReplyWithChildren,
    PaginatedForumReplyResponse
)
from app.utils.response import Success, NotFound, BadRequest, Forbidden

router = APIRouter()

# 管理员路由
admin_router = APIRouter()


@router.get("/post/{post_uuid}")
def read_post_replies(
    *,
    db: Session = Depends(deps.get_db),
    post_uuid: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    parent_id: Optional[int] = Query(None),
):
    """
    获取帖子的回复列表
    """
    # 验证帖子是否存在
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=post_uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    total, replies = crud_forum_reply.get_replies_by_post(
        db,
        post_id=post.id,
        skip=skip,
        limit=limit,
        parent_id=parent_id
    )
    return Success(data={"total": total, "items": [ForumReplyResponse.from_orm(r).model_dump() for r in replies]})


@router.get("/post/{post_uuid}/tree")
def read_post_replies_tree(
    *,
    db: Session = Depends(deps.get_db),
    post_uuid: str,
):
    """
    获取帖子的回复树结构
    """
    # 验证帖子是否存在
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=post_uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    replies = crud_forum_reply.get_replies_tree(db, post_id=post.id)
    
    def build_reply_tree(reply):
        """递归构建回复树"""
        result = ForumReplyWithChildren.from_orm(reply).model_dump()
        if hasattr(reply, 'children'):
            result['children'] = [build_reply_tree(child) for child in reply.children]
        return result
    
    return Success(data=[build_reply_tree(reply) for reply in replies])


@router.get("/{uuid}")
def read_forum_reply(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    获取回复详情
    """
    reply = crud_forum_reply.get_forum_reply_by_uuid(db=db, uuid=uuid)
    if not reply:
        return NotFound(message="Forum reply not found")
    return Success(data=ForumReplyResponse.from_orm(reply).model_dump())


@router.post("/")
def create_forum_reply(
    *,
    db: Session = Depends(deps.get_db),
    reply_in: ForumReplyCreate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    创建论坛回复
    """
    # 验证帖子是否存在且未锁定
    post = crud_forum_post.get_forum_post_by_id(db=db, post_id=reply_in.post_id)
    if not post:
        return BadRequest(message="Forum post not found")
    
    if post.is_locked:
        return Forbidden(message="Post is locked, cannot reply")
    
    # 如果是回复其他回复，验证父回复是否存在
    if reply_in.parent_id:
        parent_reply = crud_forum_reply.get_forum_reply_by_id(db=db, reply_id=reply_in.parent_id)
        if not parent_reply or parent_reply.post_id != reply_in.post_id:
            return BadRequest(message="Invalid parent reply")
        
        # 如果指定了回复对象，设置 reply_to_user_id
        if not reply_in.reply_to_user_id:
            reply_in.reply_to_user_id = parent_reply.user_id
    
    reply = crud_forum_reply.create_forum_reply(db=db, reply_in=reply_in, user_id=current_user.id)
    return Success(data=ForumReplyResponse.from_orm(reply).model_dump())


@router.put("/{uuid}")
def update_forum_reply(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    reply_in: ForumReplyUpdate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    更新论坛回复
    """
    reply = crud_forum_reply.get_forum_reply_by_uuid(db=db, uuid=uuid)
    if not reply:
        return NotFound(message="Forum reply not found")
    
    # 检查权限：只有作者或管理员可以编辑
    if reply.user_id != current_user.id and current_user.role not in ["manager", "teacher"]:
        return Forbidden(message="Not enough permissions")
    
    # 检查帖子是否被锁定
    post = crud_forum_post.get_forum_post_by_id(db=db, post_id=reply.post_id)
    if post and post.is_locked and current_user.role not in ["manager", "teacher"]:
        return Forbidden(message="Post is locked")
    
    reply = crud_forum_reply.update_forum_reply(db=db, db_obj=reply, obj_in=reply_in)
    return Success(data=ForumReplyResponse.from_orm(reply).model_dump())


@router.delete("/{uuid}")
def delete_forum_reply(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    删除论坛回复
    """
    reply = crud_forum_reply.get_forum_reply_by_uuid(db=db, uuid=uuid)
    if not reply:
        return NotFound(message="Forum reply not found")
    
    # 检查权限：只有作者或管理员可以删除
    if reply.user_id != current_user.id and current_user.role not in ["manager", "teacher"]:
        return Forbidden(message="Not enough permissions")
    
    reply = crud_forum_reply.remove_forum_reply(db=db, db_obj=reply)
    return Success(data=ForumReplyResponse.from_orm(reply).model_dump())


@router.get("/user/{user_id}")
def read_user_replies(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    获取用户的回复列表
    """
    total, replies = crud_forum_reply.get_user_replies(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return Success(data={"total": total, "items": [ForumReplyResponse.from_orm(r).model_dump() for r in replies]})


@router.get("/recent")
def read_recent_replies(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """
    获取最新回复
    """
    replies = crud_forum_reply.get_recent_replies(db, limit=limit)
    return Success(data=[ForumReplyResponse.from_orm(r).model_dump() for r in replies])


# 管理员 API
@admin_router.delete("/{uuid}")
def delete_forum_reply_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    删除论坛回复 (管理员)
    """
    reply = crud_forum_reply.get_forum_reply_by_uuid(db=db, uuid=uuid)
    if not reply:
        return NotFound(message="Forum reply not found")
    
    reply = crud_forum_reply.remove_forum_reply(db=db, db_obj=reply)
    return Success(data=ForumReplyResponse.from_orm(reply).model_dump())