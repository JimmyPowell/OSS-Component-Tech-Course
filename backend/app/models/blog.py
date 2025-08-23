from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import enum


class BlogStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    title = Column(String(255), nullable=False, comment="文章标题")
    content = Column(Text, nullable=False, comment="文章内容(支持Markdown)")
    summary = Column(Text, comment="文章摘要")
    author_id = Column(INTEGER(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cover_url = Column(String(500), comment="封面图片URL")
    view_count = Column(INTEGER(unsigned=True), default=0, comment="浏览次数")
    like_count = Column(INTEGER(unsigned=True), default=0, comment="点赞次数")
    status = Column(
        Enum(BlogStatus), 
        default=BlogStatus.published,
        comment="状态:草稿/已发布/已归档"
    )
    is_deleted = Column(Boolean, default=False, comment="软删除标记")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    author = relationship("User", back_populates="blogs")
    tag_relations = relationship("BlogTagRelation", back_populates="blog", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_blog_author', 'author_id'),
        Index('idx_blog_status', 'status'),
        Index('idx_blog_created', 'created_at'),
        Index('idx_blog_published', 'status', 'created_at'),
        {'comment': 'Blog文章表'}
    )

    @property
    def tags(self):
        """获取文章的所有标签"""
        return [relation.tag for relation in self.tag_relations if relation.tag]


class BlogTag(Base):
    __tablename__ = "blog_tags"

    id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="标签名称")
    color = Column(String(7), default="#2196F3", comment="标签颜色(HEX)")
    description = Column(Text, comment="标签描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    blog_relations = relationship("BlogTagRelation", back_populates="tag", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_blog_tag_name', 'name'),
        {'comment': 'Blog标签表'}
    )

    @property
    def blog_count(self):
        """获取使用此标签的博客数量"""
        return len([relation for relation in self.blog_relations if relation.blog and not relation.blog.is_deleted])


class BlogTagRelation(Base):
    __tablename__ = "blog_tag_relations"

    id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    blog_id = Column(INTEGER(unsigned=True), ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(INTEGER(unsigned=True), ForeignKey("blog_tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    blog = relationship("Blog", back_populates="tag_relations")
    tag = relationship("BlogTag", back_populates="blog_relations")

    # 索引和约束
    __table_args__ = (
        Index('idx_blog_tag_relation_blog', 'blog_id'),
        Index('idx_blog_tag_relation_tag', 'tag_id'),
        Index('unique_blog_tag', 'blog_id', 'tag_id', unique=True),
        {'comment': 'Blog文章标签关联表'}
    )