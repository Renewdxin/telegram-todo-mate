import logging
from datetime import datetime, date

from sqlalchemy import Date

from modules.database import SessionLocal
from modules.todo.models import Todo


class TodoDAO:
    @staticmethod
    def create(todo_name: str, create_time: datetime, end_time: datetime = None) -> Todo:
        """
        创建新的待办事项。
        如果发生任何错误，会回滚事务并抛出异常。
        """
        db = SessionLocal()
        try:
            todo = Todo(
                todo_name=todo_name,
                create_time=create_time,
                end_time=end_time
            )
            db.add(todo)
            db.commit()
            db.refresh(todo)
            return todo
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def get_by_id(todo_id: int) -> Todo:
        """获取指定ID的待办事项"""
        db = SessionLocal()
        try:
            return db.query(Todo).filter(Todo.todo_id == todo_id).first()
        finally:
            db.close()

    @staticmethod
    def update_status(todo_id: int, status: str) -> bool:
        """
        更新待办事项状态。
        如果任务不存在或发生错误，返回False。
        """
        db = SessionLocal()
        try:
            todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
            if todo:
                todo.status = status
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def update_end_time(todo_id: int, new_end_time: datetime) -> bool:
        """
        更新待办事项的截止时间。
        如果任务不存在或发生错误，返回False。
        """
        db = SessionLocal()
        try:
            todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
            if not todo:
                return False
            if todo.status == 'completed':
                raise ValueError("已完成的任务不能修改截止时间")
            todo.end_time = new_end_time
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def delete(todo_id: int) -> bool:
        """
        删除待办事项。
        如果任务不存在或发生错误，返回False。
        """
        db = SessionLocal()
        try:
            todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
            if todo:
                db.delete(todo)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def get_pending_todos():
        """获取所有未完成的待办事项，按截止时间和创建时间排序"""
        db = SessionLocal()
        try:
            return (db.query(Todo)
                    .filter(Todo.status == 'pending')  # 明确指定状态为pending
                    .order_by(Todo.end_time.asc().nullslast(),  # 先按截止时间排序，没有截止时间的放最后
                              Todo.create_time.desc())  # 然后按创建时间倒序
                    .all())
        except Exception as e:
            logging.error(f"获取待办事项失败: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def get_today_todos(today_date: date):
        """获取指定日期的待办事项"""
        db = SessionLocal()
        try:
            return db.query(Todo).filter(
                Todo.end_time.isnot(None),
                Todo.end_time.cast(Date) == today_date
            ).all()
        finally:
            db.close()

    @staticmethod
    def get_all_todos():
        """获取所有待办事项，按状态和创建时间排序"""
        db = SessionLocal()
        try:
            return (db.query(Todo)
                    .order_by(Todo.status.desc(),  # pending 排在前面，completed 排在后面
                              Todo.create_time.desc())  # 按创建时间倒序
                    .all())
        except Exception as e:
            logging.error(f"获取所有待办事项失败: {e}")
            return []
        finally:
            db.close()
