import re
class DiagData:
    def __init__(self, fileName):
        with open(fileName,'r') as f:
            self.rawData = json.load(f)

        self.__getDBName()
        self.__pgaUsage()
        self.__tableSpaceUsage()
        self.__backupStatus()
        self.__alertStatus()
        self.__asmStatus()
        self.__sgaOperation()

    # get DB NAME
    def __getDBName(self):
        self.dbName = self.rawData["DBNAME"]

    # pgaUsage
    def __pgaUsage(self):
        self.pgaDataDict = dict()

        # 메모리 점검에 대한 키값을 가져온다.
        memoryComponentsKeys = self.rawData["MEMORY"].keys()

        # 각 키값에 대한 값을 딕셔너리에 저장한다.
        for keys in range(0,len(memoryComponentsKeys)):
            self.pgaDataDict[keys] = self.rawData["MEMORY"][keys]

    # SGA 동적변화 점검
    def __sgaOperation(self):
        self.sgaOperDataDict = dict()

        sgaOperationComponentsKeys = self.rawData["SGAOPER"].keys()
        for compKeys in sgaOperationComponentsKeys:
            self.sgaOperDataDict[compKeys]=self.rawData["SGAOPER"][compKeys]

    # Tablespace
    def __tableSpaceUsage(self):
        self.tableSpaceDict = dict()

        for cntVal in range(0,len(self.rawData["TABLESPACE"])):
            self.tableSpaceDict[cntVal] = self.rawData["TABLESPACE"][cntVal]
            tablespaceUsed = round(float(self.tableSpaceDict[cntVal]["USED"])/float(self.tableSpaceDict[cntVal]["TOTAL"])*100,2)
            if tablespaceUsed > 90.00:
                tablespaceWarn = 'Critical'
            elif tablespaceUsed > 80.00:
                tablespaceWarn = 'Warning'
            else:
                tablespaceWarn = 'Normal'
            self.tableSpaceDict[cntVal]["PCT"] = tablespaceUsed
            self.tableSpaceDict[cntVal]["LEVEL"] = tablespaceWarn

    def __asmStatus(self):
        self.asmStatusDict = dict()

        for cntVal in range(0,len(self.rawData["ASM"])):
            self.asmStatusDict[cntVal] = self.rawData["ASM"][cntVal]

            # ASM 사용율 집계
            asmUse  = float(self.asmStatusDict[cntVal]["TOTAL"])-float(self.asmStautsDict[cntVal]["USABLE"])
            asmUsed = round(asmUse/float(self.asmStatusDict[cntVal]["TOTAL"])*100,2)
            if asmUsed > 90.00:
                asmWarn = 'Critical'
            elif asmUsed > 80.00:
                asmWarn = 'Warning'
            else:
                asmWarn = 'Normal'

            # 사용량 및 사용율, 경고레벨 추가
            self.asmStatusDict[cntVal]["USE"] = asmUse
            self.asmStatusDict[cntVal]["PCT"] = asmUsed
            self.asmStatusDict[cntVal]["LEVEL"] = asmWarn

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
        self.collectData['SGAOP']   = self.sgaOperDataDict
        return self.collectData

    def printData(self):
        print(self.pgaDataDict)
        print(self.tableSpaceDict)
        print(self.backupStatusDict)
