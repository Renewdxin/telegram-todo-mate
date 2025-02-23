from datetime import datetime, timedelta
from typing import List, Optional

from bot.config import TIMEZONE
from modules.todo.dao import TodoDAO
from modules.todo.models import Todo
from modules.database import SessionLocal


def parse_todo_input(text: str):
    """
    解析用户输入的待办事项内容。
    
    支持以下格式：
    1. "YYYY-MM-DD [HH:MM], todo内容" —— 用户提供截止时间
       如果只填写日期（例如 "2025-01-14"），则默认为 18:00
    2. "/todo todo内容" —— 表示无截止时间
    3. 其他格式默认没有截止时间，将整个文本作为任务内容
    """
    if ',' in text:
        parts = text.split(',', 1)
        possible_time = parts[0].strip()
        todo_content = parts[1].strip()

        # 如果只提供日期，补充默认时间
        if len(possible_time) == 10:  # YYYY-MM-DD
            possible_time += " 18:00"

        try:
            end_time = datetime.strptime(possible_time, "%Y-%m-%d %H:%M")
            end_time = TIMEZONE.localize(end_time)

            # 检查截止时间是否晚于当前时间
            current_time = datetime.now(TIMEZONE)
            if end_time <= current_time:
                raise ValueError("截止时间必须晚于当前时间")

            return end_time, todo_content
        except ValueError as e:
            if str(e) == "截止时间必须晚于当前时间":
                raise
            raise ValueError("截止时间格式错误，请使用 YYYY-MM-DD [HH:MM] 格式，时间可选，默认为 18:00")

    if text.strip().startswith("/todo"):
        todo_content = text.strip()[len("/todo"):].strip()
        return None, todo_content

    return None, text.strip()


def create_todo(todo_name: str, end_time: Optional[datetime] = None) -> Todo:
    """创建新的待办事项"""
    db = SessionLocal()
    try:
        todo = Todo(
            todo_name=todo_name,
            end_time=end_time,
            status='pending'
        )
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception as e:
        db.rollback()
        raise Exception(f"创建待办事项失败: {str(e)}")
    finally:
        db.close()


def modify_end_time(todo_id: int, new_end_time_str: str) -> bool:
    """
    修改指定待办事项的截止时间。
    所有错误检查都在这里完成，确保数据的一致性。
    
    Args:
        todo_id: 待办事项ID
        new_end_time_str: 新的截止时间字符串，格式为 YYYY-MM-DD [HH:MM]
        
    Raises:
        ValueError: 当发生以下情况时抛出：
            - 任务不存在
            - 任务已完成
            - 时间格式错误
            - 新时间早于当前时间
    """
    # 先检查任务是否存在
    todo = TodoDAO.get_by_id(todo_id)
    if not todo:
        raise ValueError("任务不存在")

    if todo.status == 'completed':
        raise ValueError("已完成的任务不能修改截止时间")

    # 处理时间格式
    if len(new_end_time_str.strip()) == 10:  # YYYY-MM-DD
        new_end_time_str += " 18:00"

    try:
        new_end_time = datetime.strptime(new_end_time_str, "%Y-%m-%d %H:%M")
        new_end_time = TIMEZONE.localize(new_end_time)

        # 检查新的截止时间是否晚于当前时间
        current_time = datetime.now(TIMEZONE)
        if new_end_time <= current_time:
            raise ValueError("新的截止时间必须晚于当前时间")

        return TodoDAO.update_end_time(todo_id, new_end_time)

    except ValueError as e:
        if str(e) in ["新的截止时间必须晚于当前时间", "任务不存在", "已完成的任务不能修改截止时间"]:
            raise
        raise ValueError("截止时间格式错误，请使用 YYYY-MM-DD [HH:MM] 格式，时间可选，默认为 18:00")


def complete_todo(todo_id: int) -> bool:
    """完成待办事项"""
    db = SessionLocal()
    try:
        todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
        if todo and todo.status != 'completed':
            todo.status = 'completed'
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise Exception(f"完成待办事项失败: {str(e)}")
    finally:
        db.close()


def delete_todo(todo_id: int) -> bool:
    """删除待办事项"""
    todo = TodoDAO.get_by_id(todo_id)
    if not todo:
        raise ValueError("任务不存在")
    return TodoDAO.delete(todo_id)


def get_pending_todos() -> List[Todo]:
    """获取未完成的待办事项"""
    db = SessionLocal()
    try:
        return db.query(Todo).filter(Todo.status == 'pending').order_by(Todo.create_time.asc()).all()
    except Exception as e:
        raise Exception(f"获取未完成待办事项失败: {str(e)}")
    finally:
        db.close()


def get_today_todos():
    """获取今天的待办事项"""
    today = datetime.now(TIMEZONE).date()
    return TodoDAO.get_today_todos(today)


def get_tomorrow_todos():
    """获取明天截止的待办事项"""
    tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)
    return TodoDAO.get_today_todos(tomorrow)


def format_todo_list(todos: List[Todo], list_type: str = "all") -> str:
    """格式化待办事项列表"""
    if not todos:
        return f"📝 没有{'未完成的' if list_type == 'pending' else ''}待办事项"
    
    result = f"📝 {'未完成的' if list_type == 'pending' else '所有'}待办事项:\n"
    
    for todo in todos:
        # 基本信息
        result += f"\n━━━━━━━━━━━━━━━\n"
        result += f"📌 <code>{todo.todo_id}</code> "
        result += "✅" if todo.status == 'completed' else "⭕️"
        result += f" {todo.todo_name}\n"
        
        # 时间信息
        result += f"⏰ 创建：{todo.create_time.strftime('%m-%d %H:%M')}"
        if todo.end_time:
            time_diff = todo.end_time - datetime.now()
            if time_diff.days >= 0:
                days = time_diff.days
                hours = time_diff.seconds // 3600
                result += f"\n⏳ 截止：{todo.end_time.strftime('%m-%d %H:%M')}"
                result += f" (还剩 {days}天{hours}小时)"
            else:
                result += f"\n⚠️ 截止：{todo.end_time.strftime('%m-%d %H:%M')} [已过期]"
    
    result += "\n━━━━━━━━━━━━━━━"
    return result


def get_all_todos() -> List[Todo]:
    """获取所有待办事项"""
    db = SessionLocal()
    try:
        return db.query(Todo).order_by(Todo.create_time.asc()).all()
    except Exception as e:
        raise Exception(f"获取所有待办事项失败: {str(e)}")
    finally:
        db.close()
