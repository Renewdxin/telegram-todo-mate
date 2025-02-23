import sys

sys.dont_write_bytecode = True

from telegram.ext import Application


async def setup_bot(token: str) -> Application:
    """初始化并返回 bot application"""
    try:
        application = Application.builder().token(token).build()
        return application
    except Exception as e:
        print(f"Error initializing bot: {e}")
        return None
