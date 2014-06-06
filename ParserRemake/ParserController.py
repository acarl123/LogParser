from ParserView import LogView
import wx
import os, sys, re


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
      self.mainWindow.logFilePicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.onFile)
      self.mainWindow.calcButton.Bind(wx.EVT_BUTTON, self.onCalc)
      self.dirPaths = []

      # Setup view

   def show(self, *args):
      self.mainWindow.Show()

   def onFile(self, event):
      logFilePath = self.mainWindow.logFilePicker.GetPath()
      self.dirPaths.append(os.path.dirname(logFilePath))

      self.mainWindow.LogFileListCtrl.InsertStringItem(self.mainWindow.LogFileListCtrl.GetItemCount(), str(os.path.basename(logFilePath)))

   def onCalc(self, event):
      for fileIndex in xrange(self.mainWindow.LogFileListCtrl.GetItemCount()):
         logFileName = os.path.join(self.dirPaths[fileIndex], self.mainWindow.LogFileListCtrl.GetItemText(fileIndex))

         with open(logFileName, 'r') as log:
            read_data = log.readlines()

         self.calcTimes(read_data)

   def calcTimes(self, data):


      openStartTimeList = []
      openEndTimeList = []

      for line in data:

         numberInLine = re.findall(r'[-+]?[0-9]*\.?[0-9]+', line)

         # Open Time
         if openStartKeyword in line.lower():
            print line
            # openStartTimeList.append(numberInLine[0])
         elif any(key in line.lower() for key in openEndKeyWordList):
            print 'end %s' % line
            # openEndTimeList.append(numberInLine[0])

         # User Time
         elif userTimeStartKeyword in line.lower():
            pass
         elif any(key in line.lower() for key in userTimeEndKeyword):
            pass

      if openStartTimeList and openEndTimeList:
         if len(openEndTimeList) == len(openStartTimeList):
            del openEndTimeList[0]
            del openStartTimeList[0]

            for itemIndex in xrange(len(openEndTimeList)):
               self.totalOpenTime += float(openEndTimeList[itemIndex]) - float(openStartTimeList[itemIndex])
         else:
            pass # Do stuff to make the lists the same size

      self.populateList()

   def populateList(self, items = []):
      print self.totalOpenTime