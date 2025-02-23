from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from modules.link.service import LinkService
from datetime import datetime
import re

class LinkHandler:
    def __init__(self):
        self.service = LinkService()

    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理用户发送的URL"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        response = self.service.save_link(user_id, message_text)
        await update.message.reply_text(response)

    async def handle_summarize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /summarize 命令，随机选择一个未读链接进行AI总结"""
        user_id = update.effective_user.id
        
        # 获取随机未读链接
        link_info = self.service.get_random_unread_link(user_id)
        if "没有未读的链接" in link_info:
            await update.message.reply_text(link_info)
            return

        await update.message.reply_text("🤖 正在生成摘要，请稍候...")
        
        try:
            # TODO: 调用AI服务生成摘要
            summary = "这里是AI生成的摘要"  # 临时占位，需要替换为实际的AI调用
            
            # 更新链接摘要
            response = self.service.update_summary(link_id, summary)
            await update.message.reply_text(response)
            
        except Exception as e:
            await update.message.reply_text("❌ 生成摘要时发生错误")

    async def handle_explain(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /explain 命令，解释指定链接"""
        user_id = update.effective_user.id
        
        # 检查命令格式
        if not context.args:
            await update.message.reply_text("❌ 请提供要解释的链接\n例如：/explain https://example.com")
            return
            
        url = context.args[0]
        
        # 验证URL格式
        if not re.match(r'https?://', url):
            await update.message.reply_text("❌ 请提供有效的URL")
            return
            
        await update.message.reply_text("🤖 正在生成解释，请稍候...")
        
        try:
            # TODO: 调用AI服务生成解释
            explanation = "这里是AI生成的解释"  # 临时占位，需要替换为实际的AI调用
            await update.message.reply_text(explanation)
            
        except Exception as e:
            await update.message.reply_text("❌ 生成解释时发生错误")

    async def handle_unread(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /unread 命令，显示未读链接统计"""
        user_id = update.effective_user.id
        response = self.service.get_unread_summary(user_id)
        await update.message.reply_text(response)

    async def handle_mark_read(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /read 命令，将链接标记为已读"""
        if not context.args:
            await update.message.reply_text("❌ 请提供链接ID\n例如：/read 1")
            return
            
        try:
            link_id = int(context.args[0])
            response = self.service.mark_as_read(link_id)
            await update.message.reply_text(response)
        except ValueError:
            await update.message.reply_text("❌ 无效的链接ID")

    def register_handlers(self, application):
        """注册所有处理器"""
        # 处理URL消息
        url_handler = MessageHandler(
            filters.TEXT & filters.Regex(r'https?://'), 
            self.handle_url
        )
        
        # 注册命令处理器
        application.add_handler(CommandHandler("summarize", self.handle_summarize))
        application.add_handler(CommandHandler("explain", self.handle_explain))
        application.add_handler(CommandHandler("unread", self.handle_unread))
        application.add_handler(CommandHandler("read", self.handle_mark_read))
        application.add_handler(url_handler)
