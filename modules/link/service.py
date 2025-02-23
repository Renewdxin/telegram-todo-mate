from typing import Optional, Tuple
from datetime import datetime
import re
from modules.link.repository import LinkRepository
from bot.config import TIMEZONE

class LinkService:
    def __init__(self):
        self.repository = LinkRepository()

    def extract_url_and_title(self, text: str) -> Tuple[str, Optional[str]]:
        """
        从文本中提取URL和标题
        支持格式：
        1. 纯URL
        2. "标题 URL"
        """
        # URL正则表达式
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        
        # 查找URL
        url_match = re.search(url_pattern, text)
        if not url_match:
            raise ValueError("未找到有效的URL")
            
        url = url_match.group()
        
        # 提取标题（如果有）
        title = None
        text_without_url = text.replace(url, '').strip()
        if text_without_url:
            title = text_without_url

        return url, title

    def save_link(self, user_id: int, text: str) -> str:
        """保存链接并返回提示信息"""
        try:
            url, title = self.extract_url_and_title(text)
            link = self.repository.create(user_id, url, title)
            return f"✅ 链接已保存！\n🔗 ID: {link.id}\n📝 标题: {title if title else '无标题'}"
        except ValueError as e:
            return f"❌ 错误: {str(e)}"
        except Exception as e:
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
        """