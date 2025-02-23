from modules.base_model import Base
from sqlalchemy import Column, String, DateTime, Text, Boolean, BigInteger
from datetime import datetime

class Link(Base):
    __tablename__ = 'links'
    
    user_id = Column(BigInteger, nullable=False)  # Telegram 用户 ID
    url = Column(Text, nullable=False)           # 链接地址
    title = Column(Text, nullable=True)          # 链接标题
    is_read = Column(Boolean, default=False)     # 是否已读
    summary = Column(Text, nullable=True)        # AI 生成的摘要
    read_at = Column(DateTime, nullable=True)    # 阅读时间

    def __repr__(self):
        return f"<Link(id={self.id}, url={self.url}, is_read={self.is_read})>"
