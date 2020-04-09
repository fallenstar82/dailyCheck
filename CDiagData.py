import re
class DiagData:
    def __init__(self, fileName):
        self.fileData = open(fileName, mode='r', encoding='utf-8')
        self.diagData = self.fileData.readlines()
        self.sourceData = "".join(self.diagData)
        self.fileData.close()

        self.__getDBName()
        self.__pgaUsage()
        self.__tableSpaceUsage()
        self.__backupStatus()
        self.__alertStatus()
        self.__asmStatus()

    # get DB NAME
    def __getDBName(self):
        startPosition = self.sourceData.find("DBnameStart")
        endPosition = self.sourceData.find("DBnameEnd")
        dbNameSource = self.sourceData[startPosition+12:endPosition-3]
        self.dbName = dbNameSource;

    # pgaUsage
    def __pgaUsage(self):
        self.pgaDataDict = {}
        startPosition = self.sourceData.find("MemoryStart")
        endPosition = self.sourceData.find("MemoryEnd")
        pgaDataSource = self.sourceData[startPosition+12:endPosition-3]
        pgaData = re.split(':|\\n',pgaDataSource)

        # 10 /2 = 5
        for x in range(0,int(len(pgaData)),2):
            self.pgaDataDict[pgaData[x]] = pgaData[x+1]

    # Tablespace
    def __tableSpaceUsage(self):
        self.tableSpaceDict = {}
        startPosition = self.sourceData.find("TablespaceStart")
        endPosition = self.sourceData.find("TablespaceEnd")
        tableSpaceSource = self.sourceData[startPosition+16:endPosition-3]
        tableSpaceData = re.split(':|\\n',tableSpaceSource)

        for x in range(0,int(len(tableSpaceData)),3):
            tablespaceUsed = round(float(tableSpaceData[x+2])/float(tableSpaceData[x+1])*100,2)
            if tablespaceUsed > 90.00:
                tablespaceWarn = 'Critical'
            elif tablespaceUsed > 80.00:
                tablespaceWarn = 'Warning'
            else:
                tablespaceWarn = 'Normal'

            self.tableSpaceDict[tableSpaceData[x]]={
                 "Total" : tableSpaceData[x+1],
                 "Used"  : tableSpaceData[x+2],
                 "PCT"   : tablespaceUsed,
                 "Level" : tablespaceWarn
            }

    def __asmStatus(self):
        self.asmStatusDict = {}
        startPosition = self.sourceData.find("AsmStart")
        endPosition = self.sourceData.find("AsmEnd")
        asmStatusSource = self.sourceData[startPosition+8:endPosition-3]
        
        asmStatusData = re.split(':|\\n',asmStatusSource)
        if len(asmStatusData) > 1:
            for x in range(0,int(len(asmStatusData)),3):
                asmUsed = round(float(asmStatusData[x+2])/float(asmStatusData[x+1])*100,2)
                if asmUsed < 10.00:
                    asmWarn = 'Critical'
                elif asmUsed < 20.00:
                    asmWarn = 'Warning'
                else:
                    asmWarn = 'Normal'

                self.asmStatusDict[asmStatusData[x]] = {
                    "Total" : asmStatusData[x+1],
                    "Usable"  : asmStatusData[x+2],
                    "FPCT"   : asmUsed,
                    "Level" : asmWarn
                }

    # BackupStatus
    def __backupStatus(self):
        self.backupStatusDict = {}
        startPosition = self.sourceData.find("BackupStatusStart")
        endPosition = self.sourceData.find("BackupStatusEnd")
        backupStatusSource = self.sourceData[startPosition+17:endPosition-3]
        backupStatusData = backupStatusSource.split()

        if len(backupStatusData) > 0:
            for x in range(0,int(len(backupStatusData)/3+4),3):
                self.backupStatusDict[backupStatusData[x]] = {
                    "BackupSize" : backupStatusData[x+1],
                        "Status" : backupStatusData[x+2]
                }

    # AlertStatus
    def __alertStatus(self):
        self.alertStatusDict = {}
        startPosition = self.sourceData.find("AlertStart")
        endPosition = self.sourceData.find("AlertEnd")
        alertStatusSource = self.sourceData[startPosition+11:endPosition-3]
        alertStatusData = alertStatusSource.split("\n")

        for x in range(0,len(alertStatusData)):
            sourceData=alertStatusData[x]
            alertDate=sourceData[0:19]
            alertMsg=sourceData[20:]
            self.alertStatusDict[alertDate] = alertMsg

    def getAllData(self):
        self.collectData={}
        self.collectData['DBNAME'] = self.dbName
        self.collectData['MEMORY']  = self.pgaDataDict
        self.collectData['TBSDATA'] = self.tableSpaceDict
        self.collectData['BKDATA']  = self.backupStatusDict
        self.collectData['ALERT']   = self.alertStatusDict
        self.collectData['ASM']     = self.asmStatusDict
        return self.collectData

    def printData(self):
        print(self.pgaDataDict)
        print(self.tableSpaceDict)
        print(self.backupStatusDict)
