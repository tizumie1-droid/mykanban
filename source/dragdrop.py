# dragdrop.py
import wx

# =========================
# Drag Source
# =========================

def bind_drag(widget, task):
    """
    Bind drag event to TaskCard
    """

    def on_left_down(event):
        data = wx.TextDataObject(task.id)
        src = wx.DropSource(widget)
        src.SetData(data)

        # Start drag
        src.DoDragDrop(flags=wx.Drag_DefaultMove)
        event.Skip()

    widget.Bind(wx.EVT_LEFT_DOWN, on_left_down)


# =========================
# Drop Target
# =========================

class TaskDropTarget(wx.TextDropTarget):
    def __init__(self, status, controller, refresh_cb):
        super().__init__()
        self.status = status
        self.controller = controller
        self.refresh_cb = refresh_cb

    def OnDropText(self, x, y, text):
        # text = task.id
        task = self.controller.get_task_by_id(text)
        if task:
            task.status = self.status
            self.controller.save()
            # self.refresh_cb()
            # ✅ イベントループ後に安全実行
        wx.CallAfter(self.refresh_cb)
        return True


# =========================
# Bind Drop
# =========================

def bind_drop(widget, status, controller, refresh_cb):
    target = TaskDropTarget(status, controller, refresh_cb)
    widget.SetDropTarget(target)
