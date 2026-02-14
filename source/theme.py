import wx

# =========================
# Lazy Theme Factory
# =========================

def get_font_title():
    return wx.Font(
        14,
        wx.FONTFAMILY_DEFAULT,
        wx.FONTSTYLE_NORMAL,
        wx.FONTWEIGHT_BOLD
    )

def get_font_normal():
    return wx.Font(
        10,
        wx.FONTFAMILY_DEFAULT,
        wx.FONTSTYLE_NORMAL,
        wx.FONTWEIGHT_NORMAL
    )

def get_bg_color():
    return wx.Colour(245, 247, 250)

def get_card_color():
    return wx.Colour(255, 255, 255)

def get_border_color():
    return wx.Colour(220, 220, 220)

# =========================
# Theme Apply
# =========================

def apply_theme(frame):
    frame.SetBackgroundColour(get_bg_color())