import wx
from models import Board
from storage import Storage
from controllers import KanbanController
from views import KanbanView
from gantt import GanttView

# == Main Application ==

class KanbanApp(wx.App):
    def OnInit(self):
        # Model
        board = Board()
        # Storage
        storage = Storage("C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\kanban.db")
        # Controller
        controller = KanbanController(board, storage)
        controller.load()
        # View
        self.view = KanbanView(controller)
        self.view.Show()
        # optional: Gantt
        # gantt = GanttView(controller)
        # gantt.Show()

        self.SetTopWindow(self.view)
        return True
    
# == Entry Point ==

if __name__ == "__main__":
    app = KanbanApp(False)
    app.MainLoop()