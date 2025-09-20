-- Migration: add sort_order to course_resources (global)
-- Up
ALTER TABLE course_resources
  ADD COLUMN sort_order INT NULL DEFAULT NULL AFTER status;

-- Down (rollback)
-- ALTER TABLE course_resources
--   DROP COLUMN sort_order;

-- Notes:
-- - Use NULL as default to indicate "no priority"; NULL rows are ordered last
-- - Effective order: non-NULL first (ASC), then by numeric ASC, then created_at DESC
