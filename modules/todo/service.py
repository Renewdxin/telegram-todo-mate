from datetime import datetime
from bot.config import TIMEZONE
from modules.todo.dao import TodoDAO

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

def create_todo(text: str):
    """
    创建待办事项。
    所有错误都会在这里处理，确保不会创建无效的待办事项。
    """
    try:
        end_time, todo_content = parse_todo_input(text)
        if not todo_content:
            raise ValueError("任务内容不能为空")
            
        create_time = datetime.now(TIMEZONE)
        return TodoDAO.create(todo_content, create_time, end_time)
    except Exception as e:
        # 确保所有错误都在这里被捕获，不会创建无效数据
        raise Exception(str(e))

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
    todo = TodoDAO.get_by_id(todo_id)
    if not todo:
        raise ValueError("任务不存在")
    if todo.status == 'completed':
        raise ValueError("任务已经完成")
    return TodoDAO.update_status(todo_id, 'completed')

def delete_todo(todo_id: int) -> bool:
    """删除待办事项"""
    todo = TodoDAO.get_by_id(todo_id)
    if not todo:
        raise ValueError("任务不存在")
    return TodoDAO.delete(todo_id)

def get_pending_todos():
    """获取所有未完成的待办事项（按创建时间倒序）"""
    return TodoDAO.get_pending_todos()

def get_today_todos():
    """获取今天的待办事项"""
    today = datetime.now(TIMEZONE).date()
    return TodoDAO.get_today_todos(today)

def format_todo_list(todos, show_type: str = "all") -> str:
    """
    格式化待办事项列表，返回可读性好的文本。
    
    Args:
        todos: 待办事项列表
        show_type: 显示类型，"all" 表示所有任务，"pending" 表示未完成任务
    """
    if not todos:
        return "📝 暂无待办事项"
    
    title = "📝 所有待办事项：" if show_type == "all" else "📝 未完成的待办事项："
    result = f"{title}\n"
    
    for todo in todos:
        # 基础信息
        task_info = (
            f"\n🔸 任务 <code>{todo.todo_id}</code>: {todo.todo_name}\n"
            f"   创建于: {todo.create_time.strftime('%Y-%m-%d %H:%M')}"
        )
        
        # 如果有截止时间，添加截止时间信息
        if todo.end_time:
            task_info += f"\n   截止时间: {todo.end_time.strftime('%Y-%m-%d %H:%M')}"
            
        # 如果是显示所有任务，才显示状态
        if show_type == "all":
            if todo.status == 'completed':
                task_info += "\n   状态: ✅ 已完成"
            else:
                task_info += "\n   状态: ⏳ 进行中"
            
        result += task_info
        
    return result

def get_all_todos():
    """获取所有待办事项（按创建时间倒序）"""
    return TodoDAO.get_all_todos() 