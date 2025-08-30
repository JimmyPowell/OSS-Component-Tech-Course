-- 作品状态重构迁移脚本
-- 将8个状态简化为5个状态，并添加previous_status字段

-- 1. 添加previous_status字段
ALTER TABLE showcases ADD COLUMN previous_status VARCHAR(20) NULL AFTER status;

-- 2. 更新现有状态映射
UPDATE showcases SET status = 'pending' WHERE status = 'pending_review';
UPDATE showcases SET status = 'reject' WHERE status = 'rejected';
UPDATE showcases SET status = 'published' WHERE status = 'approved';
UPDATE showcases SET status = 'excellent' WHERE status = 'featured';
-- excellent状态保持不变
-- draft状态保持不变
-- published状态保持不变

-- archived状态映射为draft
UPDATE showcases SET status = 'draft' WHERE status = 'archived';

-- 3. 修改status字段的枚举类型
ALTER TABLE showcases MODIFY COLUMN status ENUM('draft', 'pending', 'published', 'reject', 'excellent') NOT NULL DEFAULT 'draft';

-- 4. 为了测试前端显示，将现有的published状态作品设为excellent
-- 注意：这是为了测试，实际使用时可能需要管理员手动操作
UPDATE showcases SET status = 'excellent' WHERE status = 'published' LIMIT 1;