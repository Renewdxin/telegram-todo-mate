from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from modules.base_model import Base


class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # 用户ID
    todo_name = Column(Text, nullable=False)  # 任务内容
    status = Column(String(20), default="pending")  # 状态：pending（待办）、completed（已完成）
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    end_time = Column(DateTime, nullable=True)  # 截止时间
    completed_at = Column(DateTime, nullable=True)  # 完成时间

    def __repr__(self):
        return f"<Todo(id={self.id}, todo_name={self.todo_name}, status={self.status})>"

    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'todo_name': self.todo_name,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None
        }
