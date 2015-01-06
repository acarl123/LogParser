from wx.lib.floatcanvas import GUIMode, FloatCanvas
import wx

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