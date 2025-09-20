-- Migration: add repost fields to course_resources
-- Up
ALTER TABLE course_resources
  ADD COLUMN is_repost TINYINT(1) NOT NULL DEFAULT 0 AFTER resource_url,
  ADD COLUMN source_platform VARCHAR(50) NULL AFTER is_repost;

-- Down (rollback)
-- ALTER TABLE course_resources
--   DROP COLUMN source_platform,
--   DROP COLUMN is_repost;

-- Notes:
-- - Keep resource_url NOT NULL; for repost videos, store the original video URL here
-- - Existing rows default to is_repost=0 (original content)
