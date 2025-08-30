-- Migration script to add status field to announcements table
-- Run this script to add status management functionality to announcements

-- Add status column to announcements table
ALTER TABLE announcements ADD COLUMN status ENUM('draft', 'published') NOT NULL DEFAULT 'draft' COMMENT '状态：草稿/已发布';

-- Add indexes for better status filtering performance
CREATE INDEX IF NOT EXISTS idx_announcement_status ON announcements(status);
CREATE INDEX IF NOT EXISTS idx_announcement_publisher ON announcements(publisher_id);  
CREATE INDEX IF NOT EXISTS idx_announcement_published ON announcements(status, created_at);

-- Add table comment
ALTER TABLE announcements COMMENT = '公告表 - 支持状态管理：草稿/已发布';

-- Optional: Update existing announcements to 'published' status
-- Uncomment the following line if you want to publish all existing announcements
-- UPDATE announcements SET status = 'published' WHERE deleted_at IS NULL;