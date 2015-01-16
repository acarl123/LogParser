from ParserDetailsView import MyFrame1
from wx.lib.floatcanvas import GUIMode, FloatCanvas
from collections import OrderedDict
import wx
import CustomFloatCanvas

class ParserDetailsController:
   def __init__(self, parent, details={}, count={}, timeLineInfo={}):
      self.mainWindow = MyFrame1(parent, self)
      self.details = details
      self.count = count
      self.timelineInfo = OrderedDict((k, timeLineInfo[k]) for k in sorted(timeLineInfo.keys()))
      self.canvas = self.mainWindow.canvas
      self.tcTime = False
      self.userTime = False
      self.dlTime = False

      # init display
      self.popData()
      self.mainWindow.SetLabel(details[1])
      self.buildTimeline()

      #Bind events
      self.mainWindow.lblTCTime.Bind(wx.EVT_CHECKBOX, self.onTCTimeCheck)
      self.mainWindow.lblUserTime.Bind(wx.EVT_CHECKBOX, self.onUserTimeCheck)
      self.mainWindow.lblDLTime.Bind(wx.EVT_CHECKBOX, self.onDLTimeCheck)

      self.canvas.Canvas.ZoomToBB(None, True)

   def show(self):
      self.mainWindow.Show()

   def popData(self):
      self.mainWindow.lblDLTime.SetLabel('%s %s' % (self.mainWindow.lblDLTime.GetLabel(), str(self.details[0]['download'])))
      self.mainWindow.lblIPEMTime.SetLabel('%s %s' % (self.mainWindow.lblIPEMTime.GetLabel(), str(self.details[0]['integration'])))
      self.mainWindow.lblTCTime.SetLabel('%s %s' % (self.mainWindow.lblTCTime.GetLabel(), str(self.details[0]['teamcenter'])))
      self.mainWindow.lblTotal.SetLabel('%s %s' % (self.mainWindow.lblTotal.GetLabel(), str(self.count['total'])))
      self.mainWindow.lblTotalMan.SetLabel('%s %s' % (self.mainWindow.lblTotalMan.GetLabel(), str(self.count['manage'])))
      self.mainWindow.lblTotalOp.SetLabel('%s %s' % (self.mainWindow.lblTotalOp.GetLabel(), str(self.details[0]['totalOp'])))
      self.mainWindow.lblTotalOpNoUser.SetLabel('%s %s' % (self.mainWindow.lblTotalOpNoUser.GetLabel(), str(self.details[0]['totalOpNoUser'])))
      self.mainWindow.lblTotalSave.SetLabel('%s %s' % (self.mainWindow.lblTotalSave.GetLabel(), str(self.count['save'])))
      self.mainWindow.lblUserTime.SetLabel('%s %s' % (self.mainWindow.lblUserTime.GetLabel(), str(self.details[0]['user'])))
      self.mainWindow.lblTotalOpen.SetLabel('%s %s' % (self.mainWindow.lblTotalOpen.GetLabel(), str(self.count['open'])))

   def onTCTimeCheck(self, event):
      self.tcTime = not self.tcTime
      self.buildTimeline()

   def onUserTimeCheck(self, event):
      self.userTime = not self.userTime
      self.buildTimeline()

   def onDLTimeCheck(self, event):
      self.dlTime = not self.dlTime
      self.buildTimeline()

   def buildTimeline(self):
      self.canvas.Canvas.ClearAll(False)
      startTime = 0 # * self.canvas.Canvas.Scale# self.timelineInfo.keys()[0]
      endTime = self.timelineInfo.keys()[-1] * self.canvas.Canvas.Scale
      timeLine = FloatCanvas.Line([(startTime, 0),(endTime, 0)])
      self.canvas.Canvas.AddObject(timeLine)
      self.canvas.timeLine = timeLine
      dc = wx.ClientDC(self.canvas.Canvas)
      dc.SetPen(wx.Pen('WHITE', 3, wx.SOLID))
      dc.SetBrush(wx.BLACK_BRUSH)
      dc.SetLogicalFunction(wx.XOR)
      for time, logEventList in self.timelineInfo.iteritems():
         scaledTime = time * self.canvas.Canvas.Scale
         for logEvent in logEventList:
            if 'teamcenter' in logEvent.lower() and not self.tcTime: continue
            if 'user' in logEvent.lower() and not self.userTime: continue
            if 'download' in logEvent.lower() and not self.dlTime: continue
            textAbove = CustomFloatCanvas.RotatedText(logEvent, (scaledTime, 0), 90)
            timeBelow = CustomFloatCanvas.RotatedText(str(time), (scaledTime, 0), 0)
            self.canvas.Canvas.AddObject(textAbove)
            self.canvas.Canvas.AddObject(timeBelow)
            self.canvas.Canvas.AddLine([(scaledTime, 0),(scaledTime, 30)])
      self.canvas.Canvas.Draw(True)
