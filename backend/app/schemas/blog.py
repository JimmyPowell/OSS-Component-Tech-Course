from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BlogStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


# Blog标签相关Schema
class BlogTagBase(BaseModel):
    name: str
    color: Optional[str] = "#2196F3"
    description: Optional[str] = None


class BlogTagCreate(BlogTagBase):
    pass


class BlogTagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class BlogTag(BlogTagBase):
    id: int
    created_at: datetime
    blog_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Blog文章相关Schema
class BlogBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    status: Optional[BlogStatus] = BlogStatus.published


class BlogCreate(BlogBase):
    author_id: int
    tag_ids: Optional[List[int]] = []

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('标题不能为空')
        return v.strip()

    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('内容不能为空')
        return v.strip()


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    status: Optional[BlogStatus] = None
    tag_ids: Optional[List[int]] = None

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('标题不能为空')
        return v.strip() if v else v

    @validator('content')
    def content_must_not_be_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('内容不能为空')
        return v.strip() if v else v


# 用户信息简化Schema（用于Blog中显示作者信息）
class BlogAuthor(BaseModel):
    id: int
    uuid: str
    username: str
    real_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class Blog(BlogBase):
    id: int
    uuid: str
    author_id: int
    view_count: int = 0
    like_count: int = 0
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    author: Optional[BlogAuthor] = None
    tags: Optional[List[BlogTag]] = []

    class Config:
        from_attributes = True


class BlogDetail(Blog):
    """详细的Blog信息，包含完整内容"""
    pass


class BlogSummary(BaseModel):
    """Blog摘要信息，用于列表显示"""
    id: int
    uuid: str
    title: str
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    created_at: datetime
    author: Optional[BlogAuthor] = None
    tags: Optional[List[BlogTag]] = []

    class Config:
        from_attributes = True


# 分页响应Schema
class BlogListResponse(BaseModel):
    items: List[BlogSummary]
    total: int
    page: int
    size: int
    pages: int


# 搜索请求Schema
class BlogSearchRequest(BaseModel):
    keyword: Optional[str] = None
    tag_ids: Optional[List[int]] = []
    author_id: Optional[int] = None
    status: Optional[BlogStatus] = None
    page: Optional[int] = 1
    size: Optional[int] = 10

    @validator('page')
    def page_must_be_positive(cls, v):
        if v is not None and v < 1:
            raise ValueError('页码必须大于0')
        return v

    @validator('size')
    def size_must_be_valid(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError('每页大小必须在1-100之间')
        return v


# 访问量更新Schema
class BlogViewUpdate(BaseModel):
    increment: int = 1

    @validator('increment')
    def increment_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('增量必须为正数')
        return v