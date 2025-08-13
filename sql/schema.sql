CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    real_name VARCHAR(50),
    phone_number VARCHAR(20),
    school VARCHAR(100),
    avatar_url VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL
);

-- Indexes for performance
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);

CREATE TABLE course_resources (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    type ENUM('ppt', 'video', 'attachment', 'other') NOT NULL,
    description TEXT NULL,
    creator_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    cover_url VARCHAR(512) NULL,
    resource_url VARCHAR(512) NOT NULL,
    file_size INT UNSIGNED NULL,
    mime_type VARCHAR(100) NULL,
    download_count INT UNSIGNED NOT NULL DEFAULT 0
);

-- Indexes for performance
CREATE INDEX idx_course_resources_type ON course_resources(type);
CREATE INDEX idx_course_resources_creator_id ON course_resources(creator_id);
CREATE INDEX idx_course_resources_deleted_at ON course_resources(deleted_at);
CREATE INDEX idx_course_resources_created_at ON course_resources(created_at);

CREATE TABLE homeworks (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    content LONGTEXT NULL,
    cover_url VARCHAR(512) NULL,
    resource_urls JSON NULL,
    creator_id INT UNSIGNED NOT NULL,
    lasting_time INT UNSIGNED NULL COMMENT 'Lasting time in minutes',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for performance
CREATE INDEX idx_homeworks_creator_id ON homeworks(creator_id);
CREATE INDEX idx_homeworks_deleted_at ON homeworks(deleted_at);

CREATE TABLE showcases (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    summary VARCHAR(512) NULL,
    detailed_introduction LONGTEXT NULL,
    avatar_url VARCHAR(512) NULL,
    project_url VARCHAR(512) NULL,
    author_id INT UNSIGNED NOT NULL,
    tags JSON NULL,
    status ENUM('draft', 'published', 'archived') NOT NULL DEFAULT 'draft',
    views_count INT UNSIGNED NOT NULL DEFAULT 0,
    likes_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for performance
CREATE INDEX idx_showcases_author_id ON showcases(author_id);
CREATE INDEX idx_showcases_status ON showcases(status);
CREATE INDEX idx_showcases_deleted_at ON showcases(deleted_at);

CREATE TABLE showcase_comments (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    showcase_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    content TEXT NOT NULL,
    likes_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for performance
CREATE INDEX idx_showcase_comments_showcase_id ON showcase_comments(showcase_id);
CREATE INDEX idx_showcase_comments_user_id ON showcase_comments(user_id);
CREATE INDEX idx_showcase_comments_deleted_at ON showcase_comments(deleted_at);

CREATE TABLE showcase_comment_replies (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    comment_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    reply_to_user_id INT UNSIGNED NULL,
    content TEXT NOT NULL,
    likes_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for performance
CREATE INDEX idx_showcase_comment_replies_comment_id ON showcase_comment_replies(comment_id);
CREATE INDEX idx_showcase_comment_replies_user_id ON showcase_comment_replies(user_id);
CREATE INDEX idx_showcase_comment_replies_reply_to_user_id ON showcase_comment_replies(reply_to_user_id);
CREATE INDEX idx_showcase_comment_replies_deleted_at ON showcase_comment_replies(deleted_at);
