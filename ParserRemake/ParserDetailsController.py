from ParserDetailsView import MyFrame1


class ParserDetailsController:
   def __init__(self, parent, details={}):
      self.mainWindow = MyFrame1(parent)

   def show(self):
      self.mainWindow.Show()