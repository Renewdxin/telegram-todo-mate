from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """ 初始化数据库表（第一次启动时执行） """
    Base.metadata.create_all(bind=engine) 