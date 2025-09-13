-- Migrate current database and all its tables to utf8mb4/utf8mb4_unicode_ci
-- Usage: run this script while connected to the target database (USE your_db;)

-- Safety: consider taking a backup first
-- mysqldump --single-transaction --default-character-set=utf8mb4 <db> > backup.sql

SET @old_fk_checks = @@FOREIGN_KEY_CHECKS;
SET FOREIGN_KEY_CHECKS = 0;

-- Make sure session is utf8mb4
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET collation_connection = utf8mb4_unicode_ci;

-- Target database
SET @db = DATABASE();

-- Ensure database default is utf8mb4
SET @sql_db = CONCAT('ALTER DATABASE `', @db, '` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
PREPARE stmt FROM @sql_db; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- In case there are many tables, allow long GROUP_CONCAT
SET SESSION group_concat_max_len = 1000000;

-- Generate ALTERs for all base tables in current DB
SELECT GROUP_CONCAT(
         CONCAT('ALTER TABLE `', TABLE_SCHEMA, '`.`', TABLE_NAME,
                '` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
         SEPARATOR ';\n'
       ) INTO @alter_tables_sql
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = @db AND TABLE_TYPE = 'BASE TABLE';

-- Execute the generated ALTERs
SET @alter_tables_sql = IFNULL(@alter_tables_sql, 'SELECT 1');
PREPARE stmt FROM @alter_tables_sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET FOREIGN_KEY_CHECKS = @old_fk_checks;

-- Optional verification queries:
-- SHOW VARIABLES LIKE 'character_set_%';
-- SHOW VARIABLES LIKE 'collation_%';
-- SELECT TABLE_NAME, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE();

