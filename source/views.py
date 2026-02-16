# views.py
import wx
import uuid
from models import Task
from calendar_view import CalendarDialog
from dragdrop import bind_drag, bind_drop
from gantt import GanttView
import os


# =========================
# Task Card
# =========================

class TaskCard(wx.Panel):
    def __init__(self, parent, task, controller, refresh_cb):
        super().__init__(parent, style=wx.BORDER_SIMPLE)
        self.task = task
        self.controller = controller
        self.refresh_cb = refresh_cb

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label=task.name)
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        start = wx.StaticText(self, label=f"Start: {task.start_date if task.start_date else '-'}")
        due = wx.StaticText(self, label=f"Due: {task.due if task.due else '-'}")
        memo = wx.StaticText(self, label=task.memo)

        vbox.Add(title, 0, wx.ALL, 5)
        vbox.Add(start, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        vbox.Add(due, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        if task.memo:
            vbox.Add(memo, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.SetSizer(vbox)

        # Drag
        bind_drag(self, task)

        # Right click edit
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_edit)

    def on_edit(self, event):
        dlg = EditTaskDialog(self, self.task)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_data()
            self.task.name = data["name"]
            self.task.start_date = data["start_date"]
            self.task.due = data["due"]
            self.task.memo = data["memo"]
            self.controller.update_task(self.task)
            wx.CallAfter(self.refresh_cb)
        dlg.Destroy()


# =========================
# Add Task Dialog
# =========================

class AddTaskDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Add Task", size=(420, 380))

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Name
        vbox.Add(wx.StaticText(self, label="Task Name"), 0, wx.ALL, 5)
        self.name_ctrl = wx.TextCtrl(self)
        vbox.Add(self.name_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        # Start date
        hbox_start = wx.BoxSizer(wx.HORIZONTAL)
        self.start_ctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        btn_start_cal = wx.Button(self, label="📅")
        hbox_start.Add(self.start_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_start.Add(btn_start_cal, 0)

        vbox.Add(wx.StaticText(self, label="Start Date"), 0, wx.ALL, 5)
        vbox.Add(hbox_start, 0, wx.EXPAND | wx.ALL, 5)

        # Due date
        hbox_due = wx.BoxSizer(wx.HORIZONTAL)
        self.due_ctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        btn_due_cal = wx.Button(self, label="📅")
        hbox_due.Add(self.due_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_due.Add(btn_due_cal, 0)

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

        # CheckBox
        self.md_checkbox = wx.CheckBox(self, label="Create Markdown file (タスク名.md)")
        vbox.Add(self.md_checkbox, 0, wx.ALL, 5)

        # Events
        btn_start_cal.Bind(wx.EVT_BUTTON, self.on_start_calendar)
        btn_due_cal.Bind(wx.EVT_BUTTON, self.on_due_calendar)

    def on_start_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.start_ctrl.SetValue(dlg.get_date())
        dlg.Destroy()

    def on_due_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.due_ctrl.SetValue(dlg.get_date())
        dlg.Destroy()

    def get_data(self):
        return {
            "name": self.name_ctrl.GetValue(),
            "start_date": self.start_ctrl.GetValue(),
            "due": self.due_ctrl.GetValue(),
            "memo": self.memo_ctrl.GetValue(),
            "create_md": self.md_checkbox.GetValue()
        }


# =========================
# Edit Task Dialog
# =========================

class EditTaskDialog(wx.Dialog):
    def __init__(self, parent, task: Task):
        super().__init__(parent, title="Edit Task", size=(420, 380))
        self.task = task

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Name
        vbox.Add(wx.StaticText(self, label="Task Name"), 0, wx.ALL, 5)
        self.name_ctrl = wx.TextCtrl(self, value=task.name)
        vbox.Add(self.name_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        # Start date
        hbox_start = wx.BoxSizer(wx.HORIZONTAL)
        self.start_ctrl = wx.TextCtrl(self, value=task.start_date or "", style=wx.TE_READONLY)
        btn_start_cal = wx.Button(self, label="📅")
        hbox_start.Add(self.start_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_start.Add(btn_start_cal, 0)

        vbox.Add(wx.StaticText(self, label="Start Date"), 0, wx.ALL, 5)
        vbox.Add(hbox_start, 0, wx.EXPAND | wx.ALL, 5)

        # Due date
        hbox_due = wx.BoxSizer(wx.HORIZONTAL)
        self.due_ctrl = wx.TextCtrl(self, value=task.due or "", style=wx.TE_READONLY)
        btn_due_cal = wx.Button(self, label="📅")
        hbox_due.Add(self.due_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_due.Add(btn_due_cal, 0)

        vbox.Add(wx.StaticText(self, label="Due Date"), 0, wx.ALL, 5)
        vbox.Add(hbox_due, 0, wx.EXPAND | wx.ALL, 5)

        # Memo
        vbox.Add(wx.StaticText(self, label="Memo"), 0, wx.ALL, 5)
        self.memo_ctrl = wx.TextCtrl(self, value=task.memo, style=wx.TE_MULTILINE)
        vbox.Add(self.memo_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(vbox)

        # Events
        btn_start_cal.Bind(wx.EVT_BUTTON, self.on_start_calendar)
        btn_due_cal.Bind(wx.EVT_BUTTON, self.on_due_calendar)

    def on_start_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.start_ctrl.SetValue(dlg.get_date())
        dlg.Destroy()

    def on_due_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.due_ctrl.SetValue(dlg.get_date())
        dlg.Destroy()

    def get_data(self):
        return {
            "name": self.name_ctrl.GetValue(),
            "start_date": self.start_ctrl.GetValue(),
            "due": self.due_ctrl.GetValue(),
            "memo": self.memo_ctrl.GetValue()
        }


# =========================
# Kanban View
# =========================

class KanbanView(wx.Frame):
    def __init__(self, controller):
        super().__init__(None, title="Kanban Board", size=(1300, 750))
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
        btn_gantt = wx.Button(panel, label="📊 Gantt")
        btn_completelist = wx.Button(panel, label="Complete List")
        toolbar.Add(btn_add, 0, wx.ALL, 5)
        toolbar.Add(btn_gantt, 0, wx.ALL, 5)
        toolbar.Add(btn_completelist, 0, wx.ALL, 5)
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
        hbox.Add(done["panel"], 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(doing["panel"], 1, wx.EXPAND | wx.ALL, 5)

        self.board_panel.SetSizer(hbox)
        main_vbox.Add(self.board_panel, 1, wx.EXPAND)

        panel.SetSizer(main_vbox)

        # Events
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_task)
        btn_gantt.Bind(wx.EVT_BUTTON, self.on_open_gantt)

    # ---------------------
    # Column
    # ---------------------    
    def create_column(self, parent, title, status):
        panel = wx.Panel(parent, style=wx.BORDER_SIMPLE)
        vbox = wx.BoxSizer(wx.VERTICAL)

        lbl = wx.StaticText(panel, label=title)
        lbl.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(lbl, 0, wx.ALL | wx.ALIGN_CENTER, 3)

        scroll = wx.ScrolledWindow(panel, style=wx.VSCROLL)
        scroll.SetScrollRate(0, 20)

        container = wx.Panel(scroll)
        sizer = wx.BoxSizer(wx.VERTICAL)
        container.SetSizer(sizer)

        sc_sizer = wx.BoxSizer(wx.VERTICAL)
        sc_sizer.Add(container, 1, wx.EXPAND)
        scroll.SetSizer(sc_sizer)

        vbox.Add(scroll, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(vbox)

        bind_drop(container, status, self.controller, self.refresh)

        return {
            "panel": panel,
            "scroll": scroll,
            "task_container": container,
            "task_sizer": sizer,
            "status": status
        }

    # ---------------------
    # Events
    # ---------------------

    def on_open_gantt(self, event):
        gantt = GanttView(self.controller)
        gantt.Show()

    def on_add_task(self, event):
        dlg = AddTaskDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_data()

            task = Task(
                id=str(uuid.uuid4()),
                name=data["name"],
                start_date=data["start_date"],
                due=data["due"],
                memo=data["memo"],
                status="todo"
            )

            self.controller.add_task(task)

            # =========================
            # Markdown file creation
            # =========================
            if data.get("create_md"):
                safe_name = data["name"].replace("/", "_").replace("\\", "_")
                md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban\\mykanban"
                filename = os.path.join(md_dir, f"{safe_name}.md")

                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(f"# {data['name']}\n\n")
                        f.write(f"## Due\n{data['due']}\n\n")
                        f.write("## Memo\n")
                        f.write(f"{data['memo']}\n\n")
                        f.write("## Notes\n\n")

                    print(f"[MD CREATED] {filename}")

                except Exception as e:
                    wx.MessageBox(
                        f"Markdown file creation failed:\n{e}",
                        "File Error",
                        wx.ICON_ERROR
                    )

            self.refresh()

            wx.CallAfter(self.refresh)

        dlg.Destroy()

    # ---------------------
    # Refresh
    # ---------------------

    def refresh(self):
        # Clear safely
        for col in self.columns.values():
            for child in col["task_container"].GetChildren():
                child.Destroy()
            col["task_sizer"].Clear()

        # Draw
        for task in self.controller.get_tasks():
            col = self.columns.get(task.status)
            if not col:
                continue

            card = TaskCard(col["task_container"], task, self.controller, self.refresh)
            col["task_sizer"].Add(card, 0, wx.EXPAND | wx.ALL, 5)

        # Layout
        for col in self.columns.values():
            col["task_container"].Layout()
            col["panel"].Layout()

        self.Layout()