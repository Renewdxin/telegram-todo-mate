import os
import re
from dotenv import load_dotenv
from datetime import datetime

# 从 .env 文件中加载环境变量
load_dotenv()

# 现有配置
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REMINDER_TIME = os.getenv("REMINDER_TIME", "09:00")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")
CHAT_ID = os.getenv("CHAT_ID")

# 数据库配置
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "26221030")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "todobot")

# AI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# 代理配置
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_TYPE = os.getenv("PROXY_TYPE", "http")

# 如果设置了代理，构建代理URL
AI_PROXY = None
if PROXY_HOST and PROXY_PORT:
    AI_PROXY = f"{PROXY_TYPE}://{PROXY_HOST}:{PROXY_PORT}"

# 链接相关配置
DAILY_LINK_REMINDER_TIME = os.getenv("DAILY_LINK_REMINDER_TIME", "10:00")
MAX_SUMMARY_LENGTH = int(os.getenv("MAX_SUMMARY_LENGTH", "200"))

# 验证必要的配置
def validate_config():
    """验证配置是否完整"""
    required_configs = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "OPENAI_API_KEY": OPENAI_API_KEY,
    }
    
    missing_configs = [key for key, value in required_configs.items() if not value]
    
    if missing_configs:
        raise ValueError(f"缺少必要的配置项: {', '.join(missing_configs)}")

# 启动时验证配置
validate_config()

def set_reminder_time(new_time: str) -> bool:
    """
    修改提醒时间，格式需为 HH:MM
    """
    if re.match(r'^\d{2}:\d{2}$', new_time):
        global REMINDER_TIME
        REMINDER_TIME = new_time
        return True
    return False

def get_current_time():
    """
    获取当前时区的时间
    """
    return datetime.now(TIMEZONE) 