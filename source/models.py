# models.py
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Task:
    id: str
    name: str
    due: Optional[str] = None   # YYYY-MM-DD
    memo: str = ""
    status: str = "todo"       # todo / doing / done
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Board:
    def __init__(self):
        # Single Source of Truth
        self.tasks: List[Task] = []
