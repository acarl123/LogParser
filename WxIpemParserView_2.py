# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2013)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class LogView
###########################################################################

class LogView ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,520 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 500,-1 ), wx.DefaultSize )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.mainPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		mainPanelSizer = wx.BoxSizer( wx.VERTICAL )
		
		bSizer51 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText2 = wx.StaticText( self.mainPanel, wx.ID_ANY, u"Choose Log Files", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		bSizer51.Add( self.m_staticText2, 0, wx.ALL, 5 )
		
		self.logFilePicker = wx.FilePickerCtrl( self.mainPanel, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_CHANGE_DIR|wx.FLP_DEFAULT_STYLE )
		bSizer51.Add( self.logFilePicker, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		mainPanelSizer.Add( bSizer51, 0, wx.ALL|wx.EXPAND, 5 )
		
		optionsSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.LogFileListCtrl = wx.ListCtrl( self.mainPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_LIST )
		optionsSizer.Add( self.LogFileListCtrl, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		mainPanelSizer.Add( optionsSizer, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer81 = wx.BoxSizer( wx.VERTICAL )
		
		self.displaySummaryListCtrl = wx.ListCtrl( self.mainPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT|wx.LC_VRULES )
		bSizer81.Add( self.displaySummaryListCtrl, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer5.Add( bSizer81, 1, wx.EXPAND, 5 )
		
		
		mainPanelSizer.Add( bSizer5, 1, wx.ALL|wx.EXPAND, 5 )
		
		standardButtonSizer = wx.StdDialogButtonSizer()
		self.standardButtonSizerOK = wx.Button( self.mainPanel, wx.ID_OK )
		standardButtonSizer.AddButton( self.standardButtonSizerOK )
		self.standardButtonSizerCancel = wx.Button( self.mainPanel, wx.ID_CANCEL )
		standardButtonSizer.AddButton( self.standardButtonSizerCancel )
		standardButtonSizer.Realize();
		
		mainPanelSizer.Add( standardButtonSizer, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.mainPanel.SetSizer( mainPanelSizer )
		self.mainPanel.Layout()
		mainPanelSizer.Fit( self.mainPanel )
		mainSizer.Add( self.mainPanel, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( mainSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		

	
	def __del__( self ):
		pass
	
	


