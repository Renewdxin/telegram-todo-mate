from datetime import datetime

from sqlalchemy import Column, Integer, Text, Boolean, DateTime, BigInteger

from modules.base_model import Base


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 确保有主键
    user_id = Column(BigInteger, nullable=False)  # Telegram 用户 ID
    url = Column(Text, nullable=False)  # 链接地址
    title = Column(Text)  # 链接标题（可选）
    is_read = Column(Boolean, default=False)  # 是否已读
    summary = Column(Text)  # AI 生成的摘要（可选）
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    read_at = Column(DateTime)  # 阅读时间

    def __repr__(self):
        return f"<Link(id={self.id}, url={self.url}, is_read={self.is_read})>"

    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'url': self.url,
            'title': self.title,
            'is_read': self.is_read,
            'summary': self.summary,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'read_at': self.read_at.strftime('%Y-%m-%d %H:%M:%S') if self.read_at else None
        }
