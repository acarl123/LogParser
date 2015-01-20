from collections import defaultdict, Counter
from ParserView import LogView
from ParserDetailsController import ParserDetailsController
import wx
import time
import os, sys, re, threading

sys.path.append(r'c:\hg\tools_lag\EFS_Utils')
import Excel


openStartKeyword = "perf: teamcenter -> open begins"
openEndKeyWordList = ["perf: open from teamcenter complete",
                      "exiting operationcollectiondialog.cancelaction for teamcenter open",
                      "Exiting Operations.cancelCheckOut".lower()]

saveStartKeyword = "perf: teamcenter -> save as begins"
saveEndKeyWordList = ["perf: save to teamcenter complete",
                      "exiting operationcollectiondialog.cancelaction for teamcenter save as",
                      "Save to Teamcenter may have been unsuccessful".lower()]

manStartKeyword = "perf: manager begins"
manEndKeyWordList = ["perfsum: manager complete",
                     "exiting operationcollectiondialog.cancelaction for teamcenter manager"]

userTimeStartKeyword = "pausing perf sum"
userTimeEndKeyword = ["beginning perf sum", "resuming perf sum"]

tcStartKeywords = "service request"
tcEndKeywords = "service response"

downloadStartKeywords = "perf: fcc call starts - downloadfilestolocation"
downloadEndKeywords = "perf: fcc call ends - downloadfilestolocation"

# SWIM only
CADStartKeyword = 'open command <?xml version'
CADEndKeyword = 'number of bytes reported by cadscript:'


class MainController:
   def __init__(self):
      # Init member vars
      self.mainWindow = LogView(None)
      self.mainWindow.Raise()
      self.mainWindow.LogFileListCtrl.DragAcceptFiles(True)
      self.details = defaultdict(dict)
      self.count = defaultdict(dict)
      self.timelineDict = defaultdict(dict)

      # Bind events
      self.mainWindow.LogFileListCtrl.Bind(wx.EVT_LIST_KEY_DOWN, self.onDelete)
      self.mainWindow.calcButton.Bind(wx.EVT_BUTTON, self.onCalc)
      self.mainWindow.clearButton.Bind(wx.EVT_BUTTON, self.onClear)
      self.mainWindow.LogFileListCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onRClick)
      self.mainWindow.LogFileListCtrl.Bind(wx.EVT_DROP_FILES, self.onFile)
      self.mainWindow.displaySummaryListCtrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onItemRClick)
      self.mainWindow.Bind(wx.EVT_COMMAND_ENTER, self.onCalc)

      # Bind menu events
      self.mainWindow.Bind(wx.EVT_MENU, self.onFile, self.mainWindow.menuAdd)
      self.mainWindow.Bind(wx.EVT_MENU, self.exit, self.mainWindow.menuExit)
      self.mainWindow.Bind(wx.EVT_MENU, self.onExport, self.mainWindow.menuExport)

      self.dirPaths = []

   def exit(self, event):
      sys.exit()

   def show(self, *args):
      self.mainWindow.Show()

   def onFile(self, event):
      try:
         filelist = event.GetFiles()
         self.mainWindow.Raise()
      except:
         logFilePicker = wx.FileDialog(self.mainWindow, 'Choose a File', "", "",
                                u"log files (*.txt, *.log)|*.txt; *.log|All Files (*.*)|*.*", wx.MULTIPLE)
         if logFilePicker.ShowModal() == wx.ID_OK:
            filelist = logFilePicker.GetPaths()
         else:
            return

      for logFile in filelist:
         listLogFiles = []
         for item in xrange(self.mainWindow.LogFileListCtrl.GetItemCount()):
            fileItem = self.mainWindow.LogFileListCtrl.GetItem(itemId=item, col=0)
            listLogFiles.append(fileItem.GetText())
         if str(os.path.basename(logFile)) in listLogFiles: continue
         self.mainWindow.LogFileListCtrl.InsertStringItem(self.mainWindow.LogFileListCtrl.GetItemCount(), str(os.path.basename(logFile)))
         self.dirPaths.append(os.path.dirname(logFile))

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
            if index == -1: break
            if self.dirPaths: self.dirPaths.pop(index-counter)
            self.mainWindow.LogFileListCtrl.DeleteItem(index-counter)

   def onItemRClick(self, event):
      # get all selected items
      current = -1
      next = 0
      selItemList = []
      while next != -1:
         next = self.mainWindow.displaySummaryListCtrl.GetNextSelected(current)
         if next != -1: selItemList.append(next)
         current = next

      if not hasattr(self, 'popupId2'):
         self.popupId2 = wx.NewId()
      self.mainWindow.Bind(wx.EVT_MENU, lambda event: self.onDetails(event, selItemList), id=self.popupId2)

      menu = wx.Menu()
      menu.Append(self.popupId2, 'View Details...')

      self.mainWindow.PopupMenu(menu)
      menu.Destroy()
      self.mainWindow.Unbind(wx.EVT_MENU, id=self.popupId2)

   def onDetails(self, event, items=[]):
      for item in items:
         detailsController = ParserDetailsController(self.mainWindow, self.details[item], self.count[item], self.timelineDict[item])
         detailsController.show()

   def onCalc(self, event):
      print self.dirPaths
      if self.mainWindow.LogFileListCtrl.ItemCount == 0: return
      wx.BeginBusyCursor()
      self.onClear()
      self.initList()
      self.startTime = time.clock()
      self.mainWindow.m_statusBar1.SetStatusText('Calculating...')
      threads = []
      for fileIndex in xrange(self.mainWindow.LogFileListCtrl.GetItemCount()):
         logFileName = os.path.join(self.dirPaths[fileIndex], self.mainWindow.LogFileListCtrl.GetItemText(fileIndex))

         with open(logFileName, 'r') as log:
            read_data = log.readlines()

         worker = Worker(name=logFileName, target=self.calcTimes, args=(read_data, logFileName, self.details), callafter=self.populateList)
         threads.append(worker)
         # worker.setDaemon(True)
         worker.start()

   def calcTimes(self, data, logFileName, details):
      # check if file was already calculated
      for key, value in details.iteritems():
         if logFileName == value['fileName']:
            time.sleep(0.2*threading.active_count()) # cheap way to make sure the threads don't try to update the list at the same time
            return value['times'], value['count'], value['fileName'], value['info']

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
      timelineDict = defaultdict(list)

      #check to make sure file is actual log file
      if 'INFO' not in data[0]: return {}, {}, logFileName

      firstLine = data[0]
      if 'Pro/ENGINEER' in firstLine: integrationType = 'IPEM'
      elif 'SolidWorks' in firstLine: integrationType = 'SWIM'

      # TODO: finish fully integrating SWIM
      for line in data:
         try:
            numberInLine = re.search(r'[0-9]*\.[0-9]*.:', line)
            if numberInLine: numberInLine = float(numberInLine.group()[:-2])

            # Open Time
            if openStartKeyword in line.lower():
               timelineDict[numberInLine].append('Start open operation')
               auxTimeDict = emptyAuxTimeDict.copy()
               currentTaskDict = {}
               auxTaskDict = {}
               currentTaskDict['open'] = numberInLine
               tempList.append(line)

            if any(key in line.lower() for key in openEndKeyWordList) and currentTaskDict.get('open'):
               timelineDict[numberInLine].append('End open operation')
               opCountDict['open'] += 1
               opTimeDict['totalOp'] += (numberInLine - currentTaskDict['open'])
               opTimeDict = opTimeDict + auxTimeDict
               tempList.append('%s %s\n' % (line, opTimeDict))
               currentTaskDict = {}
               auxTaskDict = {}

            # Save time
            if saveStartKeyword in line.lower():
               timelineDict[numberInLine].append('Start save operation')
               auxTimeDict = emptyAuxTimeDict.copy()
               currentTaskDict = {}
               auxTaskDict = {}
               currentTaskDict['save'] = numberInLine
               tempList.append(line)

            if any(key in line.lower() for key in saveEndKeyWordList) and currentTaskDict.get('save'):
               timelineDict[numberInLine].append('End save operation')
               opCountDict['save'] += 1
               opTimeDict['totalOp'] += (numberInLine - currentTaskDict['save'])
               opTimeDict = opTimeDict + auxTimeDict
               tempList.append('%s %s\n' % (line, opTimeDict))
               currentTaskDict = {}
               auxTaskDict = {}

            # Manage time
            if manStartKeyword in line.lower() and not currentOpDict['manage']:
               timelineDict[numberInLine].append('Start manage operation')
               auxTimeDict = emptyAuxTimeDict.copy()
               currentTaskDict = {}
               auxTaskDict = {}
               currentTaskDict['manage'] = numberInLine

            if any(key in line.lower() for key in manEndKeyWordList) and currentTaskDict.get('manage'):
               timelineDict[numberInLine].append('End manage operation')
               opCountDict['manage'] += 1
               opTimeDict['totalOp'] += (numberInLine - currentTaskDict['manage'])
               opTimeDict = opTimeDict + auxTimeDict
               currentTaskDict = {}
               auxTaskDict = {}

            if not currentTaskDict: continue

            # User time
            if userTimeStartKeyword in line.lower():
               timelineDict[numberInLine].append('Begin user interaction')
               auxTaskDict['user'] = numberInLine
               tempList.append(line)

            if any(key in line.lower() for key in userTimeEndKeyword) and auxTaskDict.get('user'):
               timelineDict[numberInLine].append('End user interaction')
               auxTimeDict['user'] += (numberInLine - auxTaskDict['user'])
               auxTaskDict['user'] = None
               tempList.append('%s %s\n' % (line, opTimeDict))

            # Teamcenter time
            if tcStartKeywords in line.lower():
               try:
                  timelineDict[numberInLine].append('Begin Teamcenter op')
                  auxTaskDict['teamcenter'] = numberInLine
               except:
                  print 'time not found, possible corrupted log file'

            if tcEndKeywords in line.lower() and auxTaskDict.get('teamcenter'):
               try:
                  timelineDict[numberInLine].append('End Teamcenter op')
                  auxTimeDict['teamcenter'] += (numberInLine - auxTaskDict['teamcenter'])
               except:
                  print 'time not found, possible corrupted log file'
               auxTaskDict['teamcenter'] = None

            # Download time
            if downloadStartKeywords in line.lower():
               timelineDict[numberInLine].append('Start download')
               auxTaskDict['download'] = numberInLine

            if downloadEndKeywords in line.lower() and auxTaskDict.get('download'):
               timelineDict[numberInLine].append('End download')
               auxTimeDict['download'] += (numberInLine - auxTaskDict['download'])
               auxTaskDict['download'] = None

         except Exception, e:
            print e
            errList.append('\n%s in line %s\n' % (e, line))

      opTimeDict['totalOpNoUser'] = opTimeDict['totalOp'] - opTimeDict['user']
      opTimeDict['integration'] = opTimeDict['totalOpNoUser'] - opTimeDict['teamcenter'] - opTimeDict['download']
      opCountDict['total'] = opCountDict['save'] + opCountDict['open'] + opCountDict['manage']

      with open('debugFile.txt', 'w+') as debugFile:
         debugFile.writelines(tempList)
         debugFile.writelines(errList)

      return opTimeDict, opCountDict, logFileName, timelineDict

   def populateList(self, times={}, count={}, fileName='', timeInfo={}):
      if not times:
         dlg = wx.MessageDialog(None, '%s is not a valid logfile, skipping...' % fileName, 'Invalid File', wx.OK|wx.ICON_EXCLAMATION)
         dlg.ShowModal()

      else:
         index = self.mainWindow.displaySummaryListCtrl.GetItemCount()
         self.mainWindow.displaySummaryListCtrl.InsertStringItem(index, str(os.path.basename(fileName)))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 1, str(times['integration']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 2, str(times['teamcenter']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 3, str(times['user']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 4, str(times['download']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 5, str(times['totalOp']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 6, str(times['totalOpNoUser']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 7, str(count['save']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 8, str(count['open']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 9, str(count['manage']))
         self.mainWindow.displaySummaryListCtrl.SetStringItem(index, 10, str(count['total']))
         self.details[index] = {'times':times,'count':count,'info':timeInfo,'fileName':fileName}
         self.count[index] = count
         self.timelineDict[index] = timeInfo

      if len(threading.enumerate()) <= 2:
         wx.EndBusyCursor()
         self.mainWindow.WarpPointer(wx.GetMousePosition().x - self.mainWindow.GetScreenPosition().x-5,
                                     wx.GetMousePosition().y - self.mainWindow.GetScreenPosition().y-50)
         self.mainWindow.m_statusBar1.SetStatusText('%s files calculated in %.2f seconds' % (self.mainWindow.displaySummaryListCtrl.GetItemCount(), time.clock() - self.startTime))

      self.mainWindow.Refresh()

   def initList(self):
      self.mainWindow.displaySummaryListCtrl.InsertColumn(0, 'Filename')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(1, 'IPEM Time')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(2, 'Teamcenter Time')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(3, 'User Time')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(4, 'Download Time')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(5, 'Total Operation Time')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(6, 'Total Op w/o User Time')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(7, 'Total Save Ops')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(8, 'Total Open Ops')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(9, 'Total Manage Ops')
      self.mainWindow.displaySummaryListCtrl.InsertColumn(10, 'Total Ops')

   def onClear(self, event=None):
      self.mainWindow.displaySummaryListCtrl.ClearAll()

   def onExport(self, event):
      fileDlg = wx.FileDialog(self.mainWindow, 'Choose a save file location', '', '', 'Excel files (*.xlsx)|*.xlsx', wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

      if fileDlg.ShowModal() == wx.ID_CANCEL: return

      reportFile = fileDlg.GetPath()
      wb = Excel.Workbook()
      report = wb.create_worksheet('Integration log time report', columnWidths=[25, 20, 25, 20, 25, 30, 30, 25, 25, 25, 20])
      # sets header cells
      report.add_header('A1')
      report.add_header('B1')
      report.add_header('C1')
      report.add_header('D1')
      report.add_header('E1')
      report.add_header('F1')
      report.add_header('G1')
      report.add_header('H1')
      report.add_header('I1')
      report.add_header('J1')
      report.add_header('K1')
      report.append(['Filename', 'IPEM Time', 'Teamcenter Time', 'User Time', 'Download Time', 'Total Operation Time', 'Total Op w/o User Time', 'Total Save Ops', 'Total Open Ops', 'Total Manage Ops', 'Total Ops'])
      startcount = rowcounter = 1

      for row in xrange(self.mainWindow.displaySummaryListCtrl.GetItemCount()):
         rowcounter += 1
         iteminfo = []
         for col in xrange(self.mainWindow.displaySummaryListCtrl.GetColumnCount()):
            iteminfo.append(self.mainWindow.displaySummaryListCtrl.GetItem(row, col).GetText())
         report.append(iteminfo)

      report.add_table('Table'+str(1), 'A%s:K%s' % (str(startcount), str(rowcounter)), ['Filename', 'IPEM Time', 'Teamcenter Time', 'User Time', 'Download Time', 'Total Operation Time', 'Total Op w/o User Time', 'Total Save Ops', 'Total Open Ops', 'Total Manage Ops', 'Total Ops'])

      try:
         wb.save(reportFile)
         wx.MessageBox('File successfully saved.', 'Success!', wx.ICON_INFORMATION | wx.OK, self.mainWindow)
      except IOError:
         wx.MessageBox('The action cannot be completed because the file is in use.  Close the file and try again.',
                       'File In Use', wx.ICON_ERROR | wx.OK, self.mainWindow)


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