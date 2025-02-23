import logging
import re
import ssl

import aiohttp
import certifi
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from modules.link.ai_service import AIService
from modules.link.service import LinkService


class LinkHandler:
    def __init__(self):
        self.service = LinkService()
        self.ai_service = AIService()
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理用户发送的URL"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        response = await self.service.save_link(user_id, message_text)
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)

    async def handle_summarize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /summarize 命令"""
        chat_id = update.effective_chat.id

        try:
            url = context.args[0] if context.args else None

            if url:
                if not url.startswith(('http://', 'https://')):
                    await update.message.reply_text(
                        "❌ 请提供有效的URL（以 http:// 或 https:// 开头）",
                        parse_mode=ParseMode.HTML
                    )
                    return
            else:
                link_info = self.service.get_latest_unread_link(chat_id)
                if isinstance(link_info, str) and "没有未读的链接" in link_info:
                    await update.message.reply_text(link_info)
                    return

                if hasattr(link_info, 'url'):
                    url = link_info.url
                else:
                    url_match = re.search(r'🌐 URL: (https?://[^\n]+)', link_info)
                    if url_match:
                        url = url_match.group(1)
                    else:
                        await update.message.reply_text("❌ 无法获取有效的URL")
                        return

            await update.message.reply_text(
                "🤖 正在生成摘要，请稍候...",
                parse_mode=ParseMode.HTML
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        summary = await self.ai_service.generate_summary(url, content)
                        await update.message.reply_text(
                            summary,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await update.message.reply_text(
                            f"❌ 无法访问链接，状态码：{response.status}",
                            parse_mode=ParseMode.HTML
                        )

        except Exception as e:
            logging.error(f"生成摘要时发生错误: {str(e)}")
            await update.message.reply_text(
                f"❌ 生成摘要时发生错误，请检查URL格式是否正确",
                parse_mode=ParseMode.HTML
            )

    async def handle_explain(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /explain 命令"""
        chat_id = update.effective_chat.id

        try:
            url = context.args[0] if context.args else None

            if url:
                if not url.startswith(('http://', 'https://')):
                    await update.message.reply_text(
                        "❌ 请提供有效的URL（以 http:// 或 https:// 开头）",
                        parse_mode=ParseMode.HTML
                    )
                    return
            else:
                link_info = self.service.get_latest_unread_link(chat_id)
                if isinstance(link_info, str) and "没有未读的链接" in link_info:
                    await update.message.reply_text(link_info)
                    return

                if hasattr(link_info, 'url'):
                    url = link_info.url
                else:
                    url_match = re.search(r'🌐 URL: (https?://[^\n]+)', link_info)
                    if url_match:
                        url = url_match.group(1)
                    else:
                        await update.message.reply_text("❌ 无法获取有效的URL")
                        return

            await update.message.reply_text(
                "🤖 正在生成解释，请稍候...",
                parse_mode=ParseMode.HTML
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        explanation = await self.ai_service.generate_explanation(url, content)
                        await update.message.reply_text(
                            explanation,
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await update.message.reply_text(
                            f"❌ 无法访问链接，状态码：{response.status}",
                            parse_mode=ParseMode.HTML
                        )

        except Exception as e:
            logging.error(f"生成解释时发生错误: {str(e)}")
            await update.message.reply_text(
                f"❌ 生成解释时发生错误，请检查URL格式是否正确",
                parse_mode=ParseMode.HTML
            )

    async def handle_unread(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /unread 命令，显示未读链接统计"""
        user_id = update.effective_user.id
        response = self.service.get_unread_summary(user_id)
        await update.message.reply_text(response, parse_mode=ParseMode.HTML)

    async def handle_mark_read(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /read 命令，将链接标记为已读"""
        if not context.args:
            await update.message.reply_text(
                "❌ 请提供链接ID\n例如：/read 1",
                parse_mode=ParseMode.HTML
            )
            return

        try:
            link_id = int(context.args[0])
            response = self.service.mark_as_read(link_id)
            await update.message.reply_text(response, parse_mode=ParseMode.HTML)
        except ValueError:
            await update.message.reply_text("❌ 无效的链接ID", parse_mode=ParseMode.HTML)

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
