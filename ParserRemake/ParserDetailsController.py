from ParserDetailsView import MyFrame1
from wx.lib.floatcanvas import GUIMode, FloatCanvas
from collections import OrderedDict
import wx
import CustomText

class ParserDetailsController:
   def __init__(self, parent, details={}, count={}, timeLineInfo={}):
      self.mainWindow = MyFrame1(parent)
      self.details = details
      self.count = count
      self.timelineInfo = OrderedDict((k, timeLineInfo[k]) for k in sorted(timeLineInfo.keys()))
      self.canvas = self.mainWindow.canvas
      self.tcTime = True
      self.userTime = True
      self.dlTime = True

      # init display
      self.popData()
      # self.canvas.SetMode(GUIMode.GUIMove())
      self.buildTimeline()

      #Bind events
      self.mainWindow.lblTCTime.Bind(wx.EVT_CHECKBOX, self.onTCTimeCheck)
      self.mainWindow.lblUserTime.Bind(wx.EVT_CHECKBOX, self.onUserTimeCheck)
      self.mainWindow.lblDLTime.Bind(wx.EVT_CHECKBOX, self.onDLTimeCheck)

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
      startTime = 0# self.timelineInfo.keys()[0]
      endTime = self.timelineInfo.keys()[-1]
      self.canvas.Canvas.AddLine([(startTime, 0),(endTime, 0)])

      dc = wx.ClientDC(self.canvas.Canvas)
      dc.SetPen(wx.Pen('WHITE', 3, wx.SOLID))
      dc.SetBrush(wx.BLACK_BRUSH)
      dc.SetLogicalFunction(wx.XOR)
      for time, logEventList in self.timelineInfo.iteritems():
         for logEvent in logEventList:
            if 'teamcenter' in logEvent.lower() and not self.tcTime: continue
            if 'user' in logEvent.lower() and not self.userTime: continue
            if 'download' in logEvent.lower() and not self.dlTime: continue
            textAbove = CustomText.RotatedText(logEvent, (time, 0), 90)
            timeBelow = CustomText.RotatedText(str(time), (time, 0), 0)
            self.canvas.Canvas.AddObject(textAbove)
            self.canvas.Canvas.AddObject(timeBelow)
            self.canvas.Canvas.AddLine([(time, 0),(time, 25)])
            # self.canvas.Canvas.AddText(logEvent, (time, 25), Size=7)

      self.canvas.Canvas.ZoomToBB(None, True)
