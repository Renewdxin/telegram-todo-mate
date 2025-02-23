from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

# PostgreSQL 配置
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "todobot")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    echo=True,
    echo_pool=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """ 初始化数据库表（第一次启动时执行） """
    from modules.base_model import Base
    Base.metadata.create_all(bind=engine) 