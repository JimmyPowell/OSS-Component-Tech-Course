-- Migration: add summary column to course_resources
-- Purpose: support short summaries for list views

ALTER TABLE course_resources
  ADD COLUMN summary VARCHAR(512) NULL AFTER name;

-- Optional backfill example (uncomment if needed):
-- UPDATE course_resources SET summary = LEFT(description, 200)
-- WHERE summary IS NULL AND description IS NOT NULL;

