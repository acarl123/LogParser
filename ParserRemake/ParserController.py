from collections import defaultdict
from ParserView import LogView
import wx
import os, sys, re, threading


openStartKeyword = "perf: teamcenter -> open begins"
openEndKeyWordList = ["perf: open from teamcenter complete",
                      "exiting operationcollectiondialog.cancelaction for teamcenter open"]

saveStartKeyword = "perf: teamcenter -> save as begins"
saveEndKeyWordList = ["perf: save to teamcenter complete",
                      "exiting operationcollectiondialog.cancelaction for teamcenter save as"]

manStartKeyword = "perf: manager begins"
manEndKeyWordList = ["perfsum: manager complete",
                     "exiting operationcollectiondialog.cancelaction for teamcenter manager"]

userTimeStartKeyword = "pausing perf sum"
userTimeEndKeyword = ["beginning perf sum", "resuming perf sum"]

tcStartKeywords = "service request"
tcEndKeywords = "service response"

downloadStartKeywords = "perf: fcc call starts - downloadfilestolocation"
downloadEndKeywords = "perf: fcc call ends - downloadfilestolocation"


class MainController:
   def __init__(self):
      # Init member vars
      self.mainWindow = LogView(None)
      self.totalOpenTime = 0

      # Bind events
      self.mainWindow.btnAddFiles.Bind(wx.EVT_BUTTON, self.onFile)
      self.mainWindow.calcButton.Bind(wx.EVT_BUTTON, self.onCalc)
      self.mainWindow.clearButton.Bind(wx.EVT_BUTTON, self.onClear)
      self.mainWindow.LogFileListCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onRClick)
      self.dirPaths = []

      # Setup view

   def show(self, *args):
      self.mainWindow.Show()

   def onFile(self, event):
      logFilePicker = wx.FileDialog(self.mainWindow, 'Choose a File', "", "",
                             u"log files (*.txt, *.log)|*.txt; *.log|All Files (*.*)|*.*", wx.MULTIPLE)
      if logFilePicker.ShowModal() == wx.ID_OK:
         filelist = logFilePicker.GetPaths()
      else:
         return

      for logFile in filelist:
         self.dirPaths.append(os.path.dirname(logFile))

         self.mainWindow.LogFileListCtrl.InsertStringItem(self.mainWindow.LogFileListCtrl.GetItemCount(), str(os.path.basename(logFile)))

   def onRClick(self, event):
      if self.mainWindow.LogFileListCtrl.GetNextSelected(-1) < 0: return
      menu = wx.Menu()
      if not hasattr(self, 'popupID1'):
         self.popupID1 = wx.NewId()
         self.mainWindow.Bind(wx.EVT_MENU, self.onDelete, id=self.popupID1)
      menu.Append(self.popupID1,'Delete')
      self.mainWindow.PopupMenu(menu)
      menu.Destroy()

   def onDelete(self, event):
      self.mainWindow.LogFileListCtrl.DeleteItem(self.mainWindow.LogFileListCtrl.GetNextSelected(-1))

   def onCalc(self, event):
      if self.mainWindow.LogFileListCtrl.ItemCount == 0: return
      self.onClear()
      self.initList()
      threads = []
      for fileIndex in xrange(self.mainWindow.LogFileListCtrl.GetItemCount()):
         logFileName = os.path.join(self.dirPaths[fileIndex], self.mainWindow.LogFileListCtrl.GetItemText(fileIndex))

         with open(logFileName, 'r') as log:
            read_data = log.readlines()

         worker = Worker(name=logFileName, target=self.calcTimes, args=(read_data, logFileName), callafter=self.populateList)
         threads.append(worker)
         worker.setDaemon(True)
         worker.start()

   def calcTimes(self, data, logFileName):
      self.mainWindow.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      currentOpDict = {
         'open': False,
         'save': False,
         'manage': False
         }
      opCountDict = defaultdict(int)
      opTimeDict = defaultdict(int)

      for line in data:
         numberInLine = re.search(r'[0-9]*\.[0-9]*.:', line)

         # Open Time
         if openStartKeyword in line.lower():
            opCountDict['open'] += 1
            currentOpDict['open'] = True
            openStartTime = float(numberInLine.group(0)[:-2])

         if any(key in line.lower() for key in openEndKeyWordList):
            currentOpDict['open'] = False
            opTimeDict['totalOp'] += (float(numberInLine.group(0)[:-2]) - openStartTime)

         # Save time
         if saveStartKeyword in line.lower():
            opCountDict['save'] += 1
            currentOpDict['save'] = True
            saveStartTime = float(numberInLine.group(0)[:-2])

         if any(key in line.lower() for key in saveEndKeyWordList):
            currentOpDict['save'] = False
            opTimeDict['totalOp'] += (float(numberInLine.group(0)[:-2]) - saveStartTime)

         # Manage time
         if manStartKeyword in line.lower():
            opCountDict['manage'] += 1
            currentOpDict['manage'] = True
            manStartTime = float(numberInLine.group(0)[:-2])

         if any(key in line.lower() for key in manEndKeyWordList):
            currentOpDict['manage'] = False
            opTimeDict['totalOp'] += (float(numberInLine.group(0)[:-2]) - manStartTime)

         # if not any(value for value in currentOpDict.itervalues()): continue

         # User time
         if userTimeStartKeyword in line.lower():
            opCountDict['user'] += 1
            currentOpDict['user'] = True
            userStartTime = float(numberInLine.group(0)[:-2])

         if any(key in line.lower() for key in userTimeEndKeyword) and 'userStartTime' in locals():
            currentOpDict['user'] = False
            print line
            opTimeDict['user'] += (float(numberInLine.group(0)[:-2]) - userStartTime)
            del userStartTime

         # Teamcenter time
         if tcStartKeywords in line.lower():
            try:
               tcStartTime = float(numberInLine.group(0)[:-2])
               opCountDict['teamcenter'] += 1
               currentOpDict['teamcenter'] = True
            except:
               print 'time not found, possible corrupted log file'

         if tcEndKeywords in line.lower() and 'tcStartTime' in locals():
            currentOpDict['teamcenter'] = False
            try:
               opTimeDict['teamcenter'] += (float(numberInLine.group(0)[:-2]) - tcStartTime)
            except:
               print 'time not found, possible corrupted log file'
            del tcStartTime

         # Download time
         if downloadStartKeywords in line.lower():
            opCountDict['download'] += 1
            currentOpDict['download'] = True
            downloadStartTime = float(numberInLine.group(0)[:-2])

         if downloadEndKeywords in line.lower() and 'downloadStartTime' in locals():
            currentOpDict['download'] = False
            opTimeDict['download'] += (float(numberInLine.group(0)[:-2]) - downloadStartTime)
            del downloadStartTime

      opTimeDict['totalOpNoUser'] = opTimeDict['totalOp'] - opTimeDict['user']
      opTimeDict['integration'] = opTimeDict['totalOpNoUser'] - opTimeDict['teamcenter'] - opTimeDict['download']
      opCountDict['total'] = opCountDict['save'] + opCountDict['open'] + opCountDict['manage']

      return opTimeDict, opCountDict, logFileName

   def populateList(self, times, count, colName):
      curCol = self.mainWindow.displaySummaryListCtrl.ColumnCount
      self.mainWindow.displaySummaryListCtrl.InsertColumn(curCol, os.path.basename(colName))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(0, curCol, str(times['integration']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(1, curCol, str(times['teamcenter']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(2, curCol, str(times['user']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(3, curCol, str(times['download']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(4, curCol, str(times['totalOp']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(5, curCol, str(times['totalOpNoUser']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(6, curCol, str(count['save']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(7, curCol, str(count['open']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(8, curCol, str(count['manage']))
      self.mainWindow.displaySummaryListCtrl.SetStringItem(9, curCol, str(count['total']))

      if len(threading.enumerate()) <= 2:
         self.mainWindow.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

      # for some reason, altering width was the only way I could get the scroll bar on the bottom to update
      if self.mainWindow.Size == (550, 520):
         self.mainWindow.SetSize((549, 520))
      else:
         self.mainWindow.SetSize((550, 520))

   def initList(self):
      self.mainWindow.displaySummaryListCtrl.InsertColumn(0, '', width=150)
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(0, 'IPEM Time')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(1, 'Teamcenter Time')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(2, 'User Time')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(3, 'Download Time')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(4, 'Total Operation Time')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(5, 'Total Op w/o User Time')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(6, 'Total Save Ops')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(7, 'Total Open Ops')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(8, 'Total Manage Ops')
      self.mainWindow.displaySummaryListCtrl.InsertStringItem(9, 'Total Ops')

   def onClear(self, event=None):
      self.mainWindow.displaySummaryListCtrl.ClearAll()


class Worker( threading.Thread ):
   def on_thread_finished(self, thread, data):
        self.callback(*self.args)

   def __init__(self, parent=None, name=None, target=None, callafter=None, args=(), kwargs={}):
      threading.Thread.__init__(self, name=name, target=target, args=args, kwargs=kwargs)
      self.parent = parent
      self.target = target
      self.callback = callafter
      self.args = args
      self.kwargs = kwargs

   def run(self):
      self.args = self.target(*self.args, **self.kwargs)
      self and self.on_thread_finished(self, 42)