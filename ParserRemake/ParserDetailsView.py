# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from wx.lib.floatcanvas import FloatCanvas, NavCanvas
###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 600,400 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.lblIPEMTime = wx.StaticText( self.m_panel1, wx.ID_ANY, u"IPEM Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		# self.lblIPEMTime.SetValue(True)
		self.lblIPEMTime.Wrap( -1 )
		gSizer1.Add( self.lblIPEMTime, 0, wx.ALL, 5 )
		
		self.lblTotalOpNoUser = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Total Op w/o User Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblTotalOpNoUser.Wrap( -1 )
		gSizer1.Add( self.lblTotalOpNoUser, 0, wx.ALL, 5 )
		
		self.lblTCTime = wx.CheckBox( self.m_panel1, wx.ID_ANY, u"Teamcenter Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblTCTime.SetValue(True)
		# self.lblTCTime.Wrap( -1 )
		gSizer1.Add( self.lblTCTime, 0, wx.ALL, 5 )
		
		self.lblTotalSave = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Number of Save Ops:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblTotalSave.Wrap( -1 )
		gSizer1.Add( self.lblTotalSave, 0, wx.ALL, 5 )
		
		self.lblUserTime = wx.CheckBox( self.m_panel1, wx.ID_ANY, u"User Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblUserTime.SetValue(True)
		# self.lblUserTime.Wrap( -1 )
		gSizer1.Add( self.lblUserTime, 0, wx.ALL, 5 )
		
		self.lblTotalOpen = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Number of Open Ops:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblTotalOpen.Wrap( -1 )
		gSizer1.Add( self.lblTotalOpen, 0, wx.ALL, 5 )
		
		self.lblDLTime = wx.CheckBox( self.m_panel1, wx.ID_ANY, u"Download Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblDLTime.SetValue(True)
		# self.lblDLTime.Wrap( -1 )
		gSizer1.Add( self.lblDLTime, 0, wx.ALL, 5 )
		
		self.lblTotalMan = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Number of Manage Ops:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblTotalMan.Wrap( -1 )
		gSizer1.Add( self.lblTotalMan, 0, wx.ALL, 5 )
		
		self.lblTotalOp = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Total Operation Time:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblTotalOp.Wrap( -1 )
		gSizer1.Add( self.lblTotalOp, 0, wx.ALL, 5 )
		
		self.lblTotal = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Total Number of Ops:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblTotal.Wrap( -1 )
		gSizer1.Add( self.lblTotal, 0, wx.ALL, 5 )
		
		
		self.m_panel1.SetSizer( gSizer1 )
		self.m_panel1.Layout()
		gSizer1.Fit( self.m_panel1 )
		bSizer1.Add( self.m_panel1, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.canvas = NavCanvas.NavCanvas(self.m_panel2, Debug=0, BackgroundColor=(120, 172, 255))
		bSizer2.Add( self.canvas, 1, wx.GROW )
		
		
		self.m_panel2.SetSizer( bSizer2 )
		self.m_panel2.Layout()
		bSizer2.Fit( self.m_panel2 )
		bSizer1.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
