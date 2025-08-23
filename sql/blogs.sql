-- Blog功能相关数据表
-- 创建日期: 2025-08-23
-- 描述: 开源技术Blog系统的数据库表结构

-- Blog文章表
CREATE TABLE blogs (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL UNIQUE DEFAULT (UUID()),
    title VARCHAR(255) NOT NULL COMMENT '文章标题',
    content TEXT NOT NULL COMMENT '文章内容(支持Markdown)',
    summary TEXT COMMENT '文章摘要',
    author_id INT UNSIGNED NOT NULL COMMENT '作者ID',
    cover_url VARCHAR(500) COMMENT '封面图片URL',
    view_count INT UNSIGNED DEFAULT 0 COMMENT '浏览次数',
    like_count INT UNSIGNED DEFAULT 0 COMMENT '点赞次数',
    status ENUM('draft', 'published', 'archived') DEFAULT 'published' COMMENT '状态:草稿/已发布/已归档',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '软删除标记',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_uuid (uuid),
    INDEX idx_author (author_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at),
    INDEX idx_published (status, created_at)
) COMMENT = 'Blog文章表';

-- Blog标签表
CREATE TABLE blog_tags (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '标签名称',
    color VARCHAR(7) DEFAULT '#2196F3' COMMENT '标签颜色(HEX)',
    description TEXT COMMENT '标签描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_name (name)
) COMMENT = 'Blog标签表';

-- Blog文章标签关联表
CREATE TABLE blog_tag_relations (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    blog_id INT UNSIGNED NOT NULL,
    tag_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (blog_id) REFERENCES blogs(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES blog_tags(id) ON DELETE CASCADE,
    UNIQUE KEY unique_blog_tag (blog_id, tag_id),
    INDEX idx_blog (blog_id),
    INDEX idx_tag (tag_id)
) COMMENT = 'Blog文章标签关联表';

-- 插入一些示例数据
INSERT INTO blog_tags (name, color, description) VALUES
('Java', '#f89820', 'Java相关技术文章'),
('Python', '#3776ab', 'Python开发技术'),
('JavaScript', '#f7df1e', 'JavaScript和前端技术'),
('开源框架', '#28a745', '各种开源框架介绍'),
('DevOps', '#326ce5', '运维和部署相关'),
('数据库', '#dc382d', '数据库技术和优化'),
('算法', '#6f42c1', '算法和数据结构');

-- 插入一些示例Blog文章 (假设存在author_id为1的用户)
INSERT INTO blogs (title, content, summary, author_id, cover_url, view_count, like_count, status) VALUES
('GitHub 趋势榜 - 实时热门项目和开发者追踪', 
 '# GitHub 趋势榜介绍\n\nGitHub 趋势榜是开发者追踪实时热门项目和开发者的重要工具...\n\n## 主要功能\n\n1. **热门项目追踪**：实时展示GitHub上最受关注的项目\n2. **开发者排行**：展示活跃的开发者和他们的贡献\n3. **技术趋势分析**：通过数据分析展示技术发展趋势\n\n## 使用方法\n\n访问GitHub Trending页面，可以按以下维度筛选：\n- 编程语言\n- 时间范围（今天/本周/本月）\n- 项目类型\n\n这个工具对于开发者了解技术趋势、寻找优质开源项目具有重要意义。', 
 'GitHub 趋势榜是开发者追踪实时热门项目和开发者的重要工具，帮助开发者了解技术趋势和发现优质开源项目。', 
 1, '/images/blog2.png', 328, 24, 'published'),

('现代Web开发框架对比：React vs Vue vs Angular', 
 '# 现代Web开发框架对比\n\n在现代前端开发中，React、Vue和Angular是三个最主流的框架...\n\n## React\n\n**优势：**\n- 庞大的生态系统\n- 高度的灵活性\n- 强大的社区支持\n\n**劣势：**\n- 学习曲线较陡峭\n- 需要额外的状态管理库\n\n## Vue\n\n**优势：**\n- 渐进式框架，易于学习\n- 优秀的文档\n- 中文社区活跃\n\n## Angular\n\n**优势：**\n- 完整的框架解决方案\n- TypeScript原生支持\n- 企业级应用支持\n\n## 选择建议\n\n根据项目规模、团队技术栈和业务需求来选择最适合的框架。', 
 '深入对比React、Vue和Angular三大前端框架的优劣势，为开发者选择技术栈提供参考建议。', 
 1, '/images/blog3.png', 156, 18, 'published'),

('容器化部署最佳实践：Docker + Kubernetes完整指南', 
 '# 容器化部署完整指南\n\n容器化技术已经成为现代应用部署的标准...\n\n## Docker基础\n\n### 什么是Docker？\n\nDocker是一个开源的应用容器引擎，让开发者可以打包应用以及依赖包到一个轻量级、可移植的容器中。\n\n### 核心概念\n\n1. **镜像(Image)**：应用的静态表示\n2. **容器(Container)**：镜像的运行实例\n3. **仓库(Repository)**：镜像的集中存储\n\n## Kubernetes集群管理\n\n### 核心组件\n\n- Master节点：集群控制平面\n- Worker节点：运行应用负载\n- etcd：分布式配置存储\n- kubectl：命令行管理工具\n\n### 部署流程\n\n```yaml\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: my-app\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: my-app\n  template:\n    metadata:\n      labels:\n        app: my-app\n    spec:\n      containers:\n      - name: my-app\n        image: my-app:v1.0\n        ports:\n        - containerPort: 8080\n```\n\n## 最佳实践\n\n1. 使用多阶段构建优化镜像大小\n2. 设置合理的资源限制\n3. 实施健康检查和日志管理\n4. 使用配置管理工具\n\n通过合理的容器化策略，可以大大提升应用的可移植性、可扩展性和运维效率。', 
 '详细介绍Docker容器化和Kubernetes集群管理的最佳实践，帮助开发者构建高效的部署流程。', 
 1, '/images/blog2.png', 89, 12, 'published');

-- 为示例文章添加标签关联
INSERT INTO blog_tag_relations (blog_id, tag_id) VALUES
(1, 4), -- GitHub趋势榜 - 开源框架
(2, 3), -- Web框架对比 - JavaScript  
(3, 5), -- 容器化部署 - DevOps
(3, 4); -- 容器化部署 - 开源框架