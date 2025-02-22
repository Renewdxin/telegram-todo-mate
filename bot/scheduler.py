"""
定时任务模块，负责每日定时发送待办事项提醒消息
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from telegram.constants import ParseMode
from telegram.error import TelegramError

from modules.todo import service as todo_service
from bot.config import get_current_time, TIMEZONE

async def send_reminder(bot, chat_id):
    """
    根据待办事项信息构造提醒消息，并发送给指定的 chat_id
    """
    current_time = get_current_time()
    
    # 获取所有未完成的任务
    pending = todo_service.get_pending_todos()
    today_tasks = todo_service.get_today_todos()
    
    # 构建未完成任务消息
    if pending:
        left_message = "📋 <b>待办事项清单</b>\n\n"
        for todo in pending:
            # 计算剩余天数，如存在截止时间
            if todo.end_time:
                delta = todo.end_time.astimezone(TIMEZONE).date() - current_time.date()
                days_left = delta.days
                left_message += (
                    f"🔸 <code>{todo.todo_id}</code>. {todo.todo_name}"
                    f" - 还剩 <b>{days_left}</b> 天截止\n"
                )
            else:
                left_message += f"🔸 <code>{todo.todo_id}</code>. {todo.todo_name}\n"
    else:
        left_message = "📋 <b>待办事项清单</b>\n\n✨ 暂无待办事项"
    
    # 构建当天截止任务消息
    if today_tasks:
        today_message = "⚠️ <b>今日截止事项</b>\n\n"
        for todo in today_tasks:
            today_message += f"❗️ <code>{todo.todo_id}</code>. {todo.todo_name}\n"
    else:
        today_message = "📅 <b>今日截止事项</b>\n\n✨ 今天没有截止的任务"
    
    try:
        # 发送消息时使用 HTML 格式
        await bot.send_message(
            chat_id=chat_id,
            text=left_message,
            parse_mode=ParseMode.HTML
        )
        await bot.send_message(
            chat_id=chat_id,
            text=today_message,
            parse_mode=ParseMode.HTML
        )
    except TelegramError as e:
        logging.error("发送提醒失败: %s", e)

def start_scheduler(bot, chat_id, reminder_time: str):
    """
    启动定时任务调度器，根据配置的提醒时间每天发送提醒消息。
    """
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    # 使用 cron 表达式定时触发任务，提醒时间格式为 HH:MM
    hour, minute = map(int, reminder_time.split(":"))
    scheduler.add_job(
        send_reminder,
        'cron',
        hour=hour,
        minute=minute,
        args=[bot, chat_id],
        timezone=TIMEZONE
    )
    scheduler.start()
    return scheduler 