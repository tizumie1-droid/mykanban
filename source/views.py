import wx
import uuid
import os
import re
import shutil

from models import Task
from calendar_view import CalendarDialog
from dragdrop import bind_drag, bind_drop
from gantt import GanttView

# ==============================
# Task Card
# ==============================

class TaskCard(wx.Panel):
    def __init__(self, parent, task, controller, refresh_cb):
        super().__init__(parent, style=wx.BORDER_SIMPLE)
        self.task = task
        self.controller = controller
        self.refresh_cb = refresh_cb

        # self.SetBackgroundColour(self.get_color_by_status(task.status))

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label=task.name)
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        start = wx.StaticText(self, label=f"Start: {task.start_date if task.start_date else '-'}")
        due = wx.StaticText(self, label=f"Due: {task.due if task.due else '-'}") 
        memo = wx.StaticText(self, label=task.memo)

        vbox.Add(title, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(start, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        vbox.Add(due, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        vbox.Add(memo, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.SetSizer(vbox)

        # Drag & Drop
        bind_drag(self, task)
        # Right click
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_conext_menu)

    def on_resize(self, event):
        width = self.GetSize().width
        self.title.Wrap(width)
        self.Layout()
        event.Skip()

    def on_edit(self, event):
        # すでにMDファイルが存在する場合は、タスクカード上での編集を禁止
        filename = self._get_md_filepath()
        if os.path.exists(filename):
            dlg = wx.MessageDialog(self, "This task has an associated markdown file. Do you want to edit the markdown file instead?", "Editing Disabled", wx.YES_NO | wx.ICON_INFORMATION)
            dlg.SetYesNoLabels("Edit Markdown", "Cancel")
            res = dlg.ShowModal()
            dlg.Destroy()
            if res == wx.ID_YES:
                try:
                    os.startfile(filename)
                except Exception as e:
                    wx.MessageBox(f"Failed to open markdown file: {e}", "Error", wx.ICON_ERROR)
            return
        
        dlg = EditTaskDialog(self, self.task)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_data()
            self.task.name = data['name']
            self.task.start_date = data['start_date']
            self.task.due = data['due']
            self.task.memo = data['memo']
            self.controller.update_task(self.task)

            # == Markdown file creation ==
            if data.get("create_md"):
                safe_name = data["name"].replace('/', '_').replace('\\', '_')
                md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md\\todo"
                filename = os.path.join(md_dir, f"{safe_name}.md")

                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"# {data['name']}\n")
                        f.write(f"## Start\n{data['start_date']}\n")
                        f.write(f"## Due\n{data['due']}\n")
                        f.write(f"## Memo\n{data['memo']}\n\n")
                    
                    os.startfile(filename)

                except Exception as e:
                    wx.MessageBox(f"Failed to create markdown file: \n{filename}\n{e}", "File Error", wx.OK | wx.ICON_ERROR)

            wx.CallAfter(self.refresh_cb)
        dlg.Destroy()

    def on_conext_menu(self, event):
        menu = wx.Menu()
        
        open_md_item = menu.Append(wx.ID_ANY, "Open Markdown")
        edit_task_item = menu.Append(wx.ID_ANY, "Edit Task")
        delete_task_item = menu.Append(wx.ID_ANY, "Delete Task")

        self.Bind(wx.EVT_MENU, self.on_open_md_file, open_md_item)
        self.Bind(wx.EVT_MENU, self.on_edit, edit_task_item)
        self.Bind(wx.EVT_MENU, self.on_delete_task, delete_task_item)

        self.PopupMenu(menu)
        menu.Destroy()

    def _get_md_filepath(self):
        safe_name = self.task.name.replace('/', '_').replace('\\', '_')
        md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md\\todo"
        filename = os.path.join(md_dir, f"{safe_name}.md")
        return filename
    
    def on_open_md_file(self, event):
        filename = self._get_md_filepath()
        if os.path.exists(filename):
            try:
                os.startfile(filename)
            except Exception as e:
                wx.MessageBox(f"Failed to open markdown file: {e}", "Error", wx.ICON_ERROR)
        else:
            wx.MessageBox("No associated markdown file found.", "File Not Found", wx.ICON_INFORMATION)
    
    def on_delete_task(self, event):
        dlg = wx.MessageDialog(self, "Are you sure you want to delete this task?", "Confirm Delete", wx.YES_NO | wx.ICON_WARNING)
        if dlg.ShowModal() == wx.ID_YES:
            self.controller.delete_task(self.task)
            # Delete associated markdown file if exists
            filename = self._get_md_filepath()
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"Deleted markdown file: {filename}")
                except Exception as e:
                    wx.MessageBox(f"Failed to delete markdown file: \n{filename}\n{e}", "File Error", wx.OK | wx.ICON_ERROR)
            wx.CallAfter(self.refresh_cb)


# ==============================
# Add Task Dialog
# ==============================

class AddTaskDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Add Task", size=(420, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Name
        vbox.Add(wx.StaticText(self, label="Task Name:"), 0, wx.ALL, 5)
        self.name_ctrl = wx.TextCtrl(self)
        vbox.Add(self.name_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        # Start Date
        hbox_start = wx.BoxSizer(wx.HORIZONTAL)
        self.start_ctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        btn_start_cal = wx.Button(self, label="📅")
        hbox_start.Add(self.start_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_start.Add(btn_start_cal, 0)
        vbox.Add(wx.StaticText(self, label="Start Date:"), 0, wx.ALL, 5)
        vbox.Add(hbox_start, 0, wx.EXPAND | wx.ALL, 5)
        # Due Date
        hbox_due = wx.BoxSizer(wx.HORIZONTAL)
        self.due_ctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        btn_due_cal = wx.Button(self, label="📅")
        hbox_due.Add(self.due_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_due.Add(btn_due_cal, 0)
        vbox.Add(wx.StaticText(self, label="Due Date:"), 0, wx.ALL, 5)
        vbox.Add(hbox_due, 0, wx.EXPAND | wx.ALL, 5)
        # Complete Date
        hbox_complete = wx.BoxSizer(wx.HORIZONTAL)
        self.complete_ctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        btn_complete_cal = wx.Button(self, label="📅")
        hbox_complete.Add(self.complete_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_complete.Add(btn_complete_cal, 0)
        vbox.Add(wx.StaticText(self, label="Complete Date:"), 0, wx.ALL, 5)
        vbox.Add(hbox_complete, 0, wx.EXPAND | wx.ALL, 5)
        # Memo
        vbox.Add(wx.StaticText(self, label="Memo:"), 0, wx.ALL, 5)
        self.memo_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        vbox.Add(self.memo_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # Buttons
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.create_md_checkbox = wx.CheckBox(self, label="Create associated markdown file")
        vbox.Add(self.create_md_checkbox, 0, wx.ALL, 5)
        self.SetSizer(vbox)

        # Events
        btn_start_cal.Bind(wx.EVT_BUTTON, self.on_start_calendar)
        btn_due_cal.Bind(wx.EVT_BUTTON, self.on_due_calendar)
        btn_complete_cal.Bind(wx.EVT_BUTTON, self.on_complete_calendar)


    def on_start_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            date = dlg.get_date()
            self.start_ctrl.SetValue(date)
        dlg.Destroy()
    def on_due_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            date = dlg.get_date()
            self.due_ctrl.SetValue(date)
        dlg.Destroy()
    def on_complete_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            date = dlg.get_date()
            self.complete_ctrl.SetValue(date)
        dlg.Destroy()

    def get_data(self):
        return {
            "name": self.name_ctrl.GetValue(),
            "start_date": self.start_ctrl.GetValue(),
            "due": self.due_ctrl.GetValue(),
            "completed_date": self.complete_ctrl.GetValue(),
            "memo": self.memo_ctrl.GetValue(),
            "create_md": self.create_md_checkbox.GetValue()
        }


# ==============================
# Edit Task Dialog
# =============================

class EditTaskDialog(wx.Dialog):
    def __init__(self, parent, task: Task):
        super().__init__(parent, title="Edit Task", size=(420, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.task = task
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Name
        vbox.Add(wx.StaticText(self, label="Task Name:"), 0, wx.ALL, 5)
        self.name_ctrl = wx.TextCtrl(self, value=task.name)
        vbox.Add(self.name_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        # Start Date
        hbox_start = wx.BoxSizer(wx.HORIZONTAL)
        self.start_ctrl = wx.TextCtrl(self, value=task.start_date if task.start_date else '', style=wx.TE_READONLY)
        btn_start_cal = wx.Button(self, label="📅")
        hbox_start.Add(self.start_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_start.Add(btn_start_cal, 0)
        vbox.Add(wx.StaticText(self, label="Start Date:"), 0, wx.ALL, 5)
        vbox.Add(hbox_start, 0, wx.EXPAND | wx.ALL, 5)
        # Due Date
        hbox_due = wx.BoxSizer(wx.HORIZONTAL)
        self.due_ctrl = wx.TextCtrl(self, value=task.due if task.due else '', style=wx.TE_READONLY)
        btn_due_cal = wx.Button(self, label="📅")
        hbox_due.Add(self.due_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_due.Add(btn_due_cal, 0)
        vbox.Add(wx.StaticText(self, label="Due Date:"), 0, wx.ALL, 5)
        vbox.Add(hbox_due, 0, wx.EXPAND | wx.ALL, 5)
        # Complete Date
        hbox_complete = wx.BoxSizer(wx.HORIZONTAL)
        self.complete_ctrl = wx.TextCtrl(self, value=task.completed_date if task.completed_date else '', style=wx.TE_READONLY)
        btn_complete_cal = wx.Button(self, label="📅")
        hbox_complete.Add(self.complete_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox_complete.Add(btn_complete_cal, 0)
        vbox.Add(wx.StaticText(self, label="Complete Date:"), 0, wx.ALL, 5)
        vbox.Add(hbox_complete, 0, wx.EXPAND | wx.ALL, 5)
        # Memo
        vbox.Add(wx.StaticText(self, label="Memo:"), 0, wx.ALL, 5)
        self.memo_ctrl = wx.TextCtrl(self, value=task.memo if task.memo else '', style=wx.TE_MULTILINE)
        vbox.Add(self.memo_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # Buttons
        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.ALL, 5)
        self.create_md_checkbox = wx.CheckBox(self, label="Create associated markdown file")
        vbox.Add(self.create_md_checkbox, 0, wx.ALL, 5)

        self.SetSizer(vbox)

        # Events
        btn_start_cal.Bind(wx.EVT_BUTTON, self.on_start_calendar)
        btn_due_cal.Bind(wx.EVT_BUTTON, self.on_due_calendar)
        btn_complete_cal.Bind(wx.EVT_BUTTON, self.on_complete_calendar)
    

    def on_start_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            date = dlg.get_date()
            self.start_ctrl.SetValue(date)
        dlg.Destroy()

    def on_due_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            date = dlg.get_date()
            self.due_ctrl.SetValue(date)
        dlg.Destroy()

    def on_complete_calendar(self, event):
        dlg = CalendarDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            date = dlg.get_date()
            self.complete_ctrl.SetValue(date)
        dlg.Destroy()
    
    def get_data(self):
        return {
            "name": self.name_ctrl.GetValue(),
            "start_date": self.start_ctrl.GetValue(),
            "due": self.due_ctrl.GetValue(),
            "completed_date": self.complete_ctrl.GetValue(),
            "memo": self.memo_ctrl.GetValue(),
            "create_md": self.create_md_checkbox.GetValue()
        }

    
# ==============================
# kanban view
# ==============================

class KanbanView(wx.Frame):
    def __init__(self, controller):
        super().__init__(None, title="Kanban Board", size=(1300, 750))
        self.controller = controller
        self.columns = {}

        # 各カラムの現在のソート方式を保持する辞書
        self.sort_keys = {
            "todo": "name",
            "pending": "name",
            "doing": "name",
            "done": "name"
        }
        
        self.build_ui()
        self.refresh()

    # ==============================
    # UI構築
    # ==============================

    def build_ui(self):
        panel = wx.Panel(self)
        main_vbox = wx.BoxSizer(wx.VERTICAL)

        # Toolbar
        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label="Add Task")
        btn_gantt = wx.Button(panel, label="📊 Gantt")
        btn_completed_list = wx.Button(panel, label="✅ Completed Tasks")
        btn_refresh = wx.Button(panel, label="🔃 Refresh")
        toolbar.Add(btn_add, 0, wx.ALL, 5)
        toolbar.Add(btn_gantt, 0, wx.ALL, 5)
        toolbar.Add(btn_completed_list, 0, wx.ALL, 5)
        toolbar.Add(btn_refresh, 0, wx.ALL, 5)

        main_vbox.Add(toolbar, 0, wx.EXPAND | wx.ALL, 5)

        # Board
        self.board_panel = wx.Panel(panel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        todo = self.create_column(self.board_panel, "To Do", "todo")
        pending = self.create_column(self.board_panel, "Pending", "pending")
        doing = self.create_column(self.board_panel, "Doing", "doing")
        done = self.create_column(self.board_panel, "Done", "done")
        
        self.columns["todo"] = todo
        self.columns["pending"] = pending
        self.columns["doing"] = doing
        self.columns["done"] = done

        left_vbox = wx.BoxSizer(wx.VERTICAL)
        left_vbox.Add(todo["panel"], 3, wx.EXPAND | wx.ALL, 5)
        left_vbox.Add(pending["panel"], 1, wx.EXPAND | wx.ALL, 5)

        hbox.Add(left_vbox, 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(doing["panel"], 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(done["panel"], 1, wx.EXPAND | wx.ALL, 5)

        self.board_panel.SetSizer(hbox)
        main_vbox.Add(self.board_panel, 1, wx.EXPAND)
        panel.SetSizer(main_vbox)

        # Events
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_task)
        btn_gantt.Bind(wx.EVT_BUTTON, self.on_open_gantt)
        btn_completed_list.Bind(wx.EVT_BUTTON, self.on_open_completed_list)
        btn_refresh.Bind(wx.EVT_BUTTON, self.on_refresh_tasks)

    
    def make_sort_choice_handler(self, status):
        def handler(event):
            self.on_sort_choice(event, status)
        return handler

    def create_column(self, parent, title, status):
        panel = wx.Panel(parent, style=wx.BORDER_SIMPLE)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Header: Title + Sort Button
        hbox_title = wx.BoxSizer(wx.HORIZONTAL)
        title_lbl = wx.StaticText(panel, label=title)
        title_lbl.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        hbox_title.Add(title_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        # ソート選択候補
        choices = ["name", "due", "start_date", "completed_date"]
        sort_choice = wx.Choice(panel, choices=choices)
        sort_choice.SetStringSelection(self.sort_keys.get(status, "name"))
        hbox_title.Add(sort_choice, 0, wx.ALL, 5)
        sort_choice.Bind(wx.EVT_CHOICE, self.make_sort_choice_handler(status))

        # Done列のみArchiveボタンを追加
        if status == "done":
            btn_archive = wx.Button(panel, label="📁 Archive")
            hbox_title.Add(btn_archive, 0, wx.ALL, 5)
            btn_archive.Bind(wx.EVT_BUTTON, self.on_archive_completed_tasks)

        vbox.Add(hbox_title, 0, wx.EXPAND | wx.ALL, 5)

        # Task Container
        task_container = wx.ScrolledWindow(panel, style=wx.VSCROLL)
        task_container.SetScrollRate(0, 20)
        task_sizer = wx.BoxSizer(wx.VERTICAL)
        task_container.SetSizer(task_sizer)
        task_container.FitInside()

        vbox.Add(task_container, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(vbox)

        bind_drop(task_container, status, self.controller, self.refresh)

        return {
            "panel": panel, 
            "task_container": task_container, 
            "task_sizer": task_sizer,
            "status": status,
            "sort_choice": sort_choice
        }
    
    def on_sort_choice(self, event, status):
        choice_ctrl = event.GetEventObject()
        selected_sort = choice_ctrl.GetStringSelection()
        self.sort_keys[status] = selected_sort
        self.refresh()

    
    # ==============================
    # Event Handlers
    # ==============================
    def on_open_gantt(self, event):
        gantt = GanttView(self.controller)
        gantt.Show()
    
    def on_add_task(self, event):
        dlg = AddTaskDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_data()
            task = Task(
                id=str(uuid.uuid4()),
                name=data['name'],
                start_date=data['start_date'],
                due=data['due'],
                completed_date=data['completed_date'],
                memo=data['memo'],
                status="todo"
            )
            self.controller.add_task(task)

            # == Markdown file creation ==
            if data.get("create_md"):
                safe_name = data["name"].replace('/', '_').replace('\\', '_')
                md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md\\todo"
                filename = os.path.join(md_dir, f"{safe_name}.md")

                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"# {data['name']}\n")
                        f.write(f"## Start\n{data['start_date']}\n")
                        f.write(f"## Due\n{data['due']}\n")
                        f.write(f"## Completed Date\n{data['completed_date']}\n")
                        f.write(f"## Memo\n{data['memo']}\n\n")
                    print(f"Created markdown file: {filename}")
                    os.startfile(filename)
                except Exception as e:
                    wx.MessageBox(f"Failed to create markdown file: \n{filename}\n{e}", "File Error", wx.OK | wx.ICON_ERROR)
            
            wx.CallAfter(self.refresh)
        dlg.Destroy()
    
    def on_archive_completed_tasks(self, event):
        done_col = self.columns.get("done")
        if not done_col:
            wx.MessageBox("Completed column not found.", "Error", wx.ICON_ERROR)
            return
        
        tasks_to_archive = [task_panel.task for task_panel in done_col["task_container"].GetChildren() if isinstance(task_panel, TaskCard)]
        for task in tasks_to_archive:
            task.status = "completed"
            # Markdownファイルの移動
            safe_name = task.name.replace('/', '_').replace('\\', '_')
            md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md"
            src_dir = os.path.join(md_dir, "todo")
            filename = os.path.join(src_dir, f"{safe_name}.md")
            archive_dir = os.path.join(md_dir, "archive")
            try:
                shutil.move(filename, os.path.join(archive_dir, f"{safe_name}.md"))
                print(f"Archived markdown file: {filename}")
            except Exception as e:
                wx.MessageBox(f"Failed to archive markdown file: \n{filename}\n{e}", "File Error", wx.OK | wx.ICON_ERROR)
            
            self.controller.update_task(task)
        self.controller.save()
        wx.CallAfter(self.refresh)
        wx.MessageBox(f"Archived {len(tasks_to_archive)} tasks.", "Archive Completed", wx.OK | wx.ICON_INFORMATION)

    def on_open_completed_list(self, event):
        dlg = CompleteListView(self.controller)
        dlg.Show()

    def on_refresh_tasks(self, event):
        self.controller.refresh_from_md()
        self.refresh()


    def refresh(self):
        for col in self.columns.values():
            for child in col["task_container"].GetChildren():
                child.Destroy()
            col["task_sizer"].Clear()
        
        # Get tasks grouped by status
        tasks_by_status = {status: [] for status in self.columns.keys()}
        for task in self.controller.get_tasks():
            if task.status in tasks_by_status:
                tasks_by_status[task.status].append(task)
        
        # ソート関数
        def task_sort_key(task, key):
            val = getattr(task, key, "")
            if val is None:
                return ""
            return val.lower() if isinstance(val, str) else val
        
        # Draw tasks sorted
        for status, tasks in tasks_by_status.items():
            sort_key = self.sort_keys.get(status, "name")
            tasks = sorted(tasks, key=lambda t: task_sort_key(t, sort_key))

            col = self.columns.get(status)
            if not col:
                continue
            for task in tasks:
                card = TaskCard(col["task_container"], task, self.controller, self.refresh)
                col["task_sizer"].Add(card, 1, wx.EXPAND | wx.ALL, 5)
        
        for col in self.columns.values():
            col["task_container"].Layout()
            col["panel"].Layout()
        
        self.Layout()


# ==============================
# Completed List View
# ==============================

class  CompleteListView(wx.Frame):
    def __init__(self, controller):
        super().__init__(None, title="Completed Tasks", size=(900, 600))
        self.controller = controller

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Listctrlをレポートモードで作成
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "Task Name", width=200)
        self.list_ctrl.InsertColumn(1, "Status", width=100)
        self.list_ctrl.InsertColumn(2, "Start Date", width=150)
        self.list_ctrl.InsertColumn(3, "Due Date", width=150)
        self.list_ctrl.InsertColumn(4, "Completed Date", width=150)
        self.list_ctrl.InsertColumn(5, "Memo", width=250)

        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)

        self.populate_list()

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_right_click)

    def populate_list(self):
        # 完了リストのタスクだけ取得
        self.tasks = [t for t in self.controller.get_tasks() if t.status == "completed"]
        self.list_ctrl.DeleteAllItems()

        for task in self.tasks:
            idx = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), task.name)
            self.list_ctrl.SetItem(idx, 1, task.status)
            self.list_ctrl.SetItem(idx, 2, task.start_date if task.start_date else '-')
            self.list_ctrl.SetItem(idx, 3, task.due if task.due else '-')
            self.list_ctrl.SetItem(idx, 4, task.completed_date if task.completed_date else '-')
            self.list_ctrl.SetItem(idx, 5, task.memo if task.memo else '-')
    
    def on_right_click(self, event):
        idx = event.GetIndex()
        if idx == wx.NOT_FOUND:
            return
        
        menu = wx.Menu()
        open_md_item = menu.Append(wx.ID_ANY, "Open Markdown")
        delete_task_item = menu.Append(wx.ID_ANY, "Delete Task")
        self.Bind(wx.EVT_MENU, lambda e: self.on_open_md_file(idx), open_md_item)
        self.Bind(wx.EVT_MENU, lambda e: self.on_delete_task(idx), delete_task_item)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_open_md_file(self, idx):
        task = self.tasks[idx]
        md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md\\archive"
        safe_name = task.name.replace('/', '_').replace('\\', '_')
        filename = os.path.join(md_dir, f"{safe_name}.md")
        if os.path.exists(filename):
            try:
                os.startfile(filename)
            except Exception as e:
                wx.MessageBox(f"Failed to open markdown file: {e}", "Error", wx.ICON_ERROR)
        else:
            wx.MessageBox("No associated markdown file found.", "File Not Found", wx.ICON_INFORMATION)

    def on_delete_task(self, idx):
        task = self.tasks[idx]
        dlg = wx.MessageDialog(self, "Are you sure you want to delete this task?", "Confirm Delete", wx.YES_NO | wx.ICON_WARNING)
        if dlg.ShowModal() == wx.ID_YES:
            self.controller.delete_task(task)
            # Delete associated markdown file if exists
            md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md\\archive"
            safe_name = task.name.replace('/', '_').replace('\\', '_')
            filename = os.path.join(md_dir, f"{safe_name}.md")

            if os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"Deleted markdown file: {filename}")
                except Exception as e:
                    wx.MessageBox(f"Failed to delete markdown file: \n{filename}\n{e}", "File Error", wx.OK | wx.ICON_ERROR)
            self.populate_list()
        dlg.Destroy()