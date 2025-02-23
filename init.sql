-- 如果表不存在则创建 todos 表
CREATE TABLE IF NOT EXISTS todos (
    todo_id SERIAL PRIMARY KEY,
    create_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    todo_name TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

-- 创建链接表
CREATE TABLE IF NOT EXISTS links (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,                    -- Telegram 用户 ID
    url TEXT NOT NULL,                          -- 链接地址
    title TEXT,                                 -- 链接标题（可选，后续可通过爬虫获取）
    is_read BOOLEAN DEFAULT FALSE,              -- 是否已读
    summary TEXT,                               -- AI 生成的摘要（可选）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    read_at TIMESTAMP                           -- 阅读时间
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_links_user_id ON links(user_id);
CREATE INDEX IF NOT EXISTS idx_links_is_read ON links(is_read);
CREATE INDEX IF NOT EXISTS idx_links_created_at ON links(created_at); 