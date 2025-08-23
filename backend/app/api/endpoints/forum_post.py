from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api import deps
from app.crud import crud_forum_post, crud_forum_category
from app.models import User
from app.schemas.forum_post import (
    ForumPostCreate,
    ForumPostUpdate,
    ForumPostResponse,
    ForumPostListResponse,
    PaginatedForumPostResponse
)
from app.utils.response import Success, NotFound, BadRequest, Forbidden

router = APIRouter()

# 管理员路由
admin_router = APIRouter()


@router.get("/", response_model=PaginatedForumPostResponse)
def read_forum_posts(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = Query(None),  # 改为字符串类型接受UUID
    title: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    获取论坛帖子列表
    """
    # 如果提供了category_id（UUID），转换为数据库ID
    db_category_id = None
    if category_id:
        category = crud_forum_category.get_forum_category_by_uuid(db=db, uuid=category_id)
        if not category:
            return BadRequest(message="Invalid category")
        db_category_id = category.id
    
    total, posts = crud_forum_post.get_multi(
        db,
        skip=skip,
        limit=limit,
        category_id=db_category_id,
        title=title,
        start_time=start_time,
        end_time=end_time
    )
    return Success(data={"total": total, "items": [ForumPostListResponse.from_orm(p).model_dump() for p in posts]})


@router.get("/hot")
def read_hot_posts(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
):
    """
    获取热门帖子
    """
    posts = crud_forum_post.get_hot_posts(db, limit=limit, days=days)
    return Success(data=[ForumPostListResponse.from_orm(p).model_dump() for p in posts])


@router.get("/{uuid}")
def read_forum_post(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    获取论坛帖子详情
    """
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    # 增加浏览数
    crud_forum_post.increment_view_count(db=db, db_obj=post)
    
    return Success(data=ForumPostResponse.from_orm(post).model_dump())


@router.post("/")
def create_forum_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: ForumPostCreate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    创建论坛帖子
    """
    # 验证分类是否存在且活跃
    category = crud_forum_category.get_forum_category_by_id(db=db, category_id=post_in.category_id)
    if not category or not category.is_active:
        return BadRequest(message="Invalid or inactive category")
    
    # 检查标题是否重复
    existing_post = crud_forum_post.get_by_title(db=db, title=post_in.title, category_id=post_in.category_id)
    if existing_post:
        return BadRequest(message="Post with this title already exists in this category")
        
    post = crud_forum_post.create_forum_post(db=db, post_in=post_in, user_id=current_user.id)
    return Success(data=ForumPostResponse.from_orm(post).model_dump())


@router.put("/{uuid}")
def update_forum_post(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    post_in: ForumPostUpdate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    更新论坛帖子
    """
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    # 检查权限：只有作者或管理员可以编辑
    if post.user_id != current_user.id and current_user.role not in ["manager", "teacher"]:
        return Forbidden(message="Not enough permissions")
    
    # 检查帖子是否被锁定
    if post.is_locked and current_user.role not in ["manager", "teacher"]:
        return Forbidden(message="Post is locked")
    
    # 如果更改分类，验证新分类
    if post_in.category_id and post_in.category_id != post.category_id:
        category = crud_forum_category.get_forum_category_by_id(db=db, category_id=post_in.category_id)
        if not category or not category.is_active:
            return BadRequest(message="Invalid or inactive category")
    
    post = crud_forum_post.update_forum_post(db=db, db_obj=post, obj_in=post_in)
    return Success(data=ForumPostResponse.from_orm(post).model_dump())


@router.delete("/{uuid}")
def delete_forum_post(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    删除论坛帖子
    """
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    # 检查权限：只有作者或管理员可以删除
    if post.user_id != current_user.id and current_user.role not in ["manager", "teacher"]:
        return Forbidden(message="Not enough permissions")
    
    post = crud_forum_post.remove_forum_post(db=db, db_obj=post)
    return Success(data=ForumPostResponse.from_orm(post).model_dump())


# 管理员 API
@admin_router.get("/")
def read_forum_posts_admin(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    title: Optional[str] = Query(None),
    is_pinned: Optional[bool] = Query(None),
    is_locked: Optional[bool] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    获取论坛帖子列表 (管理员)
    """
    total, posts = crud_forum_post.get_multi(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        user_id=user_id,
        title=title,
        is_pinned=is_pinned,
        is_locked=is_locked,
        start_time=start_time,
        end_time=end_time
    )
    return Success(data={"total": total, "items": [ForumPostListResponse.from_orm(p).model_dump() for p in posts]})


@admin_router.post("/{uuid}/pin")
def pin_forum_post_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    pinned: bool = Query(...),
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    置顶/取消置顶帖子 (管理员)
    """
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    post = crud_forum_post.pin_post(db=db, db_obj=post, pinned=pinned)
    return Success(data=ForumPostResponse.from_orm(post).model_dump())


@admin_router.post("/{uuid}/lock")
def lock_forum_post_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    locked: bool = Query(...),
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    锁定/解锁帖子 (管理员)
    """
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    post = crud_forum_post.lock_post(db=db, db_obj=post, locked=locked)
    return Success(data=ForumPostResponse.from_orm(post).model_dump())


@admin_router.delete("/{uuid}")
def delete_forum_post_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    删除论坛帖子 (管理员)
    """
    post = crud_forum_post.get_forum_post_by_uuid(db=db, uuid=uuid)
    if not post:
        return NotFound(message="Forum post not found")
    
    post = crud_forum_post.remove_forum_post(db=db, db_obj=post)
    return Success(data=ForumPostResponse.from_orm(post).model_dump())