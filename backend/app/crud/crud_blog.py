from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from app.crud.base import CRUDBase
from app.models.blog import Blog, BlogTag, BlogTagRelation, BlogStatus
from app.schemas.blog import (
    BlogCreate, BlogUpdate, BlogSearchRequest,
    BlogTagCreate, BlogTagUpdate
)
from uuid import uuid4


class CRUDBlog(CRUDBase[Blog, BlogCreate, BlogUpdate]):
    def create_with_tags(self, db: Session, *, obj_in: BlogCreate) -> Blog:
        """创建Blog文章并关联标签"""
        # 生成UUID
        blog_uuid = str(uuid4())
        
        # 创建Blog对象
        db_obj = Blog(
            uuid=blog_uuid,
            title=obj_in.title,
            content=obj_in.content,
            summary=obj_in.summary,
            author_id=obj_in.author_id,
            cover_url=obj_in.cover_url,
            status=obj_in.status
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 关联标签
        if obj_in.tag_ids:
            for tag_id in obj_in.tag_ids:
                tag_relation = BlogTagRelation(
                    blog_id=db_obj.id,
                    tag_id=tag_id
                )
                db.add(tag_relation)
            db.commit()
            db.refresh(db_obj)
        
        return db_obj

    def update_with_tags(self, db: Session, *, db_obj: Blog, obj_in: BlogUpdate) -> Blog:
        """更新Blog文章并更新标签关联"""
        # 更新基本信息
        update_data = obj_in.dict(exclude_unset=True, exclude={"tag_ids"})
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # 更新标签关联
        if obj_in.tag_ids is not None:
            # 删除现有关联
            db.query(BlogTagRelation).filter(
                BlogTagRelation.blog_id == db_obj.id
            ).delete()
            
            # 创建新关联
            for tag_id in obj_in.tag_ids:
                tag_relation = BlogTagRelation(
                    blog_id=db_obj.id,
                    tag_id=tag_id
                )
                db.add(tag_relation)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_uuid(self, db: Session, *, uuid: str) -> Optional[Blog]:
        """根据UUID获取Blog"""
        return db.query(Blog).filter(
            and_(Blog.uuid == uuid, Blog.is_deleted == False)
        ).first()

    def get_published(
        self, db: Session, *, skip: int = 0, limit: int = 10
    ) -> List[Blog]:
        """获取已发布的Blog列表"""
        return db.query(Blog).filter(
            and_(
                Blog.status == BlogStatus.published,
                Blog.is_deleted == False
            )
        ).order_by(desc(Blog.created_at)).offset(skip).limit(limit).all()

    def get_by_author(
        self, db: Session, *, author_id: int, skip: int = 0, limit: int = 10
    ) -> List[Blog]:
        """获取指定作者的Blog列表"""
        return db.query(Blog).filter(
            and_(
                Blog.author_id == author_id,
                Blog.is_deleted == False
            )
        ).order_by(desc(Blog.created_at)).offset(skip).limit(limit).all()

    def search(
        self, db: Session, *, search_params: BlogSearchRequest, admin_access: bool = False
    ) -> tuple[List[Blog], int]:
        """搜索Blog文章"""
        query = db.query(Blog).filter(Blog.is_deleted == False)
        
        # 状态筛选
        if search_params.status:
            query = query.filter(Blog.status == search_params.status)
        elif not admin_access:
            # 非管理员访问时，默认只显示已发布的博客
            query = query.filter(Blog.status == BlogStatus.published)
        
        # 作者筛选
        if search_params.author_id:
            query = query.filter(Blog.author_id == search_params.author_id)
        
        # 关键词搜索
        if search_params.keyword:
            keyword = f"%{search_params.keyword}%"
            query = query.filter(
                or_(
                    Blog.title.like(keyword),
                    Blog.summary.like(keyword)
                )
            )
        
        # 标签筛选
        if search_params.tag_ids:
            query = query.join(BlogTagRelation).filter(
                BlogTagRelation.tag_id.in_(search_params.tag_ids)
            ).distinct()
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        blogs = query.order_by(desc(Blog.created_at)).offset(
            (search_params.page - 1) * search_params.size
        ).limit(search_params.size).all()
        
        return blogs, total

    def increment_view_count(self, db: Session, *, blog_id: int, increment: int = 1) -> Blog:
        """增加Blog浏览次数"""
        db_obj = db.query(Blog).filter(Blog.id == blog_id).first()
        if db_obj:
            db_obj.view_count += increment
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, *, id: int) -> Optional[Blog]:
        """软删除Blog"""
        db_obj = db.query(Blog).filter(Blog.id == id).first()
        if db_obj:
            db_obj.is_deleted = True
            db.commit()
            db.refresh(db_obj)
        return db_obj


class CRUDBlogTag(CRUDBase[BlogTag, BlogTagCreate, BlogTagUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[BlogTag]:
        """根据名称获取标签"""
        return db.query(BlogTag).filter(BlogTag.name == name).first()

    def get_popular_tags(self, db: Session, *, limit: int = 10) -> List[BlogTag]:
        """获取热门标签（按使用次数排序）"""
        # 使用子查询获取每个标签的使用次数
        from sqlalchemy import func
        
        tag_counts = db.query(
            BlogTag.id,
            func.count(BlogTagRelation.id).label('count')
        ).join(
            BlogTagRelation, BlogTag.id == BlogTagRelation.tag_id
        ).join(
            Blog, BlogTagRelation.blog_id == Blog.id
        ).filter(
            and_(Blog.is_deleted == False, Blog.status == BlogStatus.published)
        ).group_by(BlogTag.id).subquery()
        
        # 获取标签及其使用次数
        return db.query(BlogTag).join(
            tag_counts, BlogTag.id == tag_counts.c.id
        ).order_by(desc(tag_counts.c.count)).limit(limit).all()


# 创建CRUD实例
crud_blog = CRUDBlog(Blog)
crud_blog_tag = CRUDBlogTag(BlogTag)