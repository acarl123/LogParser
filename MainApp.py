import wx
from WxIpemParserViewLogController import WxIpemParserViewLogController

class MainApp(wx.App):
   def OnInit(self):
      self.controller = WxIpemParserViewLogController(None)
      self.controller.show()
      return True

def main():
   app = MainApp(False)
   app.MainLoop()

if __name__ == '__main__':
   main()
