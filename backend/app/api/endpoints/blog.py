from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_blog import crud_blog, crud_blog_tag
from app.models.user import User
from app.schemas.blog import (
    Blog,
    BlogCreate,
    BlogUpdate,
    BlogDetail,
    BlogSummary,
    BlogListResponse,
    BlogSearchRequest,
    BlogViewUpdate,
    BlogTag,
    BlogTagCreate,
    BlogTagUpdate
)
from app.utils.response import success_response, error_response
import math

router = APIRouter()


# Blog标签相关API
@router.get("/tags", response_model=List[BlogTag])
def get_blog_tags(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=100, le=100)
) -> Any:
    """获取所有Blog标签"""
    tags = crud_blog_tag.get_multi(db, skip=skip, limit=limit)
    return success_response(data=tags)


@router.get("/tags/popular", response_model=List[BlogTag])
def get_popular_tags(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(default=10, le=20)
) -> Any:
    """获取热门标签"""
    tags = crud_blog_tag.get_popular_tags(db, limit=limit)
    return success_response(data=tags)


@router.post("/tags", response_model=BlogTag)
def create_blog_tag(
    *,
    db: Session = Depends(deps.get_db),
    tag_in: BlogTagCreate,
    current_user: User = Depends(deps.get_current_user_obj)
) -> Any:
    """创建Blog标签 (需要管理员权限)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限创建标签"
        )
    
    # 检查标签是否已存在
    existing_tag = crud_blog_tag.get_by_name(db, name=tag_in.name)
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名称已存在"
        )
    
    tag = crud_blog_tag.create(db=db, obj_in=tag_in)
    return success_response(data=tag)


# Blog文章相关API
@router.get("/search", response_model=BlogListResponse)
def search_blogs(
    *,
    db: Session = Depends(deps.get_db),
    keyword: str = Query(None, description="搜索关键词"),
    tag_ids: List[int] = Query([], description="标签ID列表"),
    author_id: int = Query(None, description="作者ID"),
    status: Optional[str] = Query(None, description="文章状态"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小")
) -> Any:
    """搜索Blog文章"""
    search_params = BlogSearchRequest(
        keyword=keyword,
        tag_ids=tag_ids,
        author_id=author_id,
        status=status,
        page=page,
        size=size
    )
    
    # 用户端搜索，只显示已发布的博客
    blogs, total = crud_blog.search(db, search_params=search_params, admin_access=False)
    
    # 转换为摘要格式
    blog_summaries = []
    for blog in blogs:
        summary = BlogSummary(
            id=blog.id,
            uuid=blog.uuid,
            title=blog.title,
            summary=blog.summary,
            cover_url=blog.cover_url,
            view_count=blog.view_count,
            like_count=blog.like_count,
            status=blog.status,  # 添加状态字段
            created_at=blog.created_at,
            author={
                "id": blog.author.id,
                "uuid": blog.author.uuid,
                "username": blog.author.username,
                "real_name": blog.author.real_name,
                "avatar_url": blog.author.avatar_url
            } if blog.author else None,
            tags=[{
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description,
                "created_at": tag.created_at,
                "blog_count": tag.blog_count
            } for tag in blog.tags] if blog.tags else []
        )
        blog_summaries.append(summary)
    
    response_data = BlogListResponse(
        items=blog_summaries,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if size > 0 else 0
    )
    
    return success_response(data=response_data)


@router.get("/", response_model=List[BlogSummary])
def get_blogs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = Query(default=10, le=50)
) -> Any:
    """获取Blog列表（仅已发布）"""
    blogs = crud_blog.get_published(db, skip=skip, limit=limit)
    
    # 转换为摘要格式
    blog_summaries = []
    for blog in blogs:
        summary = BlogSummary(
            id=blog.id,
            uuid=blog.uuid,
            title=blog.title,
            summary=blog.summary,
            cover_url=blog.cover_url,
            view_count=blog.view_count,
            like_count=blog.like_count,
            status=blog.status,  # 添加状态字段
            created_at=blog.created_at,
            author={
                "id": blog.author.id,
                "uuid": blog.author.uuid,
                "username": blog.author.username,
                "real_name": blog.author.real_name,
                "avatar_url": blog.author.avatar_url
            } if blog.author else None,
            tags=[{
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description,
                "created_at": tag.created_at,
                "blog_count": tag.blog_count
            } for tag in blog.tags] if blog.tags else []
        )
        blog_summaries.append(summary)
    
    return success_response(data=blog_summaries)


@router.post("/", response_model=Blog)
def create_blog(
    *,
    db: Session = Depends(deps.get_db),
    blog_in: BlogCreate,
    current_user: User = Depends(deps.get_current_user_obj)
) -> Any:
    """创建Blog文章 (需要管理员权限)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限创建Blog文章"
        )
    
    # 设置作者ID为当前用户
    blog_in.author_id = current_user.id
    blog = crud_blog.create_with_tags(db=db, obj_in=blog_in)
    return success_response(data=blog)


@router.get("/{blog_uuid}", response_model=BlogDetail)
def get_blog(
    *,
    db: Session = Depends(deps.get_db),
    blog_uuid: str,
    current_user: User = Depends(deps.get_current_user_obj)
) -> Any:
    """根据UUID获取Blog详情"""
    blog = crud_blog.get_by_uuid(db, uuid=blog_uuid)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog不存在")
    
    # 检查是否为已发布状态（除非是管理员或作者本人）
    if blog.status != "published" and current_user.role != "manager" and blog.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Blog不存在")
    
    return success_response(data=blog)


@router.put("/{blog_uuid}", response_model=Blog)
def update_blog(
    *,
    db: Session = Depends(deps.get_db),
    blog_uuid: str,
    blog_in: BlogUpdate,
    current_user: User = Depends(deps.get_current_user_obj)
) -> Any:
    """更新Blog文章 (需要管理员权限或作者本人)"""
    blog = crud_blog.get_by_uuid(db, uuid=blog_uuid)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog不存在")
    
    # 权限检查
    if current_user.role != "manager" and blog.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此Blog"
        )
    
    blog = crud_blog.update_with_tags(db=db, db_obj=blog, obj_in=blog_in)
    return success_response(data=blog)


@router.delete("/{blog_uuid}")
def delete_blog(
    *,
    db: Session = Depends(deps.get_db),
    blog_uuid: str,
    current_user: User = Depends(deps.get_current_user_obj)
) -> Any:
    """删除Blog文章 (需要管理员权限或作者本人)"""
    blog = crud_blog.get_by_uuid(db, uuid=blog_uuid)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog不存在")
    
    # 权限检查
    if current_user.role != "manager" and blog.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此Blog"
        )
    
    crud_blog.soft_delete(db=db, id=blog.id)
    return success_response(message="Blog删除成功")


@router.put("/{blog_uuid}/view", response_model=Blog)
def update_blog_view(
    *,
    db: Session = Depends(deps.get_db),
    blog_uuid: str,
    view_update: BlogViewUpdate
) -> Any:
    """增加Blog浏览次数"""
    blog = crud_blog.get_by_uuid(db, uuid=blog_uuid)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog不存在")
    
    if blog.status != "published":
        raise HTTPException(status_code=404, detail="Blog不存在")
    
    blog = crud_blog.increment_view_count(db=db, blog_id=blog.id, increment=view_update.increment)
    return success_response(data=blog)


@router.get("/author/{author_id}", response_model=List[BlogSummary])
def get_blogs_by_author(
    *,
    db: Session = Depends(deps.get_db),
    author_id: int,
    skip: int = 0,
    limit: int = Query(default=10, le=50)
) -> Any:
    """获取指定作者的Blog列表"""
    blogs = crud_blog.get_by_author(db, author_id=author_id, skip=skip, limit=limit)
    
    # 转换为摘要格式
    blog_summaries = []
    for blog in blogs:
        if blog.status == "published":  # 只返回已发布的
            summary = BlogSummary(
                id=blog.id,
                uuid=blog.uuid,
                title=blog.title,
                summary=blog.summary,
                cover_url=blog.cover_url,
                view_count=blog.view_count,
                like_count=blog.like_count,
                created_at=blog.created_at,
                author={
                    "id": blog.author.id,
                    "uuid": blog.author.uuid,
                    "username": blog.author.username,
                    "real_name": blog.author.real_name,
                    "avatar_url": blog.author.avatar_url
                } if blog.author else None,
                tags=[{
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "description": tag.description,
                    "created_at": tag.created_at,
                    "blog_count": tag.blog_count
                } for tag in blog.tags] if blog.tags else []
            )
            blog_summaries.append(summary)
    
    return success_response(data=blog_summaries)


@router.get("/admin/search", response_model=BlogListResponse)
def admin_search_blogs(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_obj),
    keyword: str = Query(None, description="搜索关键词"),
    tag_ids: List[int] = Query([], description="标签ID列表"),
    author_id: int = Query(None, description="作者ID"),
    status: Optional[str] = Query(None, description="文章状态"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小")
) -> Any:
    """管理员搜索Blog文章（可查看所有状态）"""
    # 检查管理员权限
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问管理员接口"
        )
    
    search_params = BlogSearchRequest(
        keyword=keyword,
        tag_ids=tag_ids,
        author_id=author_id,
        status=status,
        page=page,
        size=size
    )
    
    # 管理员搜索，可查看所有状态的博客
    blogs, total = crud_blog.search(db, search_params=search_params, admin_access=True)
    
    # 转换为摘要格式
    blog_summaries = []
    for blog in blogs:
        summary = BlogSummary(
            id=blog.id,
            uuid=blog.uuid,
            title=blog.title,
            summary=blog.summary,
            cover_url=blog.cover_url,
            view_count=blog.view_count,
            like_count=blog.like_count,
            status=blog.status,
            created_at=blog.created_at,
            author={
                "id": blog.author.id,
                "uuid": blog.author.uuid,
                "username": blog.author.username,
                "real_name": blog.author.real_name,
                "avatar_url": blog.author.avatar_url
            } if blog.author else None,
            tags=[{
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "description": tag.description,
                "created_at": tag.created_at,
                "blog_count": tag.blog_count
            } for tag in blog.tags] if blog.tags else []
        )
        blog_summaries.append(summary)
    
    response_data = BlogListResponse(
        items=blog_summaries,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if size > 0 else 0
    )
    
    return success_response(data=response_data)