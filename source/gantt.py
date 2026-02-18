import wx
import datetime
from models import Task


class GanttView(wx.Frame):
    def __init__(self, controller):
        super().__init__(None, title="Gantt Chart", size=(900, 500))
        self.controller = controller

        panel = wx.Panel(self)
        self.panel = panel

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Tool bar
        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        
        self.view_choice = wx.Choice(panel, choices=["Monthly", "Weekly"])
        self.view_choice.SetSelection(0)
        toolbar.Add(wx.StaticText(panel, label="View: "), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        toolbar.Add(self.view_choice, 0, wx.RIGHT, 10)

        self.refresh_btn = wx.Button(panel, label="Refresh")
        toolbar.Add(self.refresh_btn, 0, wx.RIGHT, 10)

        vbox.Add(toolbar, 0, wx.EXPAND | wx.ALL, 10)

        # Canvas
        self.canvas = GanttCanvas(panel, controller)
        vbox.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox)

        self.refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        self.view_choice.Bind(wx.EVT_CHOICE, self.on_refresh)

        self.Center()
        self.Show()

    def on_refresh(self, event):
        mode = self.view_choice.GetStringSelection()
        self.canvas.set_mode(mode)
        self.canvas.Refresh()


class GanttCanvas(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.mode = "Monthly"

        self.Bind(wx.EVT_PAINT, self.on_paint)

    def set_mode(self, mode):
        self.mode = mode
    
    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()

        tasks = self.controller.get_tasks()
        today = datetime.date.today()

        # time axis
        if self.mode == "Monthly":
            start = today.replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        else:  # Weekly
            start = today - datetime.timedelta(days=today.weekday())
            end = start + datetime.timedelta(days=7)
        
        days = (end - start).days

        w, h = self.GetSize()
        margin_left = 120
        margin_top = 40
        row_h = 30
        chart_w = w - margin_left - 20

        # Draw Axis
        for i in range(days + 1):
            x = margin_left + int(chart_w * i / days)
            dc.DrawLine(x, margin_top - 10, x, h - 20)

            date_label = (start + datetime.timedelta(days=i)).strftime("%d")
            dc.DrawText(date_label, x - 5, 5)
        
        # Draw Tasks
        y = margin_top
        for t in tasks:
            if not t.due:
                continue
            try:
                due = datetime.datetime.strptime(t.due, "%Y-%m-%d").date()
            except:
                continue
            if t.start_date:
                try:
                    start_d = datetime.datetime.strptime(t.start_date, "%Y-%m-%d").date()
                except:
                    start_d = due
            else:
                start_d = due
            
            # Clip
            s = max(start_d, start)
            e = min(due, end)

            if s > e:
                continue

            xs = margin_left + int(chart_w * (s - start).days / days)
            xe = margin_left + int(chart_w * (e - start).days / days)

            dc.DrawText(t.name, 10, y + 5)
            dc.SetBrush(wx.Brush(wx.Colour(100, 180, 240)))
            dc.SetPen(wx.Pen(wx.Colour(50, 120, 200)))

            if xs == xe:
                dc.DrowCircle(xs, y + 12, 5)
            else:
                dc.DrawRectangle(xs, y, max(5, xe-xs), 15)
            
            y += row_h
