from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from telegram.constants import ParseMode
from telegram.error import TelegramError
from datetime import datetime, timedelta

from modules.todo import service as todo_service
from bot.config import get_current_time, TIMEZONE

async def send_reminder(bot, chat_id):
    """
    发送早间提醒，只包含今日截止的待办事项
    """
    current_time = get_current_time()
    today_tasks = todo_service.get_today_todos()
    
    message = "🌅 <b>早间提醒</b>\n\n"
    message += "📅 <b>今日截止事项</b>\n"
    
    if today_tasks:
        for todo in today_tasks:
            message += f"❗️ <code>{todo.todo_id}</code>. {todo.todo_name}\n"
    else:
        message += "✨ 今天没有截止的任务"
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.HTML
        )
    except TelegramError as e:
        logging.error("发送提醒失败: %s", e)

async def send_afternoon_reminder(bot, chat_id):
    """
    发送下午提醒，分别发送今日和明日截止的待办事项
    """
    today_tasks = todo_service.get_today_todos()
    tomorrow_tasks = todo_service.get_tomorrow_todos()
    
    # 发送今日截止任务
    today_message = "🕒 <b>下午提醒</b>\n\n"
    today_message += "📅 <b>今日截止事项</b>\n"
    if today_tasks:
        for todo in today_tasks:
            today_message += f"❗️ <code>{todo.todo_id}</code>. {todo.todo_name}\n"
    else:
        today_message += "✨ 今天没有截止的任务"
    
    # 发送明日截止任务
    tomorrow_message = "🕒 <b>下午提醒</b>\n\n"
    tomorrow_message += "📆 <b>明日截止事项</b>\n"
    if tomorrow_tasks:
        for todo in tomorrow_tasks:
            tomorrow_message += f"⚠️ <code>{todo.todo_id}</code>. {todo.todo_name}\n"
    else:
        tomorrow_message += "✨ 明天没有截止的任务"
    
    try:
        # 分别发送两条消息
        await bot.send_message(
            chat_id=chat_id,
            text=today_message,
            parse_mode=ParseMode.HTML
        )
        await bot.send_message(
            chat_id=chat_id,
            text=tomorrow_message,
            parse_mode=ParseMode.HTML
        )
    except TelegramError as e:
        logging.error("发送下午提醒失败: %s", e)

def start_scheduler(bot, chat_id, reminder_time: str):
    """
    启动定时任务调度器，设置每日早晚两次提醒。
    """
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    # 早间提醒
    hour, minute = map(int, reminder_time.split(":"))
    scheduler.add_job(
        send_reminder,
        'cron',
        hour=hour,
        minute=minute,
        args=[bot, chat_id],
        timezone=TIMEZONE
    )
    # 添加下午 16:00 提醒
    scheduler.add_job(
        send_afternoon_reminder,
        'cron',
        hour=16,
        minute=0,
        args=[bot, chat_id],
        timezone=TIMEZONE
    )
    scheduler.start()
    return scheduler 