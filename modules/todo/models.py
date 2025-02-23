from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig()
# 创建一个文件处理器
sql_handler = logging.FileHandler('sql.log')
sql_handler.setLevel(logging.INFO)
# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(message)s')
sql_handler.setFormatter(formatter)

# 获取 SQLAlchemy 的日志记录器
sql_logger = logging.getLogger('sqlalchemy.engine')
sql_logger.setLevel(logging.INFO)
sql_logger.addHandler(sql_handler)

Base = declarative_base()

class Todo(Base):
    __tablename__ = 'todos'
    todo_id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.utcnow)  # 创建时间
    end_time = Column(DateTime, nullable=True)  # 截止时间
    todo_name = Column(Text, nullable=False)    # 任务内容
    status = Column(String(20), default="pending")  # 状态：pending（待办）、completed（已完成）

    def __repr__(self):
        return f"<Todo(id={self.todo_id}, todo_name={self.todo_name}, status={self.status})>"

# PostgreSQL 配置（推荐通过环境变量）
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "todobot")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建引擎时启用 SQL 语句记录
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 启用 SQL 语句输出
    echo_pool=True  # 启用连接池相关日志
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """ 初始化数据库表（第一次启动时执行） """
    Base.metadata.create_all(bind=engine) 