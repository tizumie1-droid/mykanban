import uuid
from dataclasses import dataclass, field
from typing import List

@dataclass
class Task:
    name: str
    due: str
    memo: str
    status: str = "todo"
    start_date: str = None
    completed_date: str = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

class Board:
    def __init__(self):
        self.tasks: List[Task] = []
    
    def add_task(self, task:Task):
        self.tasks.append(task)
    
    def remove_task(self, task:Task):
        self.tasks = [t for t in self.tasks if t.id != task.id]

