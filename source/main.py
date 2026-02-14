# main.py
import wx

from models import Board
from storage import Storage
from controllers import KanbanController
from views import KanbanView
from gantt import GanttView


# =========================
# Application
# =========================

class KanbanApp(wx.App):
    def OnInit(self):
        # Model
        board = Board()

        # Storage
        storage = Storage("kanban.db")

        # Controller (Single Instance)
        controller = KanbanController(board, storage)

        # Load persisted data
        controller.load()

        # View
        self.view = KanbanView(controller)
        self.view.Show()

        # Optional: Gantt
        # gantt = GanttView(controller)
        # gantt.Show()

        self.SetTopWindow(self.view)
        return True


# =========================
# Entry Point
# =========================

if __name__ == "__main__":
    app = KanbanApp(False)
    app.MainLoop()
