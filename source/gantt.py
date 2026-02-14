# gantt.py
import wx
from datetime import datetime, timedelta


class GanttView(wx.Frame):
    def __init__(self, controller):
        super().__init__(None, title="Gantt Chart", size=(1000, 600))
        self.controller = controller

        self.mode = "month"  # month / week
        self.build_ui()
        self.draw()

    # ---------------------
    # UI
    # ---------------------

    def build_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Toolbar
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_month = wx.Button(panel, label="Month View")
        self.btn_week = wx.Button(panel, label="Week View")
        hbox.Add(self.btn_month, 0, wx.ALL, 5)
        hbox.Add(self.btn_week, 0, wx.ALL, 5)

        vbox.Add(hbox, 0, wx.EXPAND)

        # Canvas
        self.canvas = wx.Panel(panel)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        vbox.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(vbox)

        # Events
        self.btn_month.Bind(wx.EVT_BUTTON, self.on_month)
        self.btn_week.Bind(wx.EVT_BUTTON, self.on_week)

    # ---------------------
    # Events
    # ---------------------

    def on_month(self, event):
        self.mode = "month"
        self.canvas.Refresh()

    def on_week(self, event):
        self.mode = "week"
        self.canvas.Refresh()

    # ---------------------
    # Draw
    # ---------------------

    def draw(self):
        self.canvas.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self.canvas)
        dc.Clear()

        tasks = self.controller.get_tasks()

        if not tasks:
            return

        today = datetime.today()

        if self.mode == "month":
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1)
            days = (end - start).days
        else:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=7)
            days = 7

        width, height = self.canvas.GetSize()
        col_w = width / days
        row_h = 30

        # Grid
        for i in range(days):
            x = int(i * col_w)
            dc.DrawLine(x, 0, x, height)

        y = 0
        for t in tasks:
            if not t.due:
                continue

            try:
                due = datetime.strptime(t.due, "%Y-%m-%d")
            except:
                continue

            if not (start <= due < end):
                continue

            day_index = (due - start).days
            x = int(day_index * col_w)

            dc.DrawRectangle(x, y, int(col_w), row_h)
            dc.DrawText(t.name, x + 2, y + 8)

            y += row_h + 5
