from sqlalchemy.orm import Session
from modules.database import SessionLocal
from modules.link.models import Link
from datetime import datetime
from typing import List, Optional

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

    def get_unread_links(self, user_id: int) -> List[Link]:
        """获取用户的所有未读链接"""
        return self.db.query(Link)\
            .filter(Link.user_id == user_id, Link.is_read == False)\
            .order_by(Link.created_at.desc())\
            .all()

    def get_random_unread_link(self, user_id: int) -> Optional[Link]:
        """随机获取一个未读链接"""
        return self.db.query(Link)\
            .filter(Link.user_id == user_id, Link.is_read == False)\
            .order_by(self.db.func.random())\
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
        return self.db.query(Link)\
            .filter(Link.user_id == user_id, Link.is_read == False)\
            .count()
