import nest_asyncio

from modules.database import init_db

nest_asyncio.apply()

import logging
import os
from telegram import Update
from telegram.ext import Application
import asyncio
from contextlib import suppress

from bot.handler import register_handlers as register_todo_handlers
from modules.link.handler import LinkHandler
from bot.scheduler import start_scheduler
from bot.config import TELEGRAM_BOT_TOKEN, REMINDER_TIME, TIMEZONE
from utils.logger import init_logger

from bot import setup_bot


async def shutdown(application: Application):
    """Shutdown the application gracefully"""
    logging.info("Shutting down...")
    try:
        if application.running:
            await application.stop()
            await application.shutdown()
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")


async def main():
    """
    主函数：初始化并启动 Telegram Bot
    """
    # 初始化日志
    init_logger()
    logging.info(f"Bot starting... (Timezone: {TIMEZONE})")

    # 创建 Application 实例
    application = await setup_bot(TELEGRAM_BOT_TOKEN)
    if not application:
        logging.error("Failed to initialize bot application")
        return

    try:
        # 注册链接处理器
        link_handler = LinkHandler()
        link_handler.register_handlers(application)

        # 注册待办事项处理器
        register_todo_handlers(application)

        # 启动定时任务
        CHAT_ID = os.getenv("CHAT_ID")
        if CHAT_ID:
            start_scheduler(application.bot, int(CHAT_ID), REMINDER_TIME)
            logging.info(f"Scheduler started. Reminder time: {REMINDER_TIME}")
        else:
            logging.warning("CHAT_ID not set in environment variables!")

        # 启动机器人并保持运行
        logging.info("Bot is running...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await shutdown(application)
        raise e


def run_bot():
    """运行机器人的包装函数"""
    with suppress(KeyboardInterrupt):
        try:
            # 检测是否已有活动的事件循环
            try:
                loop = asyncio.get_running_loop()
                # 如果存在正在运行的事件循环，就直接创建任务并使用 run_forever
                loop.create_task(main())
                loop.run_forever()
            except RuntimeError:
                # 没有运行的事件循环，直接使用 asyncio.run
                asyncio.run(main())
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise e


if __name__ == '__main__':
    # 初始化数据库（仅在首次运行或者确保表不存在时调用一次）
    init_db()
    run_bot()
