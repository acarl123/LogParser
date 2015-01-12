from wx.lib.floatcanvas import GUIMode, FloatCanvas, NavCanvas, Resources
# from Utilities import BBox
import wx
import numpy as N

class RotatedText( FloatCanvas.Text ):
   def __init__(self,String, xy, angle,
                 Size =  10,
                 Color = "Black",
                 BackgroundColor = None,
                 Family = wx.MODERN,
                 Style = wx.NORMAL,
                 Weight = wx.NORMAL,
                 Underlined = False,
                 Position = 'tl',
                 InForeground = False,
                 Font = None):
      FloatCanvas.Text.__init__(self, String, xy,
                                Size,
                                Color,
                                BackgroundColor,
                                Family,
                                Style,
                                Weight,
                                Underlined,
                                Position,
                                InForeground,
                                Font)
      self.angle = angle
   def _Draw(self, dc , WorldToPixel, ScaleWorldToPixel, HTdc=None):
      XY = WorldToPixel(self.XY)
      dc.SetFont(self.Font)
      dc.SetTextForeground(self.Color)
      if self.BackgroundColor:
         dc.SetBackgroundMode(wx.SOLID)
         dc.SetTextBackground(self.BackgroundColor)
      else:
         dc.SetBackgroundMode(wx.TRANSPARENT)
      if self.TextWidth is None or self.TextHeight is None:
         (self.TextWidth, self.TextHeight) = dc.GetTextExtent(self.String)
      XY = self.ShiftFun(XY[0], XY[1], self.TextWidth, self.TextHeight)
      dc.DrawRotatedTextPoint(self.String, XY, self.angle)
      if HTdc and self.HitAble:
         HTdc.SetPen(self.HitPen)
         HTdc.SetBrush(self.HitBrush)
         HTdc.DrawRectanglePointSize(XY, (self.TextWidth, self.TextHeight) )

class CustomCanvas( NavCanvas.NavCanvas, wx.Panel):
   def __init__(self, parent, id=wx.ID_ANY, size=wx.DefaultSize, **kwargs):
      wx.Panel.__init__(self, parent, id, size=size)
      self.Modes = [("Pointer", GUIMode.GUIMouse(), Resources.getPointerBitmap()),
                   ("Zoom In",  NavGuiZoomIn(),  Resources.getMagPlusBitmap()),
                   ("Zoom Out", NavGuiZoomOut(), Resources.getMagMinusBitmap()),
                   ("Pan", NavGuiMove(), Resources.getHandBitmap()),
                   ]
      self.timeLine = None
      self.BuildToolbar()
      box = wx.BoxSizer(wx.VERTICAL)
      box.Add(self.ToolBar, 0, wx.ALL | wx.ALIGN_LEFT | wx.GROW, 1)

      self.Canvas = FloatCanvas.FloatCanvas(self, **kwargs)
      box.Add(self.Canvas, 1, wx.ALL | wx.EXPAND)

      self.SetSizerAndFit(box)

   def BuildToolbar(self): # overrides default to add clear button
      tb = wx.ToolBar(self)
      self.ToolBar = tb
      tb.SetToolBitmapSize((16, 16))
      self.AddToolbarModeButtons(tb, self.Modes)
      self.AddToolbarZoomButton(tb)
      tb.Realize()

   def AddToolbarModeButtons(self, tb, Modes):
      self.ModesDict = {}
      for Mode in Modes:
          tool = tb.AddRadioTool(wx.ID_ANY, shortHelp=Mode[0], bitmap=Mode[2])
          self.Bind(wx.EVT_TOOL, self.SetMode, tool)
          self.ModesDict[tool.GetId()]=Mode[1]

   def AddToolbarZoomButton(self, tb):
      tb.AddSeparator()
      self.ZoomButton = wx.Button(tb, label="Zoom To Fit")
      tb.AddControl(self.ZoomButton)
      self.ZoomButton.Bind(wx.EVT_BUTTON, self.ZoomToFit)

   def ZoomToFit(self, event):
      super(CustomCanvas, self).ZoomToFit(event)

class NavGuiZoomIn( GUIMode.GUIZoomIn ):
   def __init__(self, event=None, canvas=None):
      super(NavGuiZoomIn, self).__init__(canvas)
      self.Canvas = canvas
      self.event = event

   def OnMove(self, evt):
      """ Must pass this method to overwrite all onDrag events."""
      pass

   def OnLeftUp(self, event):
        if event.LeftUp() and not self.StartRBBox is None:
            self.PrevRBBox = None
            EndRBBox = event.GetPosition()
            StartRBBox = self.StartRBBox
            # if mouse has moved less that ten pixels, don't use the box.
            if ( abs(StartRBBox[0] - EndRBBox[0]) > 10
                    and abs(StartRBBox[1] - EndRBBox[1]) > 10 ):
                EndRBBox = self.Canvas.PixelToWorld(EndRBBox)
                StartRBBox = self.Canvas.PixelToWorld(StartRBBox)
                # self.Canvas.ZoomToBB( BBox.fromPoints(N.r_[EndRBBox,StartRBBox]) )
            else:
                StartRBBox = StartRBBox[0],240
                Center = self.Canvas.PixelToWorld(StartRBBox)
                self.Canvas.Zoom(1.5, Center)
            self.StartRBBox = None

class NavGuiZoomOut( GUIMode.GUIZoomOut):
   def __init__(self, event=None, canvas=None):
        super(NavGuiZoomOut, self).__init__(canvas)
        self.Canvas = canvas
        self.event = event
   def OnLeftDown(self, event):
        xy = event.GetPosition()[0], 117
        Center = self.Canvas.PixelToWorld(xy)
        self.Canvas.Zoom(1/1.5, Center)

   def OnRightDown(self, event):
        self.Canvas.Zoom(1.5, event.GetPosition(), centerCoords="pixel")

class NavGuiMove( GUIMode.GUIMove ):
   def __init__(self, event=None, canvas=None):
      super(NavGuiMove, self).__init__(canvas)
      self.Canvas = canvas
      self.event = event

   def OnMove(self, event):
      self.Canvas._RaiseMouseEvent(event, FloatCanvas.EVT_FC_MOTION)
      if event.Dragging() and event.LeftIsDown() and not self.StartMove is None:
         self.EndMove = event.GetPosition()
         self.MoveImage(event) ## This call shows the pan as it happens on both the x axis and y axis.
         DiffMove = self.MidMove - self.EndMove
         DiffMove = DiffMove[0], 0
         self.Canvas.MoveImage(DiffMove, 'Pixel', ReDraw=False)  # This call does the final pan along the x axis only
         self.MidMove = self.EndMove
         self.MoveTimer.Start(30, oneShot=True)

   def OnMiddleUp(self, event):
      pass

   def __del__(self):
      self.OnLeftUp(self.event)
      self.MoveTimer.Stop()

   def MoveImage(self, event ):
      #xy1 = N.array( event.GetPosition() )
      xy1 = self.EndMove
      wh = self.Canvas.PanelSize
      xy_tl = xy1 - self.StartMove
      dc = wx.ClientDC(self.Canvas)
      dc.BeginDrawing()
      x1,y1 = self.PrevMoveXY
      x2,y2 = xy_tl
      w,h = self.Canvas.PanelSize

      ##fixme: This sure could be cleaner!
      ##   This is all to fill in the background with the background color
      ##   without flashing as the image moves.
      if x2 > x1 and y2 > y1:
         xa = xb = x1
         ya = yb = y1
         wa = w
         ha = y2 - y1
         wb = x2-  x1
         hb = h
      elif x2 > x1 and y2 <= y1:
         xa = x1
         ya = y1
         wa = x2 - x1
         ha = h
         xb = x1
         yb = y2 + h
         wb = w
         hb = y1 - y2
      elif x2 <= x1 and y2 > y1:
         xa = x1
         ya = y1
         wa = w
         ha = y2 - y1
         xb = x2 + w
         yb = y1
         wb = x1 - x2
         hb = h - y2 + y1
      elif x2 <= x1 and y2 <= y1:
         xa = x2 + w
         ya = y1
         wa = x1 - x2
         ha = h
         xb = x1
         yb = y2 + h
         wb = w
         hb = y1 - y2

      dc.SetPen(wx.TRANSPARENT_PEN)
      dc.SetBrush(self.Canvas.BackgroundBrush)
      dc.DrawRectangle(xa, ya, wa, ha)
      dc.DrawRectangle(xb, yb, wb, hb)
      self.PrevMoveXY = xy_tl
      xy_tl = xy_tl[0], 0
      if self.Canvas._ForeDrawList:
         dc.DrawBitmapPoint(self.Canvas._ForegroundBuffer,xy_tl)
      else:
         dc.DrawBitmapPoint(self.Canvas._Buffer,xy_tl)
      dc.EndDrawing()
      #self.Canvas.Update()