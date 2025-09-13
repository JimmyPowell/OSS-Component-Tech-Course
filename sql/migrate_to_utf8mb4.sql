-- Migrate current database and all its tables to utf8mb4/utf8mb4_unicode_ci
-- Usage: connect to your target DB (USE your_db;) then run this script.
-- If your client does not support multiple statements, run blocks separately.

-- Safety: make a backup first
-- mysqldump --single-transaction --default-character-set=utf8mb4 <db> > backup.sql

-- Session charset
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET collation_connection = utf8mb4_unicode_ci;

-- Suggest the database-level ALTER (run manually once; PREPARE doesn't support it)
SELECT CONCAT('ALTER DATABASE `', DATABASE(), '` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;') AS suggested_alter_database;

-- Procedure to iterate and convert every table
DELIMITER $$
DROP PROCEDURE IF EXISTS migrate_to_utf8mb4 $$
CREATE PROCEDURE migrate_to_utf8mb4(IN db_name VARCHAR(64))
BEGIN
  DECLARE done INT DEFAULT 0;
  DECLARE tbl VARCHAR(64);
  DECLARE cur CURSOR FOR
    SELECT TABLE_NAME FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = db_name AND TABLE_TYPE = 'BASE TABLE';
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  SET @old_fk = @@FOREIGN_KEY_CHECKS;
  SET FOREIGN_KEY_CHECKS = 0;

  OPEN cur;
  read_loop: LOOP
    FETCH cur INTO tbl;
    IF done = 1 THEN
      LEAVE read_loop;
    END IF;
    SET @s = CONCAT('ALTER TABLE `', db_name, '`.`', tbl, '` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
    PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;
  END LOOP;
  CLOSE cur;

  SET FOREIGN_KEY_CHECKS = @old_fk;
END $$
DELIMITER ;

-- Execute for current database
CALL migrate_to_utf8mb4(DATABASE());

-- Verification helpers
-- SHOW VARIABLES LIKE 'character_set_%';
-- SHOW VARIABLES LIKE 'collation_%';
-- SELECT TABLE_NAME, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE();
