# views.py
import wx
from models import Task
from calendar_view import CalendarDialog
from dragdrop import bind_drag, bind_drop
import uuid


# =========================
# Task Card
# =========================

class TaskCard(wx.Panel):
    def __init__(self, parent, task, controller):
        super().__init__(parent, style=wx.BORDER_SIMPLE)
        self.task = task
        self.controller = controller

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label=task.name)
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        due = wx.StaticText(self, label=f"Due: {task.due if task.due else '-'}")

        memo = wx.StaticText(self, label=task.memo)

        vbox.Add(title, 0, wx.ALL, 5)
        vbox.Add(due, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        if task.memo:
            vbox.Add(memo, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.SetSizer(vbox)

        # Drag
        bind_drag(self, task)


# =========================
# Add Task Dialog
# =========================

class AddTaskDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Add Task", size=(400, 300))

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Name
        vbox.Add(wx.StaticText(self, label="Task Name"), 0, wx.ALL, 5)
        self.name_ctrl = wx.TextCtrl(self)
        vbox.Add(self.name_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        # Due
        hbox_due = wx.BoxSizer(wx.HORIZONTAL)
        self.due_ctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        btn_cal = wx.Button(self, label="📅")
        hbox_due.Add(self.due_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_due.Add(btn_cal, 0)

        vbox.Add(wx.StaticText(self, label="Due Date"), 0, wx.ALL, 5)
        vbox.Add(hbox_due, 0, wx.EXPAND | wx.ALL, 5)

        # Memo
        vbox.Add(wx.StaticText(self, label="Memo"), 0, wx.ALL, 5)
        self.memo_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        vbox.Add(self.memo_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(vbox)

        # Events
        btn_cal.Bind(wx.EVT_BUTTON, self.on_calendar)

    def on_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.due_ctrl.SetValue(dlg.get_date())
        dlg.Destroy()

    def get_data(self):
        return {
            "name": self.name_ctrl.GetValue(),
            "due": self.due_ctrl.GetValue(),
            "memo": self.memo_ctrl.GetValue()
        }


# =========================
# Kanban View
# =========================

class KanbanView(wx.Frame):
    def __init__(self, controller):
        super().__init__(None, title="Kanban Board", size=(1200, 700))
        self.controller = controller

        self.columns = {}

        self.build_ui()
        self.refresh()

    # ---------------------
    # UI
    # ---------------------

    def build_ui(self):
        panel = wx.Panel(self)
        main_vbox = wx.BoxSizer(wx.VERTICAL)

        # Toolbar
        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label="+ Add Task")
        toolbar.Add(btn_add, 0, wx.ALL, 5)
        main_vbox.Add(toolbar, 0, wx.EXPAND)

        # Board
        self.board_panel = wx.Panel(panel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        todo = self.create_column(self.board_panel, "To Do", "todo")
        doing = self.create_column(self.board_panel, "Doing", "doing")
        done = self.create_column(self.board_panel, "Done", "done")

        self.columns["todo"] = todo
        self.columns["doing"] = doing
        self.columns["done"] = done

        hbox.Add(todo["panel"], 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(doing["panel"], 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(done["panel"], 1, wx.EXPAND | wx.ALL, 5)

        self.board_panel.SetSizer(hbox)
        main_vbox.Add(self.board_panel, 1, wx.EXPAND)

        panel.SetSizer(main_vbox)

        # Events
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_task)

    # ---------------------
    # Column
    # ---------------------

    def create_column(self, parent, title, status):
        panel = wx.Panel(parent, style=wx.BORDER_SIMPLE)
        vbox = wx.BoxSizer(wx.VERTICAL)

        title_lbl = wx.StaticText(panel, label=title)
        title_lbl.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(title_lbl, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        task_container = wx.Panel(panel)
        task_sizer = wx.BoxSizer(wx.VERTICAL)
        task_container.SetSizer(task_sizer)

        vbox.Add(task_container, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox)

        # Drop
        bind_drop(task_container, status, self.controller, self.refresh)

        return {
            "panel": panel,
            "task_container": task_container,
            "task_sizer": task_sizer,
            "status": status
        }

    # ---------------------
    # Events
    # ---------------------

    def on_add_task(self, event):
        dlg = AddTaskDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_data()

            task = Task(
                id=str(uuid.uuid4()),
                name=data["name"],
                due=data["due"],
                memo=data["memo"],
                status="todo"
            )

            self.controller.add_task(task)
            self.refresh()

        dlg.Destroy()

    # ---------------------
    # Refresh
    # ---------------------

    def refresh(self):
        # Clear
        for col in self.columns.values():
            col["task_sizer"].Clear(True)

        # Draw
        for task in self.controller.get_tasks():
            col = self.columns.get(task.status)
            if not col:
                continue

            card = TaskCard(col["task_container"], task, self.controller)
            col["task_sizer"].Add(card, 0, wx.EXPAND | wx.ALL, 5)

        # Layout
        for col in self.columns.values():
            col["task_container"].Layout()
            col["panel"].Layout()

        self.Layout()
