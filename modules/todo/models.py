from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Todo:
    todo_id: int
    create_time: datetime
    end_time: Optional[datetime]
    todo_name: str
    status: str = "pending"  # 状态：pending（待办）、completed（已完成） 