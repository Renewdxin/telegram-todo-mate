import logging
import re
from typing import Optional, Tuple

import aiohttp
from bs4 import BeautifulSoup

from modules.link.ai_service import AIService
from modules.link.repository import LinkRepository


async def fetch_title(url: str) -> Optional[str]:
    """通过网络请求获取网页的标题"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    if soup.title and soup.title.string:
                        return soup.title.string.strip()
    except Exception as e:
        # 可根据需要记录日志
        return None


class LinkService:
    def __init__(self):
        self.repository = LinkRepository()
        self.ai_service = AIService()

    async def extract_url_and_title(self, text: str) -> Tuple[str, Optional[str]]:
        """
        从文本中提取 URL 和标题。
        如果用户没有提供标题，则自动请求网页来提取标题。
        支持格式：
        1. 纯 URL
        2. 格式形如 "标题 URL"
        """
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, text)
        if not url_match:
            raise ValueError("未找到有效的 URL")

        url = url_match.group()
        # 如果 URL 前面的部分存在，则认为是标题
        title = text.replace(url, '').strip() or None

        # 如果未提供标题，则尝试使用 AI 生成
        if not title:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            # 使用 AI 服务生成标题
                            title = await self.ai_service.generate_title(url, content)
            except Exception as e:
                logging.error(f"生成标题时发生错误: {e}")
                title = None

        return url, title

    async def save_link(self, user_id: int, text: str) -> str:
        """保存链接并返回提示信息"""
        try:
            url, title = await self.extract_url_and_title(text)
            link = self.repository.create(user_id, url, title)
            return f"✅ 链接已保存！\n🔗 ID: {link.id}\n📝 标题: {title if title else '无标题'}"
        except ValueError as e:
            return f"❌ 错误: {str(e)}"
        except Exception as e:
            logging.error(f"保存链接时发生错误: {e}")
            return "❌ 保存链接时发生错误"

    def get_unread_summary(self, user_id: int) -> str:
        """获取未读链接统计信息"""
        count = self.repository.get_unread_count(user_id)
        if count == 0:
            return "📚 您现在没有未读的链接"
        return f"📚 您还有 {count} 个链接未读"

    def format_link_info(self, link) -> str:
        """格式化链接信息"""
        result = f"🔗 链接 {link.id}:\n"
        if link.title:
            result += f"📝 标题: {link.title}\n"
        result += f"🌐 URL: {link.url}\n"
        if link.summary:
            result += f"📋 摘要: {link.summary}\n"
        result += f"⏰ 保存时间: {link.created_at.strftime('%Y-%m-%d %H:%M')}"
        return result

    def get_random_unread_link(self, user_id: int) -> str:
        """获取随机未读链接"""
        link = self.repository.get_random_unread_link(user_id)
        if not link:
            return "📭 没有未读的链接"
        return self.format_link_info(link)

    def mark_as_read(self, link_id: int) -> str:
        """将链接标记为已读"""
        if self.repository.mark_as_read(link_id):
            return f"✅ 链接 {link_id} 已标记为已读"
        return f"❌ 链接 {link_id} 不存在"

    def update_summary(self, link_id: int, summary: str) -> str:
        """更新链接摘要"""
        if self.repository.update_summary(link_id, summary):
            return f"✅ 链接摘要已更新：\n\n{summary}"
        return f"❌ 更新摘要失败：链接 {link_id} 不存在"

    def get_latest_unread_link(self, user_id: int) -> str:
        """获取最新添加的未读链接信息"""
        link = self.repository.get_latest_unread_link(user_id)
        if not link:
            return "📭 没有未读的链接"
        return self.format_link_info(link)

    def get_unread_links(self, user_id: int) -> str:
        """获取最新的5条未读链接列表"""
        links = self.repository.get_unread_links(user_id, limit=5)
        if not links:
            return "📭 没有未读的链接"

        result = "📚 部分未读链接列表：\n"
        for link in links:
            result += "\n" + self.format_link_info(link) + "\n"

        return result
