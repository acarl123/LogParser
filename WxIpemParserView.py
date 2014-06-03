# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Feb 26 2014)
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
		
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
		
		gbSizer1 = wx.GridBagSizer( 0, 0 )
		gbSizer1.SetFlexibleDirection( wx.BOTH )
		gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.calcButton = wx.Button( self.mainPanel, wx.ID_ANY, u"Calculate", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.calcButton.SetDefault() 
		gbSizer1.Add( self.calcButton, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		
		bSizer7.Add( gbSizer1, 1, wx.EXPAND, 5 )
		
		self.clearButton = wx.Button( self.mainPanel, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer7.Add( self.clearButton, 0, wx.ALL, 5 )
		
		
		bSizer5.Add( bSizer7, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		mainPanelSizer.Add( bSizer5, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.mainPanel.SetSizer( mainPanelSizer )
		self.mainPanel.Layout()
		mainPanelSizer.Fit( self.mainPanel )
		mainSizer.Add( self.mainPanel, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( mainSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		#self.logFilePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.logFilePickerOnFileChanged )
		#self.LogFileListCtrl.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.LogFileListCtrlOnListItemRightClick )
		#self.LogFileListCtrl.Bind( wx.EVT_LIST_KEY_DOWN, self.LogFileListCtrlOnListKeyDown )
		#self.calcButton.Bind( wx.EVT_BUTTON, self.calcButtonOnButtonClick )
		#self.clearButton.Bind( wx.EVT_BUTTON, self.clearButtonOnButtonClick )
	
	def __del__( self ):
		pass
	

	# Virtual event handlers, overide them in your derived class
	#def logFilePickerOnFileChanged( self, event ):
		#event.Skip()

	#def LogFileListCtrlOnListItemRightClick( self, event ):
		#event.Skip()

	#def LogFileListCtrlOnListKeyDown( self, event ):
		#event.Skip()

	#def calcButtonOnButtonClick( self, event ):
		#event.Skip()

	#def clearButtonOnButtonClick( self, event ):
		#event.Skip()
	

