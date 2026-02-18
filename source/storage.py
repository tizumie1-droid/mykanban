import sqlite3
from models import Task

class Storage:
    def __init__(self, db_path="C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\kanban.db"):
        self.db_path = db_path
        self._init_db()

    # == Init ==
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT,
                due TEXT,
                memo TEXT,
                status TEXT,
                start_date TEXT,
                completed_date TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    # == Save & Load ==
    def save_tasks(self, tasks):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Clear existing tasks
        cur.execute("DELETE FROM tasks")

        for t in tasks:
            cur.execute(
                """
                INSERT INTO tasks (id, name, due, memo, status, start_date, completed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t.id,
                    t.name,
                    t.due,
                    t.memo,
                    t.status,
                    t.start_date,
                    t.completed_date,
                )
            )
        conn.commit()
        conn.close()

    def load_tasks(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT id, name, due, memo, status, start_date, completed_date FROM tasks")
        rows = cur.fetchall()

        tasks = []
        for row in rows:
            tasks.append(Task(
                id = row[0],
                name = row[1],
                due = row[2],
                memo = row[3],
                status = row[4],
                start_date = row[5],
                completed_date = row[6],
            ))

        conn.close()
        return tasks