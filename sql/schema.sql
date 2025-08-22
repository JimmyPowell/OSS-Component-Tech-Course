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
    status ENUM('draft', 'pending_review', 'published', 'rejected', 'archived') NOT NULL DEFAULT 'draft',
    views_count INT UNSIGNED NOT NULL DEFAULT 0,
    likes_count INT UNSIGNED NOT NULL DEFAULT 0,
    reviewer_id INT UNSIGNED NULL,
    review_comment TEXT NULL,
    reviewed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for performance
CREATE INDEX idx_showcases_author_id ON showcases(author_id);
CREATE INDEX idx_showcases_status ON showcases(status);
CREATE INDEX idx_showcases_reviewer_id ON showcases(reviewer_id);
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

CREATE TABLE qiniu_tokens (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    user_id INT UNSIGNED NOT NULL,
    token_type ENUM('upload', 'download') NOT NULL,
    bucket VARCHAR(100) NOT NULL,
    file_key VARCHAR(512) NULL,
    token VARCHAR(1024) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    purpose VARCHAR(255) NULL COMMENT 'Token usage purpose description',
    status ENUM('pending', 'approved', 'rejected', 'expired', 'used') NOT NULL DEFAULT 'pending',
    approved_by INT UNSIGNED NULL,
    approved_at TIMESTAMP NULL,
    used_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_qiniu_tokens_user_id ON qiniu_tokens(user_id);
CREATE INDEX idx_qiniu_tokens_token_type ON qiniu_tokens(token_type);
CREATE INDEX idx_qiniu_tokens_status ON qiniu_tokens(status);
CREATE INDEX idx_qiniu_tokens_expires_at ON qiniu_tokens(expires_at);
CREATE INDEX idx_qiniu_tokens_approved_by ON qiniu_tokens(approved_by);
CREATE INDEX idx_qiniu_tokens_created_at ON qiniu_tokens(created_at);

CREATE TABLE announcements (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    summary VARCHAR(512) NULL,
    detail_info LONGTEXT NULL,
    cover_url VARCHAR(512) NULL,
    publisher_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for performance
CREATE INDEX idx_announcements_publisher_id ON announcements(publisher_id);
CREATE INDEX idx_announcements_deleted_at ON announcements(deleted_at);
CREATE INDEX idx_announcements_created_at ON announcements(created_at);

-- Forum Categories Table
CREATE TABLE forum_categories (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    icon VARCHAR(100) NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    post_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes for forum categories
CREATE INDEX idx_forum_categories_is_active ON forum_categories(is_active);
CREATE INDEX idx_forum_categories_sort_order ON forum_categories(sort_order);
CREATE INDEX idx_forum_categories_deleted_at ON forum_categories(deleted_at);

-- Forum Posts Table
CREATE TABLE forum_posts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    category_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    title VARCHAR(200) NOT NULL,
    content LONGTEXT NOT NULL,
    is_pinned BOOLEAN NOT NULL DEFAULT FALSE,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    view_count INT UNSIGNED NOT NULL DEFAULT 0,
    reply_count INT UNSIGNED NOT NULL DEFAULT 0,
    last_reply_at TIMESTAMP NULL,
    last_reply_user_id INT UNSIGNED NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (category_id) REFERENCES forum_categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (last_reply_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for forum posts
CREATE INDEX idx_forum_posts_category_id ON forum_posts(category_id);
CREATE INDEX idx_forum_posts_user_id ON forum_posts(user_id);
CREATE INDEX idx_forum_posts_is_pinned ON forum_posts(is_pinned);
CREATE INDEX idx_forum_posts_is_locked ON forum_posts(is_locked);
CREATE INDEX idx_forum_posts_is_deleted ON forum_posts(is_deleted);
CREATE INDEX idx_forum_posts_last_reply_at ON forum_posts(last_reply_at);
CREATE INDEX idx_forum_posts_created_at ON forum_posts(created_at);
CREATE INDEX idx_forum_posts_deleted_at ON forum_posts(deleted_at);

-- Forum Replies Table
CREATE TABLE forum_replies (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    post_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    parent_id INT UNSIGNED NULL,
    content LONGTEXT NOT NULL,
    reply_to_user_id INT UNSIGNED NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    floor_number INT UNSIGNED NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (parent_id) REFERENCES forum_replies(id) ON DELETE CASCADE,
    FOREIGN KEY (reply_to_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for forum replies
CREATE INDEX idx_forum_replies_post_id ON forum_replies(post_id);
CREATE INDEX idx_forum_replies_user_id ON forum_replies(user_id);
CREATE INDEX idx_forum_replies_parent_id ON forum_replies(parent_id);
CREATE INDEX idx_forum_replies_reply_to_user_id ON forum_replies(reply_to_user_id);
CREATE INDEX idx_forum_replies_is_deleted ON forum_replies(is_deleted);
CREATE INDEX idx_forum_replies_floor_number ON forum_replies(floor_number);
CREATE INDEX idx_forum_replies_created_at ON forum_replies(created_at);
CREATE INDEX idx_forum_replies_deleted_at ON forum_replies(deleted_at);
