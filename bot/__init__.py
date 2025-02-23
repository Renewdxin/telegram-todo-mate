import sys
sys.dont_write_bytecode = True

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handler import (
    handle_demo_command, 
    handle_demoz_command, 
    handle_message,
    handle_summarize_command,
    handle_explain_command,
    handle_unread_command,
    handle_read_command
)

async def setup_bot(token: str):
    """初始化并配置机器人"""
    application = Application.builder().token(token).build()
    
    # 注册待办事项命令处理器
    application.add_handler(CommandHandler("demo", handle_demo_command))
    application.add_handler(CommandHandler("demoz", handle_demoz_command))
    
    # 注册链接管理命令处理器
    application.add_handler(CommandHandler("summarize", handle_summarize_command))
    application.add_handler(CommandHandler("explain", handle_explain_command))
    application.add_handler(CommandHandler("unread", handle_unread_command))
    application.add_handler(CommandHandler("read", handle_read_command))
    
    # 注册消息处理器（用于处理非命令消息）
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    
    return application 