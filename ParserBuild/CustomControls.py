import wx

class FileDropTarget( wx.FileDropTarget ):
   def __init__(self, window):
      wx.FileDropTarget.__init__(self)
      self.window = window