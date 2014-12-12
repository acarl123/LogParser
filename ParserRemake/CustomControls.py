import wx
from wx.lib.floatcanvas.FloatCanvas import *

class FileDropTarget( wx.FileDropTarget ):
   def __init__(self, window):
      wx.FileDropTarget.__init__(self)
      self.window = window

   def OnDropFiles(self, x, y, filenames):   #FileDropTarget now fills in the ListOfFiles
        for DragAndDropFile in filenames:
            self.window.dropUpdate(DragAndDropFile) # update list control


class FileListCtrl( wx.ListCtrl ):
   def __init__(self, *args, **kwargs):
      wx.ListCtrl.__init__(self, *args, **kwargs)
      self.index = 0

   def dropUpdate(self, path):
      self.InsertStringItem(self.index, path)
      self.index += 1

   def DeleteItem(*args, **kwargs):
      super(wx.ListCtrl).DeleteItem(*args, **kwargs)


class nonScaledLine( Line ):
   def __init__(self, Points):
      Line.__init__(self, Points)