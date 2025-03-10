import logging
import re
import html
from typing import Optional, Tuple, List

import aiohttp
from bs4 import BeautifulSoup

from modules.link.ai_service import AIService
from modules.link.repository import LinkRepository
from modules.database import SessionLocal
from modules.link.models import Link


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

    def clean_html(self, text: str) -> str:
        """清理HTML标签并转义特殊字符"""
        # 移除所有HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 转义特殊字符
        text = html.escape(text)
        return text

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
            # 首先尝试从文本中提取URL和用户可能提供的标题
            url_pattern = r'https?://[^\s]+'
            url_match = re.search(url_pattern, text)
            if not url_match:
                return "❌ 错误: 未找到有效的 URL"
            
            url = url_match.group()
            user_title = text.replace(url, '').strip() or None
            
            if user_title:
                user_title = self.clean_html(user_title)  # 清理标题中的HTML
            
            db = SessionLocal()
            try:
                link = Link(
                    user_id=user_id,
                    url=url,
                    title=user_title,
                    is_read=False
                )
                db.add(link)
                db.commit()
                db.refresh(link)
                link_id = link.id
                
                # 在后台异步生成标题
                if not user_title:
                    self._update_title_async(url, link_id)
                
                return f"✅ 链接已保存！\n🔗 ID: {link_id}\n📝 标题: {user_title if user_title else '生成中...'}"
            finally:
                db.close()
        except Exception as e:
            logging.error(f"保存链接时发生错误: {e}")
            return "❌ 保存链接时发生错误"
    
    async def _update_title_async(self, url: str, link_id: int) -> None:
        """异步更新链接标题"""
        try:
            # 尝试获取并生成标题
            title = None
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            # 使用 AI 服务生成标题
                            title = await self.ai_service.generate_title(url, content)
            except Exception as e:
                logging.error(f"生成标题时发生错误: {e}")
                return
            
            if title:
                title = self.clean_html(title)
                # 更新数据库中的标题
                db = SessionLocal()
                try:
                    link = db.query(Link).filter(Link.id == link_id).first()
                    if link:
                        link.title = title
                        db.commit()
                finally:
                    db.close()
        except Exception as e:
            logging.error(f"异步更新标题时发生错误: {e}")

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

    def get_unread_links(self, user_id: int, limit: int = 5) -> List[Link]:
        """
        获取指定用户的最近未读链接，最多返回 limit 条
        如果未读链接不足 limit 条，则全部展示
        """
        db = SessionLocal()
        try:
            return (db.query(Link)
                    .filter(Link.is_read == False, Link.user_id == user_id)
                    .order_by(Link.created_at.desc())
                    .limit(limit)
                    .all())
        finally:
            db.close()

    async def generate_summary(self, url: str) -> str:
        """生成链接内容的摘要"""
        try:
            # 获取网页内容
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return "无法获取网页内容"
                    html_content = await response.text()

            # 解析网页内容
            soup = BeautifulSoup(html_content, 'html.parser')
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            # 获取纯文本
            text = soup.get_text()
            
            # 清理文本：移除多余空白
            lines = (line.strip() for line in text.splitlines())
            text = ' '.join(line for line in lines if line)
            
            # 使用 AI 生成摘要，限制输入长度
            summary = await self.ai_service.generate_summary(url, text[:5000])
            # 确保返回纯文本
            if summary:
                # 移除所有可能的HTML标签
                summary = re.sub(r'<[^>]+>', '', summary)
                # 移除多余的空白字符
                summary = ' '.join(summary.split())
            return summary
        except Exception as e:
            logging.error(f"生成摘要失败: {e}")
            return "生成摘要时发生错误"
