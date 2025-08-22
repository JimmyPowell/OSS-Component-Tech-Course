-- Likes tables for showcase and comments
CREATE TABLE showcase_likes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    showcase_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_showcase_like (showcase_id, user_id),
    INDEX idx_showcase_likes_showcase_id (showcase_id),
    INDEX idx_showcase_likes_user_id (user_id),
    FOREIGN KEY (showcase_id) REFERENCES showcases(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE showcase_comment_likes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    comment_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_comment_like (comment_id, user_id),
    INDEX idx_showcase_comment_likes_comment_id (comment_id),
    INDEX idx_showcase_comment_likes_user_id (user_id),
    FOREIGN KEY (comment_id) REFERENCES showcase_comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE showcase_comment_reply_likes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    reply_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_reply_like (reply_id, user_id),
    INDEX idx_showcase_comment_reply_likes_reply_id (reply_id),
    INDEX idx_showcase_comment_reply_likes_user_id (user_id),
    FOREIGN KEY (reply_id) REFERENCES showcase_comment_replies(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Notification system
CREATE TABLE notifications (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,
    recipient_id INT UNSIGNED NOT NULL COMMENT '通知接收者',
    sender_id INT UNSIGNED NULL COMMENT '通知发起人',
    admin_id INT UNSIGNED NULL COMMENT '管理员（如果是系统通知）',
    type ENUM('like_showcase', 'like_comment', 'comment_showcase', 'reply_comment', 'showcase_approved', 'showcase_rejected', 'system_announcement') NOT NULL COMMENT '通知类型',
    title VARCHAR(255) NOT NULL COMMENT '通知标题',
    content TEXT NULL COMMENT '通知内容',
    related_id INT UNSIGNED NULL COMMENT '相关对象ID（如作品ID、评论ID等）',
    related_uuid VARCHAR(36) NULL COMMENT '相关对象UUID',
    is_read BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已读',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL COMMENT '阅读时间',
    INDEX idx_notifications_recipient_id (recipient_id),
    INDEX idx_notifications_sender_id (sender_id),
    INDEX idx_notifications_admin_id (admin_id),
    INDEX idx_notifications_type (type),
    INDEX idx_notifications_is_read (is_read),
    INDEX idx_notifications_created_at (created_at),
    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
);