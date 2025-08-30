-- Migration script to extend showcase status enum with new progressive states
-- Run this script to add approved, featured, excellent statuses to showcases table

-- Add new status options to the enum
ALTER TABLE showcases MODIFY COLUMN status ENUM(
    'draft',
    'pending_review', 
    'published',
    'rejected',
    'archived',
    'approved',
    'featured',
    'excellent'
) NOT NULL DEFAULT 'draft' COMMENT '状态：草稿/待审核/已发布/已拒绝/已归档/已入库/精品/优秀';

-- Add indexes for better status filtering performance (only if they don't exist)
CREATE INDEX IF NOT EXISTS idx_showcases_status ON showcases(status);
CREATE INDEX IF NOT EXISTS idx_showcases_status_created ON showcases(status, created_at);

-- Add comment to clarify the progressive workflow
ALTER TABLE showcases COMMENT = '作品展示表 - 支持递进管理：用户提交→审核通过(approved/入库)→精品(featured)→优秀(excellent)';