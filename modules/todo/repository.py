from modules.todo.models import Todo
from datetime import datetime
from threading import Lock

class TodoRepository:
    def __init__(self):
        self.todos = {}
        self.next_id = 1
        self.lock = Lock()
    
    def add(self, create_time: datetime, end_time, todo_name: str) -> Todo:
        with self.lock:
            todo = Todo(
                todo_id=self.next_id,
                create_time=create_time,
                end_time=end_time,
                todo_name=todo_name
            )
            self.todos[self.next_id] = todo
            self.next_id += 1
        return todo
    
    def get(self, todo_id: int):
        return self.todos.get(todo_id)
    
    def mark_as_done(self, todo_id: int) -> bool:
        todo = self.get(todo_id)
        if todo and todo.status != "completed":
            todo.status = "completed"
            return True
        return False
    
    def delete(self, todo_id: int) -> bool:
        if todo_id in self.todos:
            del self.todos[todo_id]
            return True
        return False
    
    def get_pending(self):
        return [todo for todo in self.todos.values() if todo.status == "pending"]
    
    def get_today_tasks(self, today):
        """
        返回截止日期为 today 的任务列表
        """
        return [todo for todo in self.todos.values() 
                if todo.end_time and todo.end_time.date() == today] 