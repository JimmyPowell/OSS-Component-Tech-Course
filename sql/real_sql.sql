create table announcements
(
    id           int unsigned auto_increment
        primary key,
    uuid         char(36)                                              not null,
    name         varchar(255)                                          not null,
    summary      varchar(512)                                          null,
    detail_info  longtext                                              null,
    cover_url    varchar(512)                                          null,
    publisher_id int unsigned                                          not null,
    created_at   timestamp                   default CURRENT_TIMESTAMP not null,
    updated_at   timestamp                   default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at   timestamp                                             null,
    status       enum ('draft', 'published') default 'draft'           not null comment '状态：草稿/已发布',
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_announcements_created_at
    on announcements (created_at);

create index idx_announcements_deleted_at
    on announcements (deleted_at);

create index idx_announcements_publisher_id
    on announcements (publisher_id);

create table blog_tags
(
    id          int unsigned auto_increment
        primary key,
    name        varchar(50)                          not null comment '标签名称',
    color       varchar(7) default '#2196F3'         null comment '标签颜色(HEX)',
    description text                                 null comment '标签描述',
    created_at  timestamp  default CURRENT_TIMESTAMP null,
    constraint name
        unique (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    comment 'Blog标签表';

create index idx_name
    on blog_tags (name);

create table course_resources
(
    id             int unsigned auto_increment
        primary key,
    uuid           char(36)                                              not null,
    name           varchar(255)                                          not null,
    summary        varchar(512)                                          null,
    type           enum ('ppt', 'video', 'attachment', 'other')          not null,
    description    text                                                  null,
    creator_id     int unsigned                                          not null,
    created_at     timestamp                   default CURRENT_TIMESTAMP not null,
    updated_at     timestamp                   default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at     timestamp                                             null,
    cover_url      varchar(512)                                          null,
    resource_url   varchar(512)                                          not null,
    file_size      int unsigned                                          null,
    mime_type      varchar(100)                                          null,
    download_count int unsigned                default '0'               not null,
    status         enum ('draft', 'published') default 'draft'           not null comment '状态：草稿/已发布',
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_course_resource_published
    on course_resources (status, created_at);

create index idx_course_resource_status
    on course_resources (status);

create index idx_course_resources_created_at
    on course_resources (created_at);

create index idx_course_resources_creator_id
    on course_resources (creator_id);

create index idx_course_resources_deleted_at
    on course_resources (deleted_at);

create index idx_course_resources_type
    on course_resources (type);

create table forum_categories
(
    id          int unsigned auto_increment
        primary key,
    uuid        char(36)                               not null,
    name        varchar(100)                           not null,
    description text                                   null,
    icon        varchar(100)                           null,
    sort_order  int          default 0                 not null,
    is_active   tinyint(1)   default 1                 not null,
    post_count  int unsigned default '0'               not null,
    created_at  timestamp    default CURRENT_TIMESTAMP not null,
    updated_at  timestamp    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at  timestamp                              null,
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_forum_categories_deleted_at
    on forum_categories (deleted_at);

create index idx_forum_categories_is_active
    on forum_categories (is_active);

create index idx_forum_categories_sort_order
    on forum_categories (sort_order);

create table homeworks
(
    id            int unsigned auto_increment
        primary key,
    uuid          char(36)                                              not null,
    name          varchar(255)                                          not null,
    description   text                                                  null,
    content       longtext                                              null,
    cover_url     varchar(512)                                          null,
    resource_urls json                                                  null,
    creator_id    int unsigned                                          not null,
    lasting_time  int unsigned                                          null comment 'Lasting time in minutes',
    status        enum ('draft', 'published') default 'draft'           not null,
    created_at    timestamp                   default CURRENT_TIMESTAMP not null,
    updated_at    timestamp                   default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at    timestamp                                             null,
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_homeworks_creator_id
    on homeworks (creator_id);

create index idx_homeworks_deleted_at
    on homeworks (deleted_at);

create index idx_homeworks_status
    on homeworks (status);

create index idx_homeworks_status_deleted
    on homeworks (status, deleted_at);

create table qiniu_tokens
(
    id          int unsigned auto_increment
        primary key,
    uuid        char(36)                                                                              not null,
    user_id     int unsigned                                                                          not null,
    token_type  enum ('upload', 'download')                                                           not null,
    bucket      varchar(100)                                                                          not null,
    file_key    varchar(512)                                                                          null,
    token       varchar(1024)                                                                         not null,
    expires_at  timestamp                                                                             not null,
    purpose     varchar(255)                                                                          null comment 'Token usage purpose description',
    status      enum ('pending', 'approved', 'rejected', 'expired', 'used') default 'pending'         not null,
    approved_by int unsigned                                                                          null,
    approved_at timestamp                                                                             null,
    used_at     timestamp                                                                             null,
    created_at  timestamp                                                   default CURRENT_TIMESTAMP not null,
    updated_at  timestamp                                                   default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_qiniu_tokens_approved_by
    on qiniu_tokens (approved_by);

create index idx_qiniu_tokens_created_at
    on qiniu_tokens (created_at);

create index idx_qiniu_tokens_expires_at
    on qiniu_tokens (expires_at);

create index idx_qiniu_tokens_status
    on qiniu_tokens (status);

create index idx_qiniu_tokens_token_type
    on qiniu_tokens (token_type);

create index idx_qiniu_tokens_user_id
    on qiniu_tokens (user_id);

create table showcase_comment_replies
(
    id               int unsigned auto_increment
        primary key,
    uuid             char(36)                               not null,
    comment_id       int unsigned                           not null,
    user_id          int unsigned                           not null,
    reply_to_user_id int unsigned                           null,
    content          text                                   not null,
    likes_count      int unsigned default '0'               not null,
    created_at       timestamp    default CURRENT_TIMESTAMP not null,
    updated_at       timestamp    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at       timestamp                              null,
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_showcase_comment_replies_comment_id
    on showcase_comment_replies (comment_id);

create index idx_showcase_comment_replies_deleted_at
    on showcase_comment_replies (deleted_at);

create index idx_showcase_comment_replies_reply_to_user_id
    on showcase_comment_replies (reply_to_user_id);

create index idx_showcase_comment_replies_user_id
    on showcase_comment_replies (user_id);

create table showcase_comments
(
    id          int unsigned auto_increment
        primary key,
    uuid        char(36)                               not null,
    showcase_id int unsigned                           not null,
    user_id     int unsigned                           not null,
    content     text                                   not null,
    likes_count int unsigned default '0'               not null,
    created_at  timestamp    default CURRENT_TIMESTAMP not null,
    updated_at  timestamp    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at  timestamp                              null,
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_showcase_comments_deleted_at
    on showcase_comments (deleted_at);

create index idx_showcase_comments_showcase_id
    on showcase_comments (showcase_id);

create index idx_showcase_comments_user_id
    on showcase_comments (user_id);

create table showcases
(
    id                    int unsigned auto_increment
        primary key,
    uuid                  char(36)                                                                                not null,
    name                  varchar(255)                                                                            not null,
    summary               varchar(512)                                                                            null,
    detailed_introduction longtext                                                                                null,
    avatar_url            varchar(512)                                                                            null,
    project_url           varchar(512)                                                                            null,
    author_id             int unsigned                                                                            not null,
    tags                  json                                                                                    null,
    status                enum ('draft', 'pending', 'published', 'reject', 'excellent') default 'draft'           not null,
    previous_status       varchar(20)                                                                             null,
    views_count           int unsigned                                                  default '0'               not null,
    likes_count           int unsigned                                                  default '0'               not null,
    reviewer_id           int unsigned                                                                            null,
    review_comment        text                                                                                    null,
    reviewed_at           timestamp                                                                               null,
    created_at            timestamp                                                     default CURRENT_TIMESTAMP not null,
    updated_at            timestamp                                                     default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at            timestamp                                                                               null,
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_showcases_author_id
    on showcases (author_id);

create index idx_showcases_deleted_at
    on showcases (deleted_at);

create index idx_showcases_reviewer_id
    on showcases (reviewer_id);

create index idx_showcases_status
    on showcases (status);

create table users
(
    id              int unsigned auto_increment
        primary key,
    uuid            varchar(36)                           not null,
    username        varchar(50)                           not null,
    email           varchar(100)                          not null,
    real_name       varchar(50)                           null,
    phone_number    varchar(20)                           null,
    school          varchar(100)                          null,
    avatar_url      varchar(255)                          null,
    hashed_password varchar(255)                          not null,
    is_active       tinyint(1)  default 1                 null,
    role            varchar(50) default 'user'            not null,
    created_at      timestamp   default CURRENT_TIMESTAMP null,
    updated_at      timestamp   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    deleted_at      timestamp                             null,
    student_id      varchar(255)                          null,
    student_class   varchar(255)                          null,
    constraint email
        unique (email),
    constraint username
        unique (username),
    constraint uuid
        unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table blogs
(
    id         int unsigned auto_increment
        primary key,
    uuid       char(36)                                                          not null,
    title      varchar(255)                                                      not null comment '文章标题',
    content    text                                                              not null comment '文章内容(支持Markdown)',
    summary    text                                                              null comment '文章摘要',
    author_id  int unsigned                                                      not null comment '作者ID',
    cover_url  varchar(500)                                                      null comment '封面图片URL',
    view_count int unsigned                            default '0'               null comment '浏览次数',
    like_count int unsigned                            default '0'               null comment '点赞次数',
    status     enum ('draft', 'published', 'archived') default 'published'       null comment '状态:草稿/已发布/已归档',
    is_deleted tinyint(1)                              default 0                 null comment '软删除标记',
    created_at timestamp                               default CURRENT_TIMESTAMP null,
    updated_at timestamp                               default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint uuid
        unique (uuid),
    constraint blogs_ibfk_1
        foreign key (author_id) references users (id)
            on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    comment 'Blog文章表';

create table blog_tag_relations
(
    id         int unsigned auto_increment
        primary key,
    blog_id    int unsigned                        not null,
    tag_id     int unsigned                        not null,
    created_at timestamp default CURRENT_TIMESTAMP null,
    constraint unique_blog_tag
        unique (blog_id, tag_id),
    constraint blog_tag_relations_ibfk_1
        foreign key (blog_id) references blogs (id)
            on delete cascade,
    constraint blog_tag_relations_ibfk_2
        foreign key (tag_id) references blog_tags (id)
            on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    comment 'Blog文章标签关联表';

create index idx_blog
    on blog_tag_relations (blog_id);

create index idx_tag
    on blog_tag_relations (tag_id);

create index idx_author
    on blogs (author_id);

create index idx_created
    on blogs (created_at);

create index idx_published
    on blogs (status, created_at);

create index idx_status
    on blogs (status);

create index idx_uuid
    on blogs (uuid);

create table forum_posts
(
    id                 int unsigned auto_increment
        primary key,
    uuid               char(36)                               not null,
    category_id        int unsigned                           not null,
    user_id            int unsigned                           not null,
    title              varchar(200)                           not null,
    content            longtext                               not null,
    is_pinned          tinyint(1)   default 0                 not null,
    is_locked          tinyint(1)   default 0                 not null,
    is_deleted         tinyint(1)   default 0                 not null,
    view_count         int unsigned default '0'               not null,
    reply_count        int unsigned default '0'               not null,
    last_reply_at      timestamp                              null,
    last_reply_user_id int unsigned                           null,
    created_at         timestamp    default CURRENT_TIMESTAMP not null,
    updated_at         timestamp    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at         timestamp                              null,
    constraint uuid
        unique (uuid),
    constraint forum_posts_ibfk_1
        foreign key (category_id) references forum_categories (id),
    constraint forum_posts_ibfk_2
        foreign key (user_id) references users (id),
    constraint forum_posts_ibfk_3
        foreign key (last_reply_user_id) references users (id)
            on delete set null
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_forum_posts_category_id
    on forum_posts (category_id);

create index idx_forum_posts_created_at
    on forum_posts (created_at);

create index idx_forum_posts_deleted_at
    on forum_posts (deleted_at);

create index idx_forum_posts_is_deleted
    on forum_posts (is_deleted);

create index idx_forum_posts_is_locked
    on forum_posts (is_locked);

create index idx_forum_posts_is_pinned
    on forum_posts (is_pinned);

create index idx_forum_posts_last_reply_at
    on forum_posts (last_reply_at);

create index idx_forum_posts_user_id
    on forum_posts (user_id);

create index last_reply_user_id
    on forum_posts (last_reply_user_id);

create table forum_replies
(
    id               int unsigned auto_increment
        primary key,
    uuid             char(36)                             not null,
    post_id          int unsigned                         not null,
    user_id          int unsigned                         not null,
    parent_id        int unsigned                         null,
    content          longtext                             not null,
    reply_to_user_id int unsigned                         null,
    is_deleted       tinyint(1) default 0                 not null,
    floor_number     int unsigned                         null,
    created_at       timestamp  default CURRENT_TIMESTAMP not null,
    updated_at       timestamp  default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    deleted_at       timestamp                            null,
    constraint uuid
        unique (uuid),
    constraint forum_replies_ibfk_1
        foreign key (post_id) references forum_posts (id)
            on delete cascade,
    constraint forum_replies_ibfk_2
        foreign key (user_id) references users (id),
    constraint forum_replies_ibfk_3
        foreign key (parent_id) references forum_replies (id)
            on delete cascade,
    constraint forum_replies_ibfk_4
        foreign key (reply_to_user_id) references users (id)
            on delete set null
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_forum_replies_created_at
    on forum_replies (created_at);

create index idx_forum_replies_deleted_at
    on forum_replies (deleted_at);

create index idx_forum_replies_floor_number
    on forum_replies (floor_number);

create index idx_forum_replies_is_deleted
    on forum_replies (is_deleted);

create index idx_forum_replies_parent_id
    on forum_replies (parent_id);

create index idx_forum_replies_post_id
    on forum_replies (post_id);

create index idx_forum_replies_reply_to_user_id
    on forum_replies (reply_to_user_id);

create index idx_forum_replies_user_id
    on forum_replies (user_id);

create table notifications
(
    id           int unsigned auto_increment
        primary key,
    uuid         char(36)                                                                                                                                     not null,
    recipient_id int unsigned                                                                                                                                 not null comment '通知接收者',
    sender_id    int unsigned                                                                                                                                 null comment '通知发起人',
    admin_id     int unsigned                                                                                                                                 null comment '管理员（如果是系统通知）',
    type         enum ('like_showcase', 'like_comment', 'comment_showcase', 'reply_comment', 'showcase_approved', 'showcase_rejected', 'system_announcement') not null comment '通知类型',
    title        varchar(255)                                                                                                                                 not null comment '通知标题',
    content      text                                                                                                                                         null comment '通知内容',
    related_id   int unsigned                                                                                                                                 null comment '相关对象ID（如作品ID、评论ID等）',
    related_uuid varchar(36)                                                                                                                                  null comment '相关对象UUID',
    is_read      tinyint(1) default 0                                                                                                                         not null comment '是否已读',
    created_at   timestamp  default CURRENT_TIMESTAMP                                                                                                         not null,
    read_at      timestamp                                                                                                                                    null comment '阅读时间',
    constraint uuid
        unique (uuid),
    constraint notifications_ibfk_1
        foreign key (recipient_id) references users (id)
            on delete cascade,
    constraint notifications_ibfk_2
        foreign key (sender_id) references users (id)
            on delete set null,
    constraint notifications_ibfk_3
        foreign key (admin_id) references users (id)
            on delete set null
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_notifications_admin_id
    on notifications (admin_id);

create index idx_notifications_created_at
    on notifications (created_at);

create index idx_notifications_is_read
    on notifications (is_read);

create index idx_notifications_recipient_id
    on notifications (recipient_id);

create index idx_notifications_sender_id
    on notifications (sender_id);

create index idx_notifications_type
    on notifications (type);

create table showcase_comment_likes
(
    id         int unsigned auto_increment
        primary key,
    uuid       char(36)                            not null,
    comment_id int unsigned                        not null,
    user_id    int unsigned                        not null,
    created_at timestamp default CURRENT_TIMESTAMP not null,
    constraint unique_comment_like
        unique (comment_id, user_id),
    constraint uuid
        unique (uuid),
    constraint showcase_comment_likes_ibfk_1
        foreign key (comment_id) references showcase_comments (id)
            on delete cascade,
    constraint showcase_comment_likes_ibfk_2
        foreign key (user_id) references users (id)
            on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_showcase_comment_likes_comment_id
    on showcase_comment_likes (comment_id);

create index idx_showcase_comment_likes_user_id
    on showcase_comment_likes (user_id);

create table showcase_comment_reply_likes
(
    id         int unsigned auto_increment
        primary key,
    uuid       char(36)                            not null,
    reply_id   int unsigned                        not null,
    user_id    int unsigned                        not null,
    created_at timestamp default CURRENT_TIMESTAMP not null,
    constraint unique_reply_like
        unique (reply_id, user_id),
    constraint uuid
        unique (uuid),
    constraint showcase_comment_reply_likes_ibfk_1
        foreign key (reply_id) references showcase_comment_replies (id)
            on delete cascade,
    constraint showcase_comment_reply_likes_ibfk_2
        foreign key (user_id) references users (id)
            on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_showcase_comment_reply_likes_reply_id
    on showcase_comment_reply_likes (reply_id);

create index idx_showcase_comment_reply_likes_user_id
    on showcase_comment_reply_likes (user_id);

create table showcase_likes
(
    id          int unsigned auto_increment
        primary key,
    uuid        char(36)                            not null,
    showcase_id int unsigned                        not null,
    user_id     int unsigned                        not null,
    created_at  timestamp default CURRENT_TIMESTAMP not null,
    constraint unique_showcase_like
        unique (showcase_id, user_id),
    constraint uuid
        unique (uuid),
    constraint showcase_likes_ibfk_1
        foreign key (showcase_id) references showcases (id)
            on delete cascade,
    constraint showcase_likes_ibfk_2
        foreign key (user_id) references users (id)
            on delete cascade
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create index idx_showcase_likes_showcase_id
    on showcase_likes (showcase_id);

create index idx_showcase_likes_user_id
    on showcase_likes (user_id);

create index idx_users_deleted_at
    on users (deleted_at);

create index idx_users_is_active
    on users (is_active);
