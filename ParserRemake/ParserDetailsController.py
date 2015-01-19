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

      self.setDefaultImage()

   def setDefaultImage(self):
      self.canvas.Canvas.ZoomToBB(None, True)

      shift = (self.timelineInfo.keys()[-1] * self.canvas.Canvas.xScale)/2, 10
      if shift[0] > 200: shift = 0,10
      self.canvas.Canvas.MoveImageY(shift, "Pixel")
      self.canvas.Canvas.Zoom(2.25,)
      self.canvas.Canvas.Draw()

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
      startTime = 0
      endTime = self.timelineInfo.keys()[-1] * self.canvas.Canvas.xScale
      # bottom = self.canvas.Canvas.WorldToPixel((self.canvas.Canvas.ViewPortBB[1][1],0))[0]
      # bottom = int(bottom)
      bottom = -300

      timeLine = FloatCanvas.Line([(startTime, bottom),(endTime, bottom)])
      self.canvas.Canvas.AddObject(timeLine)
      self.canvas.timeLine = timeLine
      for time, logEventList in self.timelineInfo.iteritems():
         scaledTime = time * self.canvas.Canvas.xScale
         for logEvent in logEventList:
            if 'teamcenter' in logEvent.lower() and not self.tcTime: continue
            if 'user' in logEvent.lower() and not self.userTime: continue
            if 'download' in logEvent.lower() and not self.dlTime: continue
            textAbove = CustomFloatCanvas.RotatedText(logEvent, (scaledTime, bottom), 90)
            timeBelow = CustomFloatCanvas.RotatedText(str(time), (scaledTime, bottom), 0)
            self.canvas.Canvas.AddObject(textAbove)
            self.canvas.Canvas.AddObject(timeBelow)
            self.canvas.Canvas.AddLine([(scaledTime, bottom),(scaledTime, 30)])
      self.canvas.Canvas.Draw(True)