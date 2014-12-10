from collections import defaultdict, Counter
from ParserView import LogView
from ParserDetailsController import ParserDetailsController
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
      self.mainWindow.LogFileListCtrl.DragAcceptFiles(True)

      # Bind events
      self.mainWindow.LogFileListCtrl.Bind(wx.EVT_LIST_KEY_DOWN, self.onDelete)
      self.mainWindow.btnAddFiles.Bind(wx.EVT_BUTTON, self.onFile)
      self.mainWindow.calcButton.Bind(wx.EVT_BUTTON, self.onCalc)
      self.mainWindow.clearButton.Bind(wx.EVT_BUTTON, self.onClear)
      self.mainWindow.LogFileListCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onRClick)
      self.mainWindow.LogFileListCtrl.Bind(wx.EVT_DROP_FILES, self.onFile)
      self.mainWindow.displaySummaryListCtrl.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.onColRClick)
      self.dirPaths = []

      # Setup view

   def show(self, *args):
      self.mainWindow.Show()

   def onFile(self, event):
      try:
         filelist = event.GetFiles()
      except:
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
      try:
         key = event.GetKeyCode()
         if not key == wx.WXK_DELETE: return
      except AttributeError: pass
      finally:
         indexList = []
         index = self.mainWindow.LogFileListCtrl.GetNextSelected(-1)
         indexList.append(index)
         while index != -1:
            index = self.mainWindow.LogFileListCtrl.GetNextSelected(index)
            indexList.append(index)

         for counter, index in enumerate(list(set(indexList))):
            self.mainWindow.LogFileListCtrl.DeleteItem(index-counter)

   def onColRClick(self, event):
      col = event.m_col
      if col <= 0: return
      if not hasattr(self, 'popupId2'):
         self.popupId2 = wx.NewId()
         self.mainWindow.Bind(wx.EVT_MENU, self.onDetails, id=self.popupId2)

      menu = wx.Menu()
      menu.Append(self.popupId2, 'View Details...')

      self.mainWindow.PopupMenu(menu)
      menu.Destroy()

   def onDetails(self, event):
      detailsController = ParserDetailsController(self.mainWindow,)
      detailsController.show()

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
         # worker.setDaemon(True)
         worker.start()

   def calcTimes(self, data, logFileName):
      self.mainWindow.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
      currentOpDict = {
         'open': False,
         'save': False,
         'manage': False
         }
      opCountDict = defaultdict(int)
      opTimeDict = Counter({
         'totalOp'   : 0,
         'user'      : 0,
         'teamcenter': 0,
         'download'  : 0,
      })
      auxTimeDict = Counter({
         'user'      : 0,
         'teamcenter': 0,
         'download'  : 0,
      })
      emptyAuxTimeDict = auxTimeDict
      tempList = []
      errList = []
      currentTaskDict = {}
      auxTaskDict = {}

      for line in data:
         try:
            numberInLine = re.search(r'[0-9]*\.[0-9]*.:', line)
            if numberInLine: numberInLine = float(numberInLine.group()[:-2])

            # Open Time
            if openStartKeyword in line.lower():
               auxTimeDict = emptyAuxTimeDict.copy()
               currentTaskDict = {}
               auxTaskDict = {}
               currentTaskDict['open'] = numberInLine
            #    currentOpDict['open'] = True
            #    openStartTime = float(numberInLine.group(0)[:-2])
               tempList.append(line)
            #
            if any(key in line.lower() for key in openEndKeyWordList) and currentTaskDict.get('open'):
               opCountDict['open'] += 1
            #    currentOpDict['open'] = False
               opTimeDict['totalOp'] += (numberInLine - currentTaskDict['open'])
               opTimeDict = opTimeDict + auxTimeDict
               tempList.append('%s %s\n' % (line, opTimeDict))
               currentTaskDict = {}
               auxTaskDict = {}
            #
            # Save time
            if saveStartKeyword in line.lower():
               auxTimeDict = emptyAuxTimeDict.copy()
               currentTaskDict = {}
               auxTaskDict = {}
               currentTaskDict['save'] = numberInLine
            #    currentOpDict['save'] = True
            #    saveStartTime = float(numberInLine.group(0)[:-2])
               tempList.append(line)
            #
            if any(key in line.lower() for key in saveEndKeyWordList) and currentTaskDict.get('save'):
               opCountDict['save'] += 1
            #    currentOpDict['save'] = False
               opTimeDict['totalOp'] += (numberInLine - currentTaskDict['save'])
               opTimeDict = opTimeDict + auxTimeDict
               tempList.append('%s %s\n' % (line, opTimeDict))
               currentTaskDict = {}
               auxTaskDict = {}
            #    if 'userStartTime' in locals():
            #       opCountDict['user'] -= 1
            #       del userStartTime
            #
            # Manage time
            if manStartKeyword in line.lower() and not currentOpDict['manage']:
               auxTimeDict = emptyAuxTimeDict.copy()
               currentTaskDict = {}
               auxTaskDict = {}
               currentTaskDict['manage'] = numberInLine
            #    currentOpDict['manage'] = True
            #    manStartTime = float(numberInLine.group(0)[:-2])
            #
            if any(key in line.lower() for key in manEndKeyWordList) and currentTaskDict.get('manage'):
               opCountDict['manage'] += 1
            #    currentOpDict['manage'] = False
               opTimeDict['totalOp'] += (numberInLine - currentTaskDict['manage'])
               opTimeDict = opTimeDict + auxTimeDict
               currentTaskDict = {}
               auxTaskDict = {}
            #
            # if not any(value for value in currentOpDict.itervalues()):continue# outOfLoop = True
            #
            if not currentTaskDict: continue

            # User time
            if userTimeStartKeyword in line.lower():
               auxTaskDict['user'] = numberInLine
            #    userStartTime = float(numberInLine.group(0)[:-2])
               tempList.append(line)
            #
            if any(key in line.lower() for key in userTimeEndKeyword) and auxTaskDict.get('user'):
            #    # if outOfLoop: del userStartTime;outOfLoop=False;continue
               auxTimeDict['user'] += (numberInLine - auxTaskDict['user'])
               auxTaskDict['user'] = None
            #    del userStartTime
               tempList.append('%s %s\n' % (line, opTimeDict))
            #
            # Teamcenter time
            if tcStartKeywords in line.lower():
               try:
                  auxTaskDict['teamcenter'] = numberInLine
                  # opCountDict['teamcenter'] += 1
               except:
                  print 'time not found, possible corrupted log file'
            #
            if tcEndKeywords in line.lower() and auxTaskDict.get('teamcenter'):
               try:
                  auxTimeDict['teamcenter'] += (numberInLine - auxTaskDict['teamcenter'])
               except:
                  print 'time not found, possible corrupted log file'
               auxTaskDict['teamcenter'] = None
            #
            # Download time
            if downloadStartKeywords in line.lower():
               auxTaskDict['download'] = numberInLine
            #    opCountDict['download'] += 1
            #    downloadStartTime = float(numberInLine.group(0)[:-2])
            #
            if downloadEndKeywords in line.lower() and auxTaskDict.get('download'):
               auxTimeDict['download'] += (numberInLine - auxTaskDict['download'])
               auxTaskDict['download'] = None
            #    del downloadStartTime

         except Exception, e:
            print e
            errList.append('\n%s in line %s\n' % (e, line))

      opTimeDict['totalOpNoUser'] = opTimeDict['totalOp'] - opTimeDict['user']
      opTimeDict['integration'] = opTimeDict['totalOpNoUser'] - opTimeDict['teamcenter'] - opTimeDict['download']
      opCountDict['total'] = opCountDict['save'] + opCountDict['open'] + opCountDict['manage']

      with open('debugFile.txt', 'w+') as debugFile:
         debugFile.writelines(tempList)
         debugFile.writelines(errList)

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