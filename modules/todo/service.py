"""
待办事项业务逻辑
"""

from datetime import datetime
import pytz
from bot.config import TIMEZONE
from modules.todo.models import Todo

# 内存中存储任务，正式项目中可替换为数据库
todos = {}
_next_todo_id = 1

def parse_todo_input(text: str):
    """
    解析用户输入的待办事项内容。
    
    支持以下格式：
    1. "YYYY-MM-DD HH:MM, todo内容" —— 用户提供截止时间，必须符合格式要求
       如果只填写日期（例如 "2025-01-14"），则默认补全为 "2025-01-14 18:00"
    2. "/todo todo内容" —— 表示无截止时间
    3. 其他格式默认没有截止时间，将整个文本作为任务内容
    
    若逗号分隔的形式中截止时间格式错误，则抛出 ValueError 异常。
    """
    if ',' in text:
        # 尝试按逗号分割
        parts = text.split(',', 1)
        possible_time = parts[0].strip()
        todo_content = parts[1].strip()
        # 如果截止时间只填写了日期（例如 "2025-01-14"），则默认补全为 "2025-01-14 18:00"
        if ' ' not in possible_time:
            possible_time += " 18:00"
        try:
            end_time = datetime.strptime(possible_time, "%Y-%m-%d %H:%M")
            # 根据配置的时区转换
            end_time = TIMEZONE.localize(end_time)
            return end_time, todo_content
        except ValueError:
            raise ValueError("截止时间格式错误，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM 格式")
    # 如果以 /todo 开头，则表示无截止时间
    if text.strip().startswith("/todo"):
        todo_content = text.strip()[len("/todo"):].strip()
        return None, todo_content

    # 默认认为没有截止时间，整个文本作为任务内容
    return None, text.strip()

def create_todo(text: str):
    """
    创建待办事项。
    自动记录任务创建时间（按配置的时区），并解析输入中的截止时间（可选）。
    """
    global _next_todo_id
    try:
        end_time, todo_content = parse_todo_input(text)
    except ValueError as err:
        raise Exception(str(err))
    
    creation_time = datetime.now(TIMEZONE)
    todo = Todo(
        todo_id=_next_todo_id,
        todo_name=todo_content,
        creation_time=creation_time,
        end_time=end_time
    )
    todos[_next_todo_id] = todo
    _next_todo_id += 1
    return todo

def modify_end_time(todo_id: int, new_end_time_str: str) -> bool:
    """
    修改指定待办事项的截止时间。
    new_end_time_str 必须为 "YYYY-MM-DD HH:MM" 格式。如果只输入 "YYYY-MM-DD"，默认按18:00处理。
    """
    # 如果没有提供时分，默认补上 " 18:00"
    if len(new_end_time_str.strip()) == 10:
        new_end_time_str += " 18:00"
    try:
        new_end_time = datetime.strptime(new_end_time_str, "%Y-%m-%d %H:%M")
        new_end_time = TIMEZONE.localize(new_end_time)
    except ValueError:
        return False
    if todo_id in todos:
        todos[todo_id].end_time = new_end_time
        return True
    return False

def complete_todo(todo_id: int) -> bool:
    if todo_id in todos and todos[todo_id].status != 'completed':
        todos[todo_id].status = 'completed'
        return True
    return False

def delete_todo(todo_id: int) -> bool:
    if todo_id in todos:
        del todos[todo_id]
        return True
    return False

def get_pending_todos():
    return [todo for todo in todos.values() if todo.status != 'completed']

def get_today_todos():
    today = datetime.now(TIMEZONE).date()
    return [todo for todo in todos.values() if todo.end_time and todo.end_time.date() == today] 