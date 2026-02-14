# storage.py
import sqlite3
from models import Task


class Storage:
    def __init__(self, db_path="kanban.db"):
        self.db_path = db_path
        self._init_db()

    # ---------------------
    # Init
    # ---------------------

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
                end_date TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    # ---------------------
    # Save
    # ---------------------

    def save_tasks(self, tasks):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("DELETE FROM tasks")

        for t in tasks:
            cur.execute(
                """
                INSERT INTO tasks (id, name, due, memo, status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t.id,
                    t.name,
                    t.due,
                    t.memo,
                    t.status,
                    t.start_date,
                    t.end_date,
                )
            )

        conn.commit()
        conn.close()

    # ---------------------
    # Load
    # ---------------------

    def load_tasks(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT id, name, due, memo, status, start_date, end_date FROM tasks")
        rows = cur.fetchall()

        tasks = []
        for r in rows:
            tasks.append(Task(
                id=r[0],
                name=r[1],
                due=r[2],
                memo=r[3],
                status=r[4],
                start_date=r[5],
                end_date=r[6],
            ))

        conn.close()
        return tasks
