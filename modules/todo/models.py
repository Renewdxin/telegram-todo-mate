from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, String
from modules.base_model import Base


class Todo(Base):
    __tablename__ = 'todos'

    todo_id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    todo_name = Column(Text, nullable=False)
    status = Column(String(20), default='pending')

    def __repr__(self):
        return f"<Todo(id={self.todo_id}, todo_name={self.todo_name}, status={self.status})>"

    def to_dict(self):
        """将对象转换为字典"""
        return {
            'todo_id': self.todo_id,
            'todo_name': self.todo_name,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None
        }
