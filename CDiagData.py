import json

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
        self.__dataguardStatus()

    # get DB NAME
    def __getDBName(self):
        self.dbName = self.rawData["DBNAME"]

    # pgaUsage
    def __pgaUsage(self):
        self.pgaDataDict = dict()

        # 메모리 점검에 대한 키값을 가져온다.
        memoryComponentsKeys = self.rawData["MEMORY"].keys()

        # 각 키값에 대한 값을 딕셔너리에 저장한다.
        for keys in memoryComponentsKeys:
            self.pgaDataDict[keys] = self.rawData["MEMORY"][keys]

    # SGA 동적변화 점검
    def __sgaOperation(self):
        self.sgaOperDataDict = dict()

        if self.rawData["SGAOPER"] == "NoData":
            self.sgaOperDataDict[0] = "NoOper"
        else:
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

        if self.rawData["ASM"] == "NoData":
            self.asmStatusDict[0] = "NoASM"
        else:
            for cntVal in range(0,len(self.rawData["ASM"])):
                self.asmStatusDict[cntVal] = self.rawData["ASM"][cntVal]

                # ASM 사용율 집계
                asmUse  = float(self.asmStatusDict[cntVal]["TOTAL"])-float(self.asmStatusDict[cntVal]["USABLE"])
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
        self.backupStatusDict = dict()

        if self.rawData["BACKUP"] == "NoData":
            self.backupStatusDict[0] = "NoBackup"
        else:
            for cntVal in range(0,len(self.rawData["BACKUP"])):
                self.backupStatusDict[cntVal] = self.rawData["BACKUP"][cntVal]

    def __dataguardStatus(self):
        self.dataguardStatusDict = dict()

        if self.rawData["DG"] == "NoData":
            self.dataguardStatusDict[0] = "NoData"
        else:
            for cntVal in range(0,len(self.rawData["DG"])):
                self.dataguardStatusDict[cntVal] = self.rawData["DG"][cntVal]

    # AlertStatus
    def __alertStatus(self):
        self.alertStatusDict = dict()

        if self.rawData["ALERT"] == "NoData":
            self.alertStatusDict[0] = self.rawData["ALERT"]
        else:
            for cntVal in range(0,len(self.rawData["ALERT"])):
                self.alertStatusDict[cntVal] = self.rawData["ALERT"][cntVal]

    def getAllData(self):
        self.collectData = dict()
        self.collectData['DBNAME'] = self.dbName
        self.collectData['MEMORY']  = self.pgaDataDict
        self.collectData['TBSDATA'] = self.tableSpaceDict
        self.collectData['BKDATA']  = self.backupStatusDict
        self.collectData['ALERT']   = self.alertStatusDict
        self.collectData['ASM']     = self.asmStatusDict
        self.collectData['SGAOP']   = self.sgaOperDataDict
        self.collectData['DG']      = self.dataguardStatusDict
        return self.collectData

    def printData(self):
        print(self.collectData)
