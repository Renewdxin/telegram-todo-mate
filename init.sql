-- 如果表不存在则创建 todos 表
CREATE TABLE IF NOT EXISTS todos (
    todo_id SERIAL PRIMARY KEY,
    create_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    todo_name TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
); 