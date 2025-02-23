import logging
import os
from logging.handlers import RotatingFileHandler

def init_logger():
    # 创建 logs 目录（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建文件处理器
    file_handler = RotatingFileHandler(
        'logs/bot.log',  # 日志文件路径
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,  # 保留5个备份文件
        encoding='utf-8'
    )
    
    # 设置文件处理器的格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # 获取根日志记录器并添加文件处理器
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # 单独配置 SQL 日志
    sql_handler = RotatingFileHandler(
        'logs/sql.log',
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    sql_handler.setFormatter(formatter)
    
    # 配置 SQLAlchemy 日志
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)
    sql_logger.addHandler(sql_handler) 