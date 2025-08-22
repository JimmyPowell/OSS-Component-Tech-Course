# 论坛讨论系统实现文档

## 项目概述
基于现有作品展示系统，扩展实现完整的论坛讨论功能，包括作品评论优化和独立讨论区模块。

## 实现阶段规划

### 第一阶段：数据库设计与后端基础 ✅
#### 1.1 数据库表设计 ✅
- [x] 创建 forum_categories 表 (论坛分类)
- [x] 创建 forum_posts 表 (论坛帖子)
- [x] 创建 forum_replies 表 (帖子回复)
- [x] 优化现有 showcase_comments 表索引
- [x] 添加必要的外键约束和索引

#### 1.2 后端模型创建 ✅
- [x] 创建 ForumCategory 模型
- [x] 创建 ForumPost 模型  
- [x] 创建 ForumReply 模型
- [x] 建立模型关联关系
- [x] 创建相应的 Pydantic schemas

#### 1.3 CRUD 操作实现 ✅
- [x] 实现 forum_category CRUD
- [x] 实现 forum_post CRUD
- [x] 实现 forum_reply CRUD
- [x] 添加分页、搜索、排序功能
- [x] 实现软删除和状态管理

#### 1.4 API 端点开发 ✅
- [x] 论坛分类管理 API
- [x] 帖子管理 API (CRUD + 置顶/锁定)
- [x] 回复管理 API (支持楼中楼)
- [x] 统计信息 API (回复数、浏览数等)
- [x] 管理员专用 API

### 第二阶段：前端基础框架 ⏳
#### 2.1 路由配置 ⏳
- [ ] 添加论坛相关路由
- [ ] 配置嵌套路由结构
- [ ] 实现路由守卫和权限控制

#### 2.2 基础组件开发 ⏳
- [ ] ForumCategoryList (分类列表)
- [ ] ForumPostList (帖子列表)
- [ ] ForumPostDetail (帖子详情)
- [ ] ForumReplyList (回复列表)
- [ ] ForumEditor (发帖/回复编辑器)

#### 2.3 状态管理 ⏳
- [ ] 论坛数据状态管理
- [ ] 用户权限状态管理
- [ ] 实时更新机制

### 第三阶段：管理后台扩展 ⏳
#### 3.1 论坛分类管理 ⏳
- [ ] ForumCategoryManagement 组件
- [ ] 分类的增删改查界面
- [ ] 分类排序和状态管理

#### 3.2 论坛内容管理 ⏳
- [ ] ForumPostManagement 组件
- [ ] 帖子审核和管理界面
- [ ] 批量操作功能

#### 3.3 内容审核系统 ⏳
- [ ] 举报内容管理
- [ ] 敏感词过滤配置
- [ ] 用户行为监控

### 第四阶段：用户界面开发 ⏳
#### 4.1 论坛首页 ⏳
- [ ] 分类展示界面
- [ ] 热门帖子推荐
- [ ] 最新动态展示

#### 4.2 帖子功能 ⏳
- [ ] 发帖界面 (富文本编辑器)
- [ ] 帖子详情页
- [ ] 帖子搜索和筛选

#### 4.3 回复功能 ⏳
- [ ] 楼中楼回复界面
- [ ] @用户功能
- [ ] 回复通知系统

### 第五阶段：功能优化与完善 ⏳
#### 5.1 用户体验优化 ⏳
- [ ] 无限滚动加载
- [ ] 实时消息推送
- [ ] 移动端适配

#### 5.2 性能优化 ⏳
- [ ] 数据缓存机制
- [ ] 图片懒加载
- [ ] API 请求优化

#### 5.3 安全功能 ⏳
- [ ] 内容安全过滤
- [ ] 防刷屏机制
- [ ] 权限细化控制

## 数据库设计详情

### 论坛分类表 (forum_categories)
```sql
CREATE TABLE forum_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    post_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 论坛帖子表 (forum_posts)
```sql
CREATE TABLE forum_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    category_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    last_reply_at DATETIME,
    last_reply_user_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES forum_categories(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (last_reply_user_id) REFERENCES users(id)
);
```

### 论坛回复表 (forum_replies)
```sql
CREATE TABLE forum_replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    parent_id INTEGER,
    content TEXT NOT NULL,
    reply_to_user_id INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE,
    floor_number INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES forum_replies(id),
    FOREIGN KEY (reply_to_user_id) REFERENCES users(id)
);
```

## API 接口设计

### 论坛分类 API
- `GET /api/v1/forum/categories` - 获取分类列表
- `POST /api/v1/forum/categories` - 创建分类 (管理员)
- `PUT /api/v1/forum/categories/{id}` - 更新分类 (管理员)
- `DELETE /api/v1/forum/categories/{id}` - 删除分类 (管理员)

### 论坛帖子 API
- `GET /api/v1/forum/posts` - 获取帖子列表
- `GET /api/v1/forum/posts/{uuid}` - 获取帖子详情
- `POST /api/v1/forum/posts` - 发布帖子
- `PUT /api/v1/forum/posts/{uuid}` - 更新帖子
- `DELETE /api/v1/forum/posts/{uuid}` - 删除帖子
- `POST /api/v1/forum/posts/{uuid}/pin` - 置顶帖子 (管理员)

### 论坛回复 API
- `GET /api/v1/forum/replies/post/{post_uuid}` - 获取帖子回复
- `POST /api/v1/forum/replies` - 发布回复
- `PUT /api/v1/forum/replies/{uuid}` - 更新回复
- `DELETE /api/v1/forum/replies/{uuid}` - 删除回复

## 前端路由设计
```javascript
/forum                          # 论坛首页
/forum/category/:id             # 分类帖子列表  
/forum/category/:id/post/:uuid  # 帖子详情页
/forum/category/:id/new         # 发布新帖
/forum/search                   # 搜索结果页
```

## 开发进度追踪

### 当前状态：第一阶段完成 ✅
- ✅ 数据库表设计完成
- ✅ 后端模型创建完成
- ✅ CRUD 操作实现完成
- ✅ API 端点开发完成

### 完成项目列表
✅ **第一阶段：数据库设计与后端基础**
- 论坛分类、帖子、回复三大核心表设计
- SQLAlchemy 模型和关联关系
- 完整的 CRUD 操作实现
- RESTful API 端点和管理员权限控制

### 下一步计划
开始第二阶段：前端基础框架开发

---

**最后更新时间：** 2025-08-18  
**当前阶段：** 第二阶段 - 前端基础框架  
**整体进度：** 25% (第一阶段完成)