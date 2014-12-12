from ParserDetailsView import MyFrame1
from wx.lib.floatcanvas import GUIMode, FloatCanvas
from collections import OrderedDict


class ParserDetailsController:
   def __init__(self, parent, details={}, count={}, timeLineInfo={}):
      self.mainWindow = MyFrame1(parent)
      self.details = details
      self.count = count
      self.timelineInfo = OrderedDict((k, timeLineInfo[k]) for k in sorted(timeLineInfo.keys()))
      self.canvas = self.mainWindow.canvas

      # init display
      self.popData()
      # self.canvas.SetMode(GUIMode.GUIMove())
      self.buildTimeline()

   def show(self):
      self.mainWindow.Show()

   def popData(self):
      self.mainWindow.lblDLTime.SetLabel('%s %s' % (self.mainWindow.lblDLTime.GetLabel(), str(self.details['download'])))
      self.mainWindow.lblIPEMTime.SetLabel('%s %s' % (self.mainWindow.lblIPEMTime.GetLabel(), str(self.details['integration'])))
      self.mainWindow.lblTCTime.SetLabel('%s %s' % (self.mainWindow.lblTCTime.GetLabel(), str(self.details['teamcenter'])))
      self.mainWindow.lblTotal.SetLabel('%s %s' % (self.mainWindow.lblTotal.GetLabel(), str(self.count['total'])))
      self.mainWindow.lblTotalMan.SetLabel('%s %s' % (self.mainWindow.lblTotalMan.GetLabel(), str(self.count['manage'])))
      self.mainWindow.lblTotalOp.SetLabel('%s %s' % (self.mainWindow.lblTotalOp.GetLabel(), str(self.details['totalOp'])))
      self.mainWindow.lblTotalOpNoUser.SetLabel('%s %s' % (self.mainWindow.lblTotalOpNoUser.GetLabel(), str(self.details['totalOpNoUser'])))
      self.mainWindow.lblTotalSave.SetLabel('%s %s' % (self.mainWindow.lblTotalSave.GetLabel(), str(self.count['save'])))
      self.mainWindow.lblUserTime.SetLabel('%s %s' % (self.mainWindow.lblUserTime.GetLabel(), str(self.details['user'])))
      self.mainWindow.lblTotalOpen.SetLabel('%s %s' % (self.mainWindow.lblTotalOpen.GetLabel(), str(self.count['open'])))

   def buildTimeline(self):
      startTime = self.timelineInfo.keys()[0]
      endTime = self.timelineInfo.keys()[-1]
      self.canvas.Canvas.AddLine([(startTime, 0),(endTime, 0)])

      for time, logEvent in self.timelineInfo.iteritems():
         self.canvas.Canvas.AddLine([(time, 0),(time, 25)])

      self.canvas.Canvas.Draw(True)
      self.canvas.ZoomToFit(None)