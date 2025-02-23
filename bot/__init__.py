import sys
sys.dont_write_bytecode = True

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handler import handle_demo_command, handle_demoz_command, handle_message

async def setup_bot(token: str):
    """初始化并配置机器人"""
    application = Application.builder().token(token).build()
    
    # 注册命令处理器
    application.add_handler(CommandHandler("demo", handle_demo_command))
    application.add_handler(CommandHandler("demoz", handle_demoz_command))
    
    # 注册消息处理器（用于处理非命令消息）
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application 