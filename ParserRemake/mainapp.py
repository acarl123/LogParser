import wx
from ParserController import MainController

def main():
   app = wx.App(False)
   frame = MainController()
   frame.show()
   app.MainLoop()

if __name__ == '__main__': main()
