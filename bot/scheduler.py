import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.config import get_current_time, TIMEZONE
from modules.link.service import LinkService
from modules.todo import service as todo_service


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


async def send_unread_links_summary(bot, chat_id):
    """
    发送未读链接摘要
    """
    service = LinkService()
    # 获取5条未读链接
    unread_links = service.get_unread_links(limit=5)
    
    if not unread_links:
        await bot.send_message(
            chat_id=chat_id,
            text="📚 今天没有未读的链接",
            parse_mode=ParseMode.HTML
        )
        return

    # 发送总览消息
    overview = "📚 <b>未读链接摘要</b>\n\n"
    for i, link in enumerate(unread_links, 1):
        overview += f"{i}. <a href='{link.url}'>{link.title or '无标题'}</a>\n"
    
    await bot.send_message(
        chat_id=chat_id,
        text=overview,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    # 为每个链接生成并发送摘要
    for link in unread_links:
        try:
            summary = await service.generate_summary(link.url)
            message = f"🔍 <b>{link.title or '无标题'}</b>\n\n"
            message += f"🌐 <a href='{link.url}'>原文链接</a>\n\n"
            message += f"📝 <b>摘要</b>:\n{summary}"
            
            try:  # 添加单独的消息发送错误处理
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except TelegramError as te:
                logging.error(f"发送链接摘要消息失败: {te}")
                # 尝试发送不带格式的消息
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"链接: {link.url}\n\n摘要生成失败，请直接访问原文。",
                    disable_web_page_preview=True
                )
        except Exception as e:
            logging.error(f"生成链接摘要失败 (URL: {link.url}): {str(e)}")
            continue


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
    # 添加未读链接摘要推送
    scheduler.add_job(
        send_unread_links_summary,
        'cron',
        hour=14,
        minute=50,
        args=[bot, chat_id],
        timezone=TIMEZONE
    )
    scheduler.start()
    return scheduler


async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """发送每日未读链接提醒"""
    job = context.job
    user_id = job.data['user_id']

    service = LinkService()
    reminder = service.get_unread_summary(user_id)

    await context.bot.send_message(
        chat_id=user_id,
        text=f"📅 每日提醒\n{reminder}"
    )


def schedule_daily_reminder(application, user_id: int, time: str = "10:00"):
    """设置每日提醒定时任务"""
    job_queue = application.job_queue

    # 解析时间
    hour, minute = map(int, time.split(':'))

    # 设置每日定时任务
    job_queue.run_daily(
        send_daily_reminder,
        time=datetime.time(hour=hour, minute=minute),
        days=(0, 1, 2, 3, 4, 5, 6),  # 每天
        data={'user_id': user_id}
    )
