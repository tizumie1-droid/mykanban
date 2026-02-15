# controllers.py
from models import Task


class KanbanController:
    def __init__(self, board, storage):
        self.board = board
        self.storage = storage

    # ===== Task Ops =====
    def add_task(self, task: Task):
        self.board.add_task(task)
        self.save()
        return task

    def update_task(self, task):
        self.save()

    def delete_task(self, task):
        self.board.remove_task(task)
        self.save()

    def get_tasks(self):
        return list(self.board.tasks)

    def get_task_by_id(self, tid):
        for t in self.board.tasks:
            if t.id == tid:
                return t
        return None

    # ===== Persistence =====
    def save(self):
        self.storage.save_tasks(self.board.tasks)

    def load(self):
        self.board.tasks = self.storage.load_tasks()
