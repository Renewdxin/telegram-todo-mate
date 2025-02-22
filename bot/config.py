import os
import re
from dotenv import load_dotenv
import pytz
from datetime import datetime

# 从 .env 文件中加载环境变量
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YourTelegramBotTokenHere")
REMINDER_TIME = os.getenv("REMINDER_TIME", "09:00")
TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "Asia/Shanghai"))

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