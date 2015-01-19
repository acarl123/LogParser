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
      self.timeList = []
      # init display
      self.popData()
      self.mainWindow.SetLabel(details['fileName'])
      self.buildTimeline()

      #Bind events
      self.mainWindow.lblTCTime.Bind(wx.EVT_CHECKBOX, self.onTCTimeCheck)
      self.mainWindow.lblUserTime.Bind(wx.EVT_CHECKBOX, self.onUserTimeCheck)
      self.mainWindow.lblDLTime.Bind(wx.EVT_CHECKBOX, self.onDLTimeCheck)

      self.setDefaultImage()

   def setDefaultImage(self):
      self.canvas.Canvas.ZoomToBB(None, True)

      shift = (self.timelineInfo.keys()[-1] * self.canvas.Canvas.xScale)/2, 10
      if shift[0] > 200: shift = 0,20
      self.canvas.Canvas.MoveImageY(shift, "Pixel")
      self.canvas.Canvas.Zoom(2.25,)
      self.canvas.Canvas.Draw()

   def show(self):
      self.mainWindow.Show()

   def popData(self):
      self.mainWindow.lblDLTime.SetLabel('%s %s' % (self.mainWindow.lblDLTime.GetLabel(), str(self.details['times']['download'])))
      self.mainWindow.lblIPEMTime.SetLabel('%s %s' % (self.mainWindow.lblIPEMTime.GetLabel(), str(self.details['times']['integration'])))
      self.mainWindow.lblTCTime.SetLabel('%s %s' % (self.mainWindow.lblTCTime.GetLabel(), str(self.details['times']['teamcenter'])))
      self.mainWindow.lblTotal.SetLabel('%s %s' % (self.mainWindow.lblTotal.GetLabel(), str(self.count['total'])))
      self.mainWindow.lblTotalMan.SetLabel('%s %s' % (self.mainWindow.lblTotalMan.GetLabel(), str(self.count['manage'])))
      self.mainWindow.lblTotalOp.SetLabel('%s %s' % (self.mainWindow.lblTotalOp.GetLabel(), str(self.details['times']['totalOp'])))
      self.mainWindow.lblTotalOpNoUser.SetLabel('%s %s' % (self.mainWindow.lblTotalOpNoUser.GetLabel(), str(self.details['times']['totalOpNoUser'])))
      self.mainWindow.lblTotalSave.SetLabel('%s %s' % (self.mainWindow.lblTotalSave.GetLabel(), str(self.count['save'])))
      self.mainWindow.lblUserTime.SetLabel('%s %s' % (self.mainWindow.lblUserTime.GetLabel(), str(self.details['times']['user'])))
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
      self.timeList = []
      startTime = 0
      endTime = self.timelineInfo.keys()[-1] * self.canvas.Canvas.xScale
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
            check = self.checkTimes(scaledTime)
            self.timeList.append(scaledTime)

            textAbove = CustomFloatCanvas.RotatedText(logEvent, (scaledTime-25, bottom), 90)
            timeBelow = CustomFloatCanvas.RotatedText(str(time), (scaledTime, bottom), 0)
            if check == 1:
               textAbove = CustomFloatCanvas.RotatedText(logEvent, (scaledTime, bottom), 90)
            # if check == 2:
            #    timeBelow = CustomFloatCanvas.RotatedText(str(time), (scaledTime, bottom-20), 0)
            self.canvas.Canvas.AddObject(textAbove)
            self.canvas.Canvas.AddObject(timeBelow)
            self.canvas.Canvas.AddLine([(scaledTime, bottom),(scaledTime, 30)])
      self.canvas.Canvas.Draw(True)

   def checkTimes(self, scaledTime):
      for time in self.timeList:
         timeAbove = time+5
         timeBelow = time-5
         if scaledTime > timeBelow and scaledTime < timeAbove:
            return 1
      return 0