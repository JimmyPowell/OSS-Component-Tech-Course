from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api import deps
from app.crud import crud_forum_category
from app.models import User
from app.schemas.forum_category import (
    ForumCategoryCreate,
    ForumCategoryUpdate,
    ForumCategoryResponse,
    PaginatedForumCategoryResponse
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()

# 管理员路由
admin_router = APIRouter()


@router.get("/", response_model=PaginatedForumCategoryResponse)
def read_forum_categories(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """
    获取论坛分类列表
    """
    total, categories = crud_forum_category.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        is_active=is_active,
        include_inactive=is_active is None
    )
    return Success(data={"total": total, "items": [ForumCategoryResponse.from_orm(c).model_dump() for c in categories]})


@router.get("/active")
def read_active_categories(db: Session = Depends(deps.get_db)):
    """
    获取所有激活的分类
    """
    categories = crud_forum_category.get_active_categories(db)
    return Success(data=[ForumCategoryResponse.from_orm(c).model_dump() for c in categories])


@router.get("/{uuid}")
def read_forum_category(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    获取论坛分类详情
    """
    category = crud_forum_category.get_forum_category_by_uuid(db=db, uuid=uuid)
    if not category:
        return NotFound(message="Forum category not found")
    return Success(data=ForumCategoryResponse.from_orm(category).model_dump())


# 管理员 API
@admin_router.post("/")
def create_forum_category_admin(
    *,
    db: Session = Depends(deps.get_db),
    category_in: ForumCategoryCreate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    创建论坛分类 (管理员)
    """
    existing_category = crud_forum_category.get_by_name(db=db, name=category_in.name)
    if existing_category:
        return BadRequest(message="Category with this name already exists.")
        
    category = crud_forum_category.create_forum_category(db=db, category_in=category_in)
    return Success(data=ForumCategoryResponse.from_orm(category).model_dump())


@admin_router.get("/")
def read_forum_categories_admin(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """
    获取论坛分类列表 (管理员)
    """
    total, categories = crud_forum_category.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        is_active=is_active,
        include_inactive=True  # 管理员可以看到所有分类
    )
    return Success(data={"total": total, "items": [ForumCategoryResponse.from_orm(c).model_dump() for c in categories]})


@admin_router.get("/{uuid}")
def read_forum_category_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    获取论坛分类详情 (管理员)
    """
    category = crud_forum_category.get_forum_category_by_uuid(db=db, uuid=uuid)
    if not category:
        return NotFound(message="Forum category not found")
    return Success(data=ForumCategoryResponse.from_orm(category).model_dump())


@admin_router.put("/{uuid}")
def update_forum_category_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    category_in: ForumCategoryUpdate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    更新论坛分类 (管理员)
    """
    category = crud_forum_category.get_forum_category_by_uuid(db=db, uuid=uuid)
    if not category:
        return NotFound(message="Forum category not found")
    
    # 检查名称是否重复
    if category_in.name and category_in.name != category.name:
        existing_category = crud_forum_category.get_by_name(db=db, name=category_in.name)
        if existing_category:
            return BadRequest(message="Category with this name already exists.")
    
    category = crud_forum_category.update_forum_category(db=db, db_obj=category, obj_in=category_in)
    return Success(data=ForumCategoryResponse.from_orm(category).model_dump())


@admin_router.delete("/{uuid}")
def delete_forum_category_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    删除论坛分类 (管理员)
    """
    category = crud_forum_category.get_forum_category_by_uuid(db=db, uuid=uuid)
    if not category:
        return NotFound(message="Forum category not found")
    
    # 检查是否有帖子，如果有则不允许删除
    if category.post_count > 0:
        return BadRequest(message="Cannot delete category that contains posts")
    
    category = crud_forum_category.remove_forum_category(db=db, db_obj=category)
    return Success(data=ForumCategoryResponse.from_orm(category).model_dump())