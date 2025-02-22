from datetime import datetime
from sqlalchemy.orm import Session
from modules.todo.models import Todo, SessionLocal

class TodoDAO:
    @staticmethod
    def create(todo_name: str, create_time: datetime, end_time: datetime = None) -> Todo:
        todo = Todo(
            todo_name=todo_name,
            create_time=create_time,
            end_time=end_time
        )
        db = SessionLocal()
        try:
            db.add(todo)
            db.commit()
            db.refresh(todo)
            return todo
        finally:
            db.close()

    @staticmethod
    def get_by_id(todo_id: int) -> Todo:
        db = SessionLocal()
        try:
            return db.query(Todo).filter(Todo.todo_id == todo_id).first()
        finally:
            db.close()

    @staticmethod
    def update_status(todo_id: int, status: str) -> bool:
        db = SessionLocal()
        try:
            todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
            if todo:
                todo.status = status
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def update_end_time(todo_id: int, new_end_time: datetime) -> bool:
        db = SessionLocal()
        try:
            todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
            if todo:
                todo.end_time = new_end_time
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def delete(todo_id: int) -> bool:
        db = SessionLocal()
        try:
            todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
            if todo:
                db.delete(todo)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def get_pending_todos():
        db = SessionLocal()
        try:
            return db.query(Todo).filter(Todo.status != 'completed').all()
        finally:
            db.close()

    @staticmethod
    def get_today_todos(today_date):
        db = SessionLocal()
        try:
            return db.query(Todo).filter(
                Todo.end_time.isnot(None)
            ).filter(
                Todo.end_time.cast(Date) == today_date
            ).all()
        finally:
            db.close() 