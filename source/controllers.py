from models import Task
import re
from datetime import datetime
import os


class KanbanController:
    def __init__(self, board, storage):
        self.board = board
        self.storage = storage
    
    def add_task(self, task:Task):
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
    
    def save(self):
        self.storage.save_tasks(self.board.tasks)
    
    def load(self):
        self.board.tasks = self.storage.load_tasks()
    
    def refresh_from_md(self):
        """
        全タスクの md を読み込んで反映
        """
        for task in self.board.tasks:
            self.update_task_from_md(task)
        self.save()

    def update_task_from_md(self, task):
        safe_name = task.name.replace('/', '_').replace('\\', '_')
        filename = os.path.join("C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md\\todo", f"{safe_name}.md")
        if not os.path.exists(filename):
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                text = f.read()
        except:
            return

        # ---------- セクション抽出 ----------
        def extract(section):
            pattern = rf"## {section}\n(.*?)(?=\n## |\Z)"
            m = re.search(pattern, text, re.S)
            if not m:
                return ""
            return m.group(1).strip()

        start_raw = extract("Start")
        due_raw = extract("Due")
        completed_raw = extract("Completed")
        memo_raw = extract("Memo")

        # ---------- 反映 ----------
        start = parse_date(start_raw)
        due = parse_date(due_raw)
        completed = parse_date(completed_raw)

        if start:
            task.start_date = start

        if due:
            task.due = due

        if completed:
            task.completed_date = completed
            task.status = "complete"   # 完了扱いに移動

        if memo_raw:
            task.memo = memo_raw.strip()

def parse_date(s: str):
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date().isoformat()
    except:
        return None