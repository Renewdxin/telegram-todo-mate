-- 创建待办事项表
CREATE TABLE IF NOT EXISTS todos
(
    todo_id
    SERIAL
    PRIMARY
    KEY,
    todo_name
    TEXT
    NOT
    NULL,
    is_completed
    BOOLEAN
    DEFAULT
    FALSE,
    create_time
    TIMESTAMP
    WITH
    TIME
    ZONE
    DEFAULT
    CURRENT_TIMESTAMP,
    end_time
    TIMESTAMP
    WITH
    TIME
    ZONE
);

-- 创建链接管理表
CREATE TABLE IF NOT EXISTS links
(
    id
    SERIAL
    PRIMARY
    KEY,
    user_id
    BIGINT
    NOT
    NULL,              -- Telegram 用户ID
    url
    TEXT
    NOT
    NULL,              -- 链接地址
    title
    TEXT,              -- 链接标题（可选）
    is_read
    BOOLEAN
    DEFAULT
    FALSE,             -- 是否已读
    summary
    TEXT,              -- AI 生成的摘要（可选）
    created_at
    TIMESTAMP
    WITH
    TIME
    ZONE
    DEFAULT
    CURRENT_TIMESTAMP, -- 创建时间
    read_at
    TIMESTAMP
    WITH
    TIME
    ZONE               -- 阅读时间
);

-- 为链接表创建索引
CREATE INDEX IF NOT EXISTS idx_links_user_id ON links(user_id);
CREATE INDEX IF NOT EXISTS idx_links_is_read ON links(is_read);
CREATE INDEX IF NOT EXISTS idx_links_created_at ON links(created_at);

-- 为链接表添加注释
COMMENT
ON TABLE links IS '链接管理表';
COMMENT
ON COLUMN links.id IS '链接ID';
COMMENT
ON COLUMN links.user_id IS 'Telegram用户ID';
COMMENT
ON COLUMN links.url IS '链接地址';
COMMENT
ON COLUMN links.title IS '链接标题';
COMMENT
ON COLUMN links.is_read IS '是否已读';
COMMENT
ON COLUMN links.summary IS 'AI生成的摘要';
COMMENT
ON COLUMN links.created_at IS '创建时间';
COMMENT
ON COLUMN links.read_at IS '阅读时间';