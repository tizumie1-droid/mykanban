import wx
import wx.adv


class CalendarDialog(wx.Dialog):
    """
    CalendarDialog の Docstring
    """

    def __init__(self, parent, initial_date=None):
        super().__init__(parent, title="Select Due Date", size=(300, 300))

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.calendar = wx.adv.CalendarCtrl(self, style=wx.adv.CAL_SHOW_HOLIDAYS | wx.adv.CAL_MONDAY_FIRST)
        if initial_date:
            y, m, d = map(int, initial_date.split('-'))
            self.calendar.SetDate(wx.DateTime(d, m - 1, y))

        vbox.Add(self.calendar, 1, wx.EXPAND | wx.ALL, 10)

        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        self.SetSizer(vbox)
    
    def get_date(self):
        dt = self.calendar.GetDate()
        return f"{dt.GetYear()}-{dt.GetMonth() + 1:02d}-{dt.GetDay():02d}"
    