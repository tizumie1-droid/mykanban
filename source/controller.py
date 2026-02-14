# controllers.py
from models import Task


class KanbanController:
    def __init__(self, board, storage):
        self.board = board
        self.storage = storage

    # ---------------------
    # CRUD
    # ---------------------

    def add_task(self, task: Task):
        self.board.tasks.append(task)
        self.save()

    def get_tasks(self):
        return list(self.board.tasks)

    def get_task_by_id(self, task_id: str):
        for t in self.board.tasks:
            if t.id == task_id:
                return t
        return None

    def update_task(self, task: Task):
        # In-memory object reference update
        self.save()

    def delete_task(self, task_id: str):
        self.board.tasks = [t for t in self.board.tasks if t.id != task_id]
        self.save()

    # ---------------------
    # Persistence
    # ---------------------

    def save(self):
        self.storage.save_tasks(self.board.tasks)

    def load(self):
        self.board.tasks = self.storage.load_tasks()
