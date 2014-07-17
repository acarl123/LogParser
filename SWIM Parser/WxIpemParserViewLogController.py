'''
Program that parses IPEM and SWIM logs and measures performance characteristics.
Developed by JDH 5/29/14

Fixed for SWIM by AHC 17-Jul-2014
'''

import wx
import WxIpemParserView
import os
import re
import sys
import pprint

_VERSION = "1.0"

def numberFormat(line):
   line = line.split(':')
   desc = line[-1].strip()
   digitList = re.findall('\d+', line[0])
   if digitList:
      line = digitList[0] + "." + digitList[1]
      return line, desc
   else:
      return False, False


def findAverage(inputlist):
   average = sum(inputlist) / float(len(inputlist))
   return '%.4f' % float(average)

# Implementing LogView
class WxIpemParserViewLogController():
   def __init__( self, parent ):
      self.MainWindow = WxIpemParserView.LogView(None)
      self.MainWindow.LogFileListCtrl.Bind( wx.EVT_LIST_KEY_DOWN, self.LogFileListCtrlOnListKeyDown )
      self.MainWindow.btnAddFiles.Bind( wx.EVT_BUTTON, self.logFilePickerOnFileChanged )
      self.MainWindow.calcButton.Bind( wx.EVT_BUTTON, self.calcButtonOnButtonClick)
      self.MainWindow.clearButton.Bind( wx.EVT_BUTTON, self.clearButtonOnButtonClick)

      self.IndexCounter = 0
      self.inputTextFileList = []
      self.headerRow = []
      self.totalProEandSwimTimeList = []
      self.totalTcTimeList = []
      self.totalUserTimeList = []
      self.totalDlTimeList = []
      self.totalOperationTimeList = []
      self.totalOperationTimeWithoutUserTimeList = []
      self.totalNumberOfOperationsList = []
      self.totalSaveOperationList = []
      self.totalOpenOperationList = []
      self.totalManOperationList = []


   def logFilePickerOnFileChanged( self, event ):
      dialog = wx.FileDialog(self.MainWindow, 'Choose a File', "", "", u"log files (*.txt, *.log)|*.txt; *.log|All Files (*.*)|*.*", wx.MULTIPLE)
      if dialog.ShowModal() == wx.ID_OK:
         filelist = dialog.GetPaths()
      else:return

      for file in filelist:
         with open(file, 'r') as f:
            first_line = f.readline()
         parts = first_line.split(':')
         self.MainWindow.SetTitle(parts[-1])
         basePath = os.path.basename(file)
         self.inputTextFileList.append(file)
         self.MainWindow.LogFileListCtrl.InsertStringItem(self.IndexCounter, basePath)

         self.IndexCounter += 1


      # # TODO: Implement saveFolderPickerOnDirChanged
      # fullPath = self.MainWindow.logFilePicker.GetPath()
      # with open(fullPath, 'r') as f:
      #    first_line = f.readline()
      # parts = first_line.split(':')
      # self.MainWindow.SetTitle(parts[-1])
      # basePath = os.path.basename(fullPath)
      # self.inputTextFileList.append(fullPath)
      # self.MainWindow.LogFileListCtrl.InsertStringItem(self.IndexCounter, basePath)
      #
      # self.MainWindow.logFilePicker.SetPath("")
      # self.IndexCounter += 1

   def LogFileListCtrlOnListKeyDown(self, event): # wxGlade: MyFrame1.<event_handler>
     keycode = event.GetKeyCode()
     if keycode == wx.WXK_DELETE:
        if self.MainWindow.LogFileListCtrl.GetFocusedItem() != -1: pass
        item = self.MainWindow.LogFileListCtrl.GetFocusedItem()
        self.MainWindow.LogFileListCtrl.DeleteItem(item)
        del self.inputTextFileList[item]
        self.MainWindow.SetTitle("")


   def clearButtonOnButtonClick( self, event ):
      # TODO: Implement standardButtonSizerOnCancelButtonClick
      self.MainWindow.displaySummaryListCtrl.ClearAll()

   def calcButtonOnButtonClick( self, event ):
      self.MainWindow.displaySummaryListCtrl.ClearAll()

      if self.inputTextFileList:

         rowHeaderDict, resultsDict, avgDict = self.calculateSummaryTimes(self.inputTextFileList)
         rowIndexCounter = 0
         colIndexCounter = 0

         for rowHeader in rowHeaderDict:
            self.MainWindow.displaySummaryListCtrl.InsertColumn(colIndexCounter,rowHeader)
            colIndexCounter += 1
            for colLabel in rowHeaderDict[rowHeader]:
               self.MainWindow.displaySummaryListCtrl.InsertStringItem(sys.maxint,colLabel)


         for logFile in resultsDict:
            colIndex = self.MainWindow.displaySummaryListCtrl.InsertColumn(colIndexCounter,logFile)
            colIndexCounter += 1
            rowIndexCounter = 0
            for results in resultsDict[logFile]:
               self.MainWindow.displaySummaryListCtrl.SetStringItem(rowIndexCounter,colIndex,str(results))
               rowIndexCounter += 1


         if len(resultsDict) > 1:
            for avg in avgDict:
               colIndex = self.MainWindow.displaySummaryListCtrl.InsertColumn(colIndexCounter,avg)
               colIndexCounter += 1
               rowIndexCounter = 0
               for results in avgDict[avg]:
                  self.MainWindow.displaySummaryListCtrl.SetStringItem(rowIndexCounter,colIndex,str(results))
                  rowIndexCounter += 1
         self.MainWindow.displaySummaryListCtrl.SetColumnWidth(0,wx.LIST_AUTOSIZE)
      else:
         pass

   def calculateSummaryTimes(self, listOfFiles):
      openEndKeyWordList = ["perf: open from teamcenter complete","exiting operationcollectiondialog.cancelaction for teamcenter open", "Exiting Operations.cancelCheckOut".lower()]

      saveStartKeyword = "perf: teamcenter -> save as begins"
      saveEndKeyWordList = ["perf: save to teamcenter complete","exiting operationcollectiondialog.cancelaction for teamcenter save", "Save to Teamcenter may have been unsuccessful".lower()]

      manStartKeyword = "perf: manager begins"
      manEndKeyWordList = ["perfsum: manager complete","exiting operationcollectiondialog.cancelaction for teamcenter manager"]


      openStartKeyword = "perf: teamcenter -> open begins"

      userTimeStartKeyword = "pausing perf sum"
      userTimeEndKeyword = ["beginning perf sum","resuming perf sum"]

      tcStartKeywords = "service request"
      tcEndKeywords = "service response"

      downloadStartKeywords = "perf: fcc call starts - downloadfilestolocation"
      downloadEndKeywords = "perf: fcc call ends - downloadfilestolocation"

      CADStartKeyword = 'open command <?xml version'
      CADEndKeyword = 'number of bytes reported by cadscript:'

      # Added the option to account for ProE times if the logs ever support it. You will notice this is only for the manager operation.
      # You would need to do the same for open and save operations. Same format would be followed for adding in integration calculation times

      #proeStartKeywords = "start ProE action"
      #proeEndKeywords = "end ProE action"

      #integrationStartKeywords = "Ipem/SWIM start keywords"
      #integrationEndKeywords = "Ipem/SWIM end keywords"



      #openDict = {'s|e':[{'s':'e'},{'s':'e'},{'s':'e'},{'s':'e'}]}
      #openDict {'openStart|openEnd|complete/cacel':[[('TCstart,TCend,TCdesc1,TCdesc2')],[('ProEstart,ProEend,ProEdesc1,ProEdesc2')],[('UserStart,UserEnd,Userdesc1,Userdesc2')],[('DownloadStart,DownloadEnd,Dowloaddesc1,Downloaddesc2')]]}
      logCounter = 0
      logOperationDict = {}
      swimTimeList = []
      for file_path in listOfFiles:

         #######################OPEN Variables#######################
         tcStartTimesList = []
         tcEndTimesList = []
         tcStarttcDescList = []
         tcEndtcDescList = []

         userStartTimesList = []
         userEndTimesList = []
         userStarttcDescList = []
         userEndtcDescList = []

         downloadStartTimesList = []
         downloadEndTimesList = []
         downloadStarttcDescList = []
         downloadEndtcDescList = []

         openCancelCounter = 0
         openCompleteCounter = 0
         openStartFound = False
         openuserTimeBeginsInitiallyFound = False

         openDict = {}
         #######################OPEN Variables#######################

         #######################SAVE Variables#######################
         savetcStartTimesList = []
         savetcEndTimesList = []
         savetcStarttcDescList = []
         savetcEndtcDescList = []

         saveuserStartTimesList = []
         saveuserEndTimesList = []
         saveuserStarttcDescList = []
         saveuserEndtcDescList = []

         savedownloadStartTimesList = []
         savedownloadEndTimesList = []
         savedownloadStarttcDescList = []
         savedownloadEndtcDescList = []

         saveCancelCounter = 0
         saveCompleteCounter = 0
         saveStartFound = False
         saveuserTimeBeginsInitiallyFound = False
         swimTime = 0

         saveDict = {}
         #######################SAVE Variables#######################


         #######################MAN Variables#######################
         mantcStartTimesList = []
         mantcEndTimesList = []
         mantcStarttcDescList = []
         mantcEndtcDescList = []

         manuserStartTimesList = []
         manuserEndTimesList = []
         manuserStarttcDescList = []
         manuserEndtcDescList = []

         mandownloadStartTimesList = []
         mandownloadEndTimesList = []
         mandownloadStarttcDescList = []
         mandownloadEndtcDescList = []
         '''
         manproeStartTimesList = []
         manproeEndTimesList = []
         manproeStarttcDescList = []
         manproeEndtcDescList = []
         '''

         manCancelCounter = 0
         manCompleteCounter = 0
         manStartFound = False
         manuserTimeBeginsInitiallyFound = False
         manDict = {}

         #######################MAN Variables#######################
         for line in open(file_path, 'r'):
            line = line.lower()


            # if CADEndKeyword in line:
            #    lineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', line)
            #    oldLineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', oldLine)
            #    # swimTime += (float(lineTime[0]) - float(oldLineTime[0]))
            #    # print oldLine, line, swimTime, '\n'
            #
            # # oldLine = line
         ############################MAN####################################
            if manStartKeyword in line:
               manStartTime,desc= numberFormat(line)
               manDict[manStartTime] = []
               manStartFound = True


            if manStartFound == True:
               if CADEndKeyword in line:
                  lineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', line)
                  oldLineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', oldLine)
                  if len(oldLineTime[0]) < 5:
                     oldLineTime = oldLineTime[1]
                  else:
                     oldLineTime = oldLineTime[0]
                  swimTime += (float(lineTime[0]) - float(oldLineTime))

               oldLine = line

               #skip first occurrence of begin. Because that is just the way the log works out.
               if "beginning perf sum" in line and not manuserTimeBeginsInitiallyFound:
                  manuserTimeBeginsInitiallyFound = True
                  continue

               #Check if any downloads took place while doing a manager operation
               if downloadStartKeywords in line:
                  mandownloadStartTime, desc = numberFormat(line)
                  mandownloadStartTimesList.append(mandownloadStartTime)
                  mandownloadStarttcDescList.append(desc)

               if downloadEndKeywords in line:
                  mandownloadEndTime,desc = numberFormat(line)
                  mandownloadEndTimesList.append(mandownloadEndTime)
                  mandownloadEndtcDescList.append(desc)

               #Check if any user time took place while doing a manager operation
               if userTimeStartKeyword in line:
                  manuserStartTime, desc = numberFormat(line)
                  manuserStartTimesList.append(manuserStartTime)
                  manuserStarttcDescList.append(desc)
               '''
               #Check if any ProE time took place while doing a manager operation
               if proeStartKeywords in line:
                  manproeStartTime, desc = numberFormat(line)
                  manproeStartTimesList.append(manproeStartTime)
                  manproeStarttcDescList.append(desc)

               if proeEndKeywords in line:
                  manproeEndTime,desc = numberFormat(line)
                  manproeEndTimesList.append(manproeEndTime)
                  manproeEndtcDescList.append(desc)
               '''


               # There can be multiple end words for user time. must use a loop
               for userEndWord in userTimeEndKeyword:
                  if userEndWord in line:
                     manuserEndTime,desc = numberFormat(line)
                     manuserEndTimesList.append(manuserEndTime)
                     manuserEndtcDescList.append(desc)


               #Check if any TC time took place while doing a manager operation
               if tcStartKeywords in line:
                  mantcStartTime, desc = numberFormat(line)
                  mantcStartTimesList.append(mantcStartTime)
                  mantcStarttcDescList.append(desc)


               if tcEndKeywords in line:
                  mantcEndTime,desc = numberFormat(line)
                  mantcEndTimesList.append(mantcEndTime)
                  mantcEndtcDescList.append(desc)


               #Start building your manDict to have all the times. Because there are multiple end times for manager operation being cancel or complete we must iterat
               for word in manEndKeyWordList:
                  # if we find the end time of a manager operation
                  if word in line:
                     manEndTime,desc = numberFormat(line)
                     #if it was a cancel operation make a cancel key. else make a complete key. key incudes start, end, and operation complete or not
                     if 'cancel' in word:
                        manStartEndTimeKey = manStartTime + "||" + manEndTime + "||" + "canceled"
                        manCancelCounter += 1
                     else:
                        manStartEndTimeKey = manStartTime + "||" + manEndTime + "||" + "completed"
                        manCompleteCounter += 1
                     #create a new key in the manDict that has the end time and operation on it. Then delete the old one. we dont account for operations that havent been compelted
                     manDict[manStartEndTimeKey] = manDict[manStartTime]
                     del manDict[manStartTime]
                     mantcStarttcEndTimeList = zip(mantcStartTimesList,mantcEndTimesList,mantcStarttcDescList,mantcEndtcDescList)
                     manuserStarttcEndTimeList = zip(manuserStartTimesList,manuserEndTimesList,manuserStarttcDescList,manuserEndtcDescList)
                     mandownloadStarttcEndTimeList = zip(mandownloadStartTimesList,mandownloadEndTimesList,mandownloadStarttcDescList,mandownloadEndtcDescList)
                     #manproeStarttcEndTimeList = zip(manproeStartTimesList,manproeEndTimesList,manproeStarttcDescList,manproeEndtcDescList)


                     manDict[manStartEndTimeKey].append(mantcStarttcEndTimeList)
                     manDict[manStartEndTimeKey].append(manuserStarttcEndTimeList)
                     manDict[manStartEndTimeKey].append(mandownloadStarttcEndTimeList)
                     #manDict[manStartEndTimeKey].append(manproeStarttcEndTimeList)


                     mantcStartTimesList = []
                     mantcEndTimesList = []
                     mantcStarttcDescList = []
                     mantcEndtcDescList = []

                     manuserStartTimesList = []
                     manuserEndTimesList = []
                     manuserStarttcDescList = []
                     manuserEndtcDescList = []

                     mandownloadStartTimesList = []
                     mandownloadEndTimesList = []
                     mandownloadStarttcDescList = []
                     mandownloadEndtcDescList = []
                     '''
                     manproeStartTimesList = []
                     manproeEndTimesList = []
                     manproeStarttcDescList = []
                     manproeEndtcDescList = []
                     '''
                     manuserTimeBeginsInitiallyFound = False
                     # reset the start operation boolean so we can find more manager ops
                     manStartFound = False

         ############################MAN####################################

         ############################SAVE####################################
            if saveStartKeyword in line:
               saveStartTime,desc= numberFormat(line)
               saveDict[saveStartTime] = []
               saveStartFound = True


            if saveStartFound == True:
               if CADEndKeyword in line:
                  lineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', line)
                  oldLineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', oldLine)
                  if len(oldLineTime[0]) < 5:
                     oldLineTime = oldLineTime[1]
                  else:
                     oldLineTime = oldLineTime[0]
                  swimTime += (float(lineTime[0]) - float(oldLineTime))

               oldLine = line

               #skip first occuranve of begin
               if "beginning perf sum" in line and not saveuserTimeBeginsInitiallyFound:
                  saveuserTimeBeginsInitiallyFound = True
                  continue

               if downloadStartKeywords in line:
                  savedownloadStartTime, desc = numberFormat(line)
                  savedownloadStartTimesList.append(savedownloadStartTime)
                  savedownloadStarttcDescList.append(desc)

               if downloadEndKeywords in line:
                  savedownloadEndTime,desc = numberFormat(line)
                  savedownloadEndTimesList.append(savedownloadEndTime)
                  savedownloadEndtcDescList.append(desc)


               if userTimeStartKeyword in line:
                  saveuserStartTime, desc = numberFormat(line)
                  saveuserStartTimesList.append(saveuserStartTime)
                  saveuserStarttcDescList.append(desc)



               for userEndWord in userTimeEndKeyword:
                  if userEndWord in line:
                     saveuserEndTime,desc = numberFormat(line)
                     saveuserEndTimesList.append(saveuserEndTime)
                     saveuserEndtcDescList.append(desc)



               if tcStartKeywords in line:
                  savetcStartTime, desc = numberFormat(line)
                  savetcStartTimesList.append(savetcStartTime)
                  savetcStarttcDescList.append(desc)


               if tcEndKeywords in line:
                  savetcEndTime,desc = numberFormat(line)
                  savetcEndTimesList.append(savetcEndTime)
                  savetcEndtcDescList.append(desc)



               for word in saveEndKeyWordList:
                  if word in line:
                     saveEndTime,desc = numberFormat(line)
                     if 'cancel' in word:
                        saveStartEndTimeKey = saveStartTime + "||" + saveEndTime + "||" + "canceled"
                        saveCancelCounter += 1
                     else:
                        saveStartEndTimeKey = saveStartTime + "||" + saveEndTime + "||" + "completed"
                        saveCompleteCounter += 1

                     saveDict[saveStartEndTimeKey] = saveDict[saveStartTime]
                     del saveDict[saveStartTime]
                     savetcStarttcEndTimeList = zip(savetcStartTimesList,savetcEndTimesList,savetcStarttcDescList,savetcEndtcDescList)
                     saveuserStarttcEndTimeList = zip(saveuserStartTimesList,saveuserEndTimesList,saveuserStarttcDescList,saveuserEndtcDescList)
                     savedownloadStarttcEndTimeList = zip(savedownloadStartTimesList,savedownloadEndTimesList,savedownloadStarttcDescList,savedownloadEndtcDescList)


                     saveDict[saveStartEndTimeKey].append(savetcStarttcEndTimeList)
                     saveDict[saveStartEndTimeKey].append(saveuserStarttcEndTimeList)
                     saveDict[saveStartEndTimeKey].append(savedownloadStarttcEndTimeList)


                     savetcStartTimesList = []
                     savetcEndTimesList = []
                     savetcStarttcDescList = []
                     savetcEndtcDescList = []

                     saveuserStartTimesList = []
                     saveuserEndTimesList = []
                     saveuserStarttcDescList = []
                     saveuserEndtcDescList = []

                     savedownloadStartTimesList = []
                     savedownloadEndTimesList = []
                     savedownloadStarttcDescList = []
                     savedownloadEndtcDescList = []

                     saveuserTimeBeginsInitiallyFound = False
                     saveStartFound = False

         ############################SAVE####################################

         ##########################OPEN##########################################
            if openStartKeyword in line:
               openStartTime,desc= numberFormat(line)
               openDict[openStartTime] = []
               openStartFound = True

            if openStartFound == True:

               if CADEndKeyword in line:
                  lineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', line)
                  oldLineTime = re.findall(r'[-+]?[0-9]*\.?[0-9]+', oldLine)
                  if len(oldLineTime[0]) < 5:
                     oldLineTime = oldLineTime[1]
                  else:
                     oldLineTime = oldLineTime[0]
                  swimTime += (float(lineTime[0]) - float(oldLineTime))

               oldLine = line


               if downloadStartKeywords in line:
                  downloadStartTime, desc = numberFormat(line)
                  downloadStartTimesList.append(downloadStartTime)
                  downloadStarttcDescList.append(desc)

               if "beginning perf sum" in line and not openuserTimeBeginsInitiallyFound:
                  openuserTimeBeginsInitiallyFound = True
                  continue


               if downloadEndKeywords in line:
                  downloadEndTime,desc = numberFormat(line)
                  downloadEndTimesList.append(downloadEndTime)
                  downloadEndtcDescList.append(desc)


               if userTimeStartKeyword in line:
                  userStartTime, desc = numberFormat(line)
                  if userStartTime:
                     userStartTimesList.append(userStartTime)
                     userStarttcDescList.append(desc)


               for userEndWord in userTimeEndKeyword:
                  if userEndWord in line:
                     userEndTime,desc = numberFormat(line)
                     userEndTimesList.append(userEndTime)
                     userEndtcDescList.append(desc)



               if tcStartKeywords in line:
                  tcStartTime, desc = numberFormat(line)
                  tcStartTimesList.append(tcStartTime)
                  tcStarttcDescList.append(desc)


               if tcEndKeywords in line:
                  tcEndTime,desc = numberFormat(line)
                  tcEndTimesList.append(tcEndTime)
                  tcEndtcDescList.append(desc)

               for word in openEndKeyWordList:
                  if word in line:
                     openEndTime,desc = numberFormat(line)
                     if 'cancel' in word:
                        openStartEndTimeKey = openStartTime + "||" + openEndTime + "||" + "canceled"
                        openCancelCounter += 1
                     else:
                        openStartEndTimeKey = openStartTime + "||" + openEndTime + "||" + "completed"
                        openCompleteCounter += 1

                     openDict[openStartEndTimeKey] = openDict[openStartTime]
                     del openDict[openStartTime]
                     tcStarttcEndTimeList = zip(tcStartTimesList,tcEndTimesList,tcStarttcDescList,tcEndtcDescList)
                     userStarttcEndTimeList = zip(userStartTimesList,userEndTimesList,userStarttcDescList,userEndtcDescList)
                     downloadStarttcEndTimeList = zip(downloadStartTimesList,downloadEndTimesList,downloadStarttcDescList,downloadEndtcDescList)


                     openDict[openStartEndTimeKey].append(tcStarttcEndTimeList)
                     openDict[openStartEndTimeKey].append(userStarttcEndTimeList)
                     openDict[openStartEndTimeKey].append(downloadStarttcEndTimeList)

                     tcStartTimesList =[]
                     tcEndTimesList = []
                     tcStarttcDescList = []
                     tcEndtcDescList = []

                     userStartTimesList =[]
                     userEndTimesList = []
                     userStarttcDescList = []
                     userEndtcDescList = []

                     downloadStartTimesList =[]
                     downloadEndTimesList = []
                     downloadStarttcDescList = []
                     downloadEndtcDescList = []

                     openuserTimeBeginsInitiallyFound = False
                     openStartFound = False
         swimTimeList.append(swimTime)

         ##########################OPEN##########################################
         logOperationDictKey = "log_" + str(logCounter)
         logOperationDict[logOperationDictKey] = [openDict,saveDict,manDict]
         logCounter += 1


      totalTcTimeList = []
      totalDlTimeList = []
      totalUserTimeList = []
      totalOperationTimeList = []
      totalOperationTimeWithoutUserTimeList = []
      totalProEandSwimTimeList = []
      totalOpenOperationList = []
      totalSaveOperationList = []
      totalManOperationList = []
      totalNumberOfOperationsList = []

      for logOperationDictKey in logOperationDict:
         openDict = logOperationDict[logOperationDictKey][0]
         saveDict = logOperationDict[logOperationDictKey][1]
         manDict = logOperationDict[logOperationDictKey][2]

         ##########################OPEN DETAILS##########################################
         opentcElapsedTimeList = []
         opentcStartTimeList = []
         opentcEndTimeList = []
         opentcDescList = []
         openuserElapsedTimeList = []
         openuserStartTimeList = []
         openuserEndTimeList = []
         openuserDescList = []
         opendownloadElapsedTimeList =[]
         opendownloadStartTimeList =[]
         opendownloadEndTimeList = []
         opendownloadDescList = []

         savetcElapsedTimeList = []
         savetcStartTimeList = []
         savetcEndTimeList = []
         savetcDescList = []
         saveuserElapsedTimeList = []
         saveuserStartTimeList = []
         saveuserEndTimeList = []
         saveuserDescList = []
         savedownloadElapsedTimeList =[]
         savedownloadStartTimeList =[]
         savedownloadEndTimeList = []
         savedownloadDescList = []

         mantcElapsedTimeList = []
         mantcStartTimeList = []
         mantcEndTimeList = []
         mantcDescList = []
         manuserElapsedTimeList = []
         manuserStartTimeList = []
         manuserEndTimeList = []
         manuserDescList = []
         mandownloadElapsedTimeList =[]
         mandownloadStartTimeList =[]
         mandownloadEndTimeList = []
         mandownloadDescList = []

         totalOpenTcTime = 0
         totalManTcTime = 0
         totalSaveTcTime = 0

         totalOpenDlTime = 0
         totalManDlTime = 0
         totalSaveDlTime = 0

         totalOpenUserTime = 0
         totalManUserTime = 0
         totalSaveUserTime = 0

         elapsedOpenTimeTotal = 0
         elapsedmanTimeTotal = 0
         elapsedsaveTimeTotal = 0

         elapsedOpenTimeList = []
         elapsedmanTimeList = []
         elapsedsaveTimeList = []

         openOpCounter = 0
         manOpCounter = 0
         saveOpCounter = 0

         if openDict:
            openOpCounter += 1
            for openKey in openDict:
               operationLists = openDict[openKey]

               openTimeList = openKey.split('||')
               if len(openTimeList) >= 2:
                  openStartTime = openTimeList[0]
                  openEndtTime = openTimeList[1]
                  elapsedOpenTime = float(openEndtTime) - float(openStartTime)
                  elapsedOpenTimeTotal = elapsedOpenTime + elapsedOpenTimeTotal
                  elapsedOpenTimeList.append(elapsedOpenTimeTotal)

               # if len(operationLists) >=2:
               tcTimeList = operationLists[0]
               userTimeList = operationLists[1]
               dlTimeList = operationLists[2]

               for dlDescTuple in dlTimeList:
                  startTime = float(dlDescTuple[0])
                  endTime = float(dlDescTuple[1])
                  startDesc = dlDescTuple[2]
                  endDesc = dlDescTuple[3]
                  elapsedTime = endTime - startTime

                  opendownloadElapsedTimeList.append(elapsedTime)
                  opendownloadStartTimeList.append(str(startTime))
                  opendownloadEndTimeList.append(str(endTime))
                  opendownloadDescList.append(str(startDesc))


               for timeDescTuple in tcTimeList:
                  startTime = float(timeDescTuple[0])
                  endTime = float(timeDescTuple[1])
                  startDesc = timeDescTuple[2]
                  endDesc = timeDescTuple[3]
                  elapsedTime = endTime - startTime

                  opentcElapsedTimeList.append(elapsedTime)
                  opentcStartTimeList.append(str(startTime))
                  opentcEndTimeList.append(str(endTime))
                  opentcDescList.append(str(startDesc))


               for timeDescTuple in userTimeList:
                  startTime = float(timeDescTuple[0])
                  endTime = float(timeDescTuple[1])
                  startDesc = timeDescTuple[2]
                  endDesc = timeDescTuple[3]
                  elapsedTime = endTime - startTime


                  openuserElapsedTimeList.append(elapsedTime)
                  openuserStartTimeList.append(str(startTime))
                  openuserEndTimeList.append(str(endTime))
                  openuserDescList.append(str(startDesc))


         if saveDict:
            saveOpCounter += 1
            for saveKey in saveDict:
               operationLists = saveDict[saveKey]
               tcTimeList = operationLists[0]
               userTimeList = operationLists[1]
               dlTimeList = operationLists[2]

               saveTimeList = saveKey.split('||')
               saveStartTime = saveTimeList[0]
               saveEndtTime = saveTimeList[1]
               elapsedsaveTime = float(saveEndtTime) - float(saveStartTime)
               elapsedsaveTimeTotal = elapsedsaveTime + elapsedsaveTimeTotal
               elapsedsaveTimeList.append(elapsedsaveTimeTotal)

               for dlDescTuple in dlTimeList:
                  startTime = float(dlDescTuple[0])
                  endTime = float(dlDescTuple[1])
                  startDesc = dlDescTuple[2]
                  endDesc = dlDescTuple[3]
                  elapsedTime = endTime - startTime


                  savedownloadElapsedTimeList.append(elapsedTime)
                  savedownloadStartTimeList.append(str(startTime))
                  savedownloadEndTimeList.append(str(endTime))
                  savedownloadDescList.append(str(startDesc))


               for timeDescTuple in tcTimeList:
                  startTime = float(timeDescTuple[0])
                  endTime = float(timeDescTuple[1])
                  startDesc = timeDescTuple[2]
                  endDesc = timeDescTuple[3]
                  elapsedTime = endTime - startTime


                  savetcElapsedTimeList.append(elapsedTime)
                  savetcStartTimeList.append(str(startTime))
                  savetcEndTimeList.append(str(endTime))
                  savetcDescList.append(str(startDesc))


               for timeDescTuple in userTimeList:
                  startTime = float(timeDescTuple[0])
                  endTime = float(timeDescTuple[1])
                  startDesc = timeDescTuple[2]
                  endDesc = timeDescTuple[3]
                  elapsedTime = endTime - startTime


                  saveuserElapsedTimeList.append(elapsedTime)
                  saveuserStartTimeList.append(str(startTime))
                  saveuserEndTimeList.append(str(endTime))
                  saveuserDescList.append(str(startDesc))

         if manDict:
            manOpCounter += 1
            for manKey in manDict:
               if manDict[manKey] == []: continue
               operationLists = manDict[manKey]
               tcTimeList = operationLists[0]
               userTimeList = operationLists[1]
               dlTimeList = operationLists[2]
               #proeTimeList = operationLists[3]

               manTimeList = manKey.split('||')
               manStartTime = manTimeList[0]
               manEndtTime = manTimeList[1]
               elapsedmanTime = float(manEndtTime) - float(manStartTime)
               elapsedmanTimeTotal = elapsedmanTime + elapsedmanTimeTotal
               elapsedmanTimeList.append(elapsedmanTimeTotal)

               for dlDescTuple in dlTimeList:
                  startTime = float(dlDescTuple[0])
                  endTime = float(dlDescTuple[1])
                  startDesc = dlDescTuple[2]
                  endDesc = dlDescTuple[3]
                  elapsedTime = endTime - startTime

                  mandownloadElapsedTimeList.append(elapsedTime)
                  mandownloadStartTimeList.append(str(startTime))
                  mandownloadEndTimeList.append(str(endTime))
                  mandownloadDescList.append(str(startDesc))


               for timeDescTuple in tcTimeList:
                  startTime = float(timeDescTuple[0])
                  endTime = float(timeDescTuple[1])
                  startDesc = timeDescTuple[2]
                  endDesc = timeDescTuple[3]
                  elapsedTime = endTime - startTime


                  mantcElapsedTimeList.append(elapsedTime)
                  mantcStartTimeList.append(str(startTime))
                  mantcEndTimeList.append(str(endTime))
                  mantcDescList.append(str(startDesc))


               for timeDescTuple in userTimeList:
                  startTime = float(timeDescTuple[0])
                  endTime = float(timeDescTuple[1])
                  startDesc = timeDescTuple[2]
                  endDesc = timeDescTuple[3]
                  elapsedTime = endTime - startTime

                  manuserElapsedTimeList.append(elapsedTime)
                  manuserStartTimeList.append(str(startTime))
                  manuserEndTimeList.append(str(endTime))
                  manuserDescList.append(str(startDesc))

         # if 'swimTime' in locals(): print "Total SWIM time: %ss" % swimTime


         for number in opentcElapsedTimeList:
            totalOpenTcTime  = totalOpenTcTime + number
         for number in savetcElapsedTimeList:
            totalSaveTcTime  = totalSaveTcTime + number
         for number in mantcElapsedTimeList:
            totalManTcTime  = totalManTcTime + number

         for number in savedownloadElapsedTimeList:
            totalSaveDlTime  = totalSaveDlTime + number
         for number in opendownloadElapsedTimeList:
            totalOpenDlTime  = totalOpenDlTime + number
         for number in mandownloadElapsedTimeList:
            totalManDlTime  = totalManDlTime + number


         for number in openuserElapsedTimeList:
            totalOpenUserTime  = totalOpenUserTime + number
         for number in saveuserElapsedTimeList:
            totalSaveUserTime  = totalSaveUserTime + number
         for number in manuserElapsedTimeList:
            totalManUserTime  = totalManUserTime + number


         totalTcTime = totalOpenTcTime + totalSaveTcTime + totalManTcTime
         totalDlTime = totalManDlTime + totalOpenDlTime + totalSaveDlTime
         totalUserTime = totalManUserTime + totalSaveUserTime + totalOpenUserTime
         totalOperationTime = swimTime + totalDlTime + totalTcTime + totalUserTime
         totalOperationTimeWithoutUserTime = swimTime + totalTcTime + totalDlTime#totalOperationTime - totalUserTime
         totalProEandSwimTime = totalOperationTime - totalUserTime - totalDlTime - totalTcTime
         totalNumberOfOperations = openOpCounter + saveOpCounter + manOpCounter

         totalTcTimeList.append(totalTcTime)
         totalDlTimeList.append(totalDlTime)
         totalUserTimeList.append(totalUserTime)
         totalOperationTimeList.append(totalOperationTime)
         totalOperationTimeWithoutUserTimeList.append(totalOperationTimeWithoutUserTime)
         totalProEandSwimTimeList = swimTimeList#.append(swimTime)#totalProEandSwimTime)

         totalOpenOperationList.append(openOpCounter)
         totalSaveOperationList.append(saveOpCounter)
         totalManOperationList.append(manOpCounter)
         totalNumberOfOperationsList.append(totalNumberOfOperations)



      ##########################OPEN DETAILS##########################################
      summaryColumnHeader = ("SWIM Time","Teamcenter Time","User Time","Download Time","Total Operation Time","Total Operation w/o User",'Total Save','Total Open','Total Manager',"Total Operations")
      summaryResultsDict = {}
      summaryRowLabelDict = {}
      summaryAvgColDict = {}
      summaryRowLabelDict[''] = summaryColumnHeader

      if len(listOfFiles) > 1:
         totalAverageTimeTuple = (str(findAverage(totalProEandSwimTimeList)),str(findAverage(totalTcTimeList)),str(findAverage(totalUserTimeList)),str(findAverage(totalDlTimeList)),str(findAverage(totalOperationTimeList)),str(findAverage(totalOperationTimeWithoutUserTimeList)))
         summaryAvgColDict["Average"] = totalAverageTimeTuple

      totalProEandSwimTimeList = [ '%.4f' % float(elem) for elem in totalProEandSwimTimeList ]
      totalTcTimeList = [ '%.4f' % float(elem) for elem in totalTcTimeList ]
      totalUserTimeList = [ '%.4f' % float(elem) for elem in totalUserTimeList ]
      totalDlTimeList = [ '%.4f' % float(elem) for elem in totalDlTimeList ]
      totalOperationTimeList = [ '%.4f' % float(elem) for elem in totalOperationTimeList ]
      totalOperationTimeWithoutUserTimeList = [ '%.4f' % float(elem) for elem in totalOperationTimeWithoutUserTimeList ]

      listOfLogFileSummaryResults = zip(totalProEandSwimTimeList,totalTcTimeList,totalUserTimeList,totalDlTimeList,totalOperationTimeList,totalOperationTimeWithoutUserTimeList,totalSaveOperationList,totalOpenOperationList,totalManOperationList,totalNumberOfOperationsList)

      counter = 0
      for log in listOfFiles:
         summaryResultsDict[os.path.basename(log)] = listOfLogFileSummaryResults[counter]
         counter += 1
      return summaryRowLabelDict,summaryResultsDict,summaryAvgColDict



   def show(self):
      self.MainWindow.Show()