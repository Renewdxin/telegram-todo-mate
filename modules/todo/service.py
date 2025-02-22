from datetime import datetime
from bot.config import TIMEZONE
from modules.todo.dao import TodoDAO

def parse_todo_input(text: str):
    """
    解析用户输入的待办事项内容。
    
    支持以下格式：
    1. "YYYY-MM-DD HH:MM, todo内容" —— 用户提供截止时间，必须符合格式要求
       如果只填写日期（例如 "2025-01-14"），则默认补全为 "2025-01-14 18:00"
    2. "/todo todo内容" —— 表示无截止时间
    3. 其他格式默认没有截止时间，将整个文本作为任务内容
    """
    if ',' in text:
        parts = text.split(',', 1)
        possible_time = parts[0].strip()
        todo_content = parts[1].strip()
        if ' ' not in possible_time:
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
            raise ValueError("截止时间格式错误，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM 格式")
    
    if text.strip().startswith("/todo"):
        todo_content = text.strip()[len("/todo"):].strip()
        return None, todo_content

    return None, text.strip()

def create_todo(text: str):
    """创建待办事项"""
    try:
        end_time, todo_content = parse_todo_input(text)
    except ValueError as err:
        raise Exception(str(err))
    
    create_time = datetime.now(TIMEZONE)
    return TodoDAO.create(todo_content, create_time, end_time)

def modify_end_time(todo_id: int, new_end_time_str: str) -> bool:
    """
    修改指定待办事项的截止时间
    
    Args:
        todo_id: 待办事项ID
        new_end_time_str: 新的截止时间字符串，格式为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM
        
    Returns:
        bool: 修改是否成功
        
    Raises:
        ValueError: 当截止时间格式错误或早于当前时间时抛出
    """
    if len(new_end_time_str.strip()) == 10:
        new_end_time_str += " 18:00"
    try:
        new_end_time = datetime.strptime(new_end_time_str, "%Y-%m-%d %H:%M")
        new_end_time = TIMEZONE.localize(new_end_time)
        
        # 检查新的截止时间是否晚于当前时间
        current_time = datetime.now(TIMEZONE)
        if new_end_time <= current_time:
            raise ValueError("新的截止时间必须晚于当前时间")
            
    except ValueError as e:
        if str(e) == "新的截止时间必须晚于当前时间":
            raise
        raise ValueError("截止时间格式错误，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM 格式")
    
    return TodoDAO.update_end_time(todo_id, new_end_time)

def complete_todo(todo_id: int) -> bool:
    """完成待办事项"""
    return TodoDAO.update_status(todo_id, 'completed')

def delete_todo(todo_id: int) -> bool:
    """删除待办事项"""
    return TodoDAO.delete(todo_id)

def get_pending_todos():
    """获取所有未完成的待办事项"""
    return TodoDAO.get_pending_todos()

def get_today_todos():
    """获取今天的待办事项"""
    today = datetime.now(TIMEZONE).date()
    return TodoDAO.get_today_todos(today) 