-- 为作业表添加状态字段
-- 状态类型：draft(未发布)、published(已发布)
-- 默认状态为draft(未发布)

ALTER TABLE homeworks 
ADD COLUMN status ENUM('draft', 'published') 
NOT NULL DEFAULT 'draft' 
AFTER lasting_time;

-- 创建状态索引以优化查询性能
CREATE INDEX idx_homeworks_status ON homeworks(status);

-- 创建复合索引：状态+删除时间（用于查询已发布且未删除的作业）
CREATE INDEX idx_homeworks_status_deleted ON homeworks(status, deleted_at);

-- 更新现有数据：将所有现有作业设置为已发布状态
UPDATE homeworks SET status = 'published' WHERE deleted_at IS NULL;