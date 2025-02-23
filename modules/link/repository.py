from datetime import datetime
from typing import Optional

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from modules.database import SessionLocal
from modules.link.models import Link


class LinkRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def __del__(self):
        self.db.close()

    def create(self, user_id: int, url: str, title: Optional[str] = None) -> Link:
        """创建新的链接记录"""
        link = Link(
            user_id=user_id,
            url=url,
            title=title,
            is_read=False
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def get_by_id(self, link_id: int) -> Optional[Link]:
        """通过ID获取链接"""
        return self.db.query(Link).filter(Link.id == link_id).first()

    def get_unread_links(self, user_id: int, limit: int = None):
        """获取未读链接列表，默认按创建时间倒序排列"""
        query = self.db.query(Link) \
            .filter(Link.user_id == user_id, Link.is_read == False) \
            .order_by(desc(Link.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_random_unread_link(self, user_id: int) -> Optional[Link]:
        """随机获取一个未读链接"""
        return self.db.query(Link) \
            .filter(Link.user_id == user_id, Link.is_read == False) \
            .order_by(func.random()) \
            .first()

    def mark_as_read(self, link_id: int) -> bool:
        """将链接标记为已读"""
        link = self.get_by_id(link_id)
        if not link:
            return False

        link.is_read = True
        link.read_at = datetime.utcnow()
        self.db.commit()
        return True

    def update_summary(self, link_id: int, summary: str) -> bool:
        """更新链接的AI摘要"""
        link = self.get_by_id(link_id)
        if not link:
            return False

        link.summary = summary
        self.db.commit()
        return True

    def get_unread_count(self, user_id: int) -> int:
        """获取用户未读链接数量"""
        return self.db.query(func.count(Link.id)) \
            .filter(Link.user_id == user_id, Link.is_read == False) \
            .scalar()

    def get_latest_unread_link(self, user_id: int) -> Link:
        """获取最新添加的未读链接"""
        return self.db.query(Link) \
            .filter_by(user_id=user_id, is_read=False) \
            .order_by(desc(Link.created_at)) \
            .first()
