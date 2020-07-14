import json
import DataModel
class DataController:
    def setFile(self):
        with open('C:\\Users\\GoodusData\\Documents\\mygitprj\\dailyCheck\\V2\\Test2.log','r') as f:
            self.rawData = json.load(f)

    def getObjectId(self):
        sourceDBName = self.rawData['DBNAME']
        # monitoring_db 에 연결한다.
        dbConn = DataModel.DataModel('monitoring_db')
        resultSet = dbConn.getOneData('dblist',{'DBNAME' : sourceDBName}, 'Y')
        if resultSet == 0:
            databaseInfo = dict()
            print("New Database Found : ",sourceDBName)
            print("Inserting New Database Information")
            databaseInfo['DBNAME'] = self.rawData['DBNAME']
            databaseInfo['HOSTNAME'] = self.rawData['HOSTNAME']
            databaseInfo['VERSION'] = self.rawData['VERSION']
            databaseInfo['DATABASE_TYPE'] = self.rawData['DATABASE_TYPE']
            databaseInfo['INSTANCE_NUMBER'] = self.rawData['INSTANCE_NUMBER']
            resultSet = dbConn.addData('dblist',databaseInfo)
        else:
            resultSet = dbConn.getOneData('dblist',{'DBNAME' : sourceDBName})
        return resultSet["_id"]

    def addAnalyzeData(self, analyzedData):
        dbConn = DataModel.DataModel('monitoring_db')
        resultSet = dbConn.addData('dailyCheck',analyzedData)

    def analyzeData(self, objectID):
        def pgaAnalyze():
            pgaData = dict()
            pgaData["SGA"]      = self.rawData["MEMORY"]["SGA"]
            pgaData["PGA"]      = self.rawData["MEMORY"]["PGA"]
            pgaData["STATUS"]   = {
                "ALLOCATE" : self.rawData["MEMORY"]["ALLOCATE"],
                "USED"     : self.rawData["MEMORY"]["USED"],
                "FREEABLE" : self.rawData["MEMORY"]["FREEABLE"]
            }

            if "PGALIMIT" in self.rawData["MEMORY"].keys():
                # pga limit 값이 설정되어 있을 경우 - 12c 이상
                # pga_aggregate_limit 에서 allocate 의 사용 비율을 구한다.
                pgaData["PGALIMIT"] = self.rawData["MEMORY"]["PGALIMIT"]
                pgaData["APL"]      = round(float(pgaData["STATUS"]["ALLOCATE"])/float(pgaData["PGALIMIT"])*100,2)
            else:
                # pga_aggreate_target 에서 allocate 의 사용 비율을 구한다.
                pgaData["APT"]      = round(float(pgaData["STATUS"]["ALLOCATE"])/float(pgaData["PGA"])*100,2)

            return pgaData

        def sgaOperAnalyze():
            sgaOperData = dict()
            if self.rawData["SGAOPER"] == "NoData":
                sgaOperData["0"] = self.rawData["SGAOPER"]
            else:
                for compKey in self.rawData["SGAOPER"].keys():
                    sgaOperData[compKey] = self.rawData["SGAOPER"][compKeys]
            return sgaOperData

        def dataguardAnalyze():
            dataguardData = dict()

            if self.rawData["DG"] == "NoData":
                dataguardData["0"] = "NoData"
            else:
                for cntVal in range(0,len(self.rawData["DG"])):
                    dataguardData[str(cntVal)] = self.rawData["DG"][cntVal]

        def asmAnalyze():
            asmData = dict()

            if self.rawData["ASM"] == "NoData":
                self.asmData["0"] = self.rawData["ASM"]
            else:
                for asmCounter in range(0,len(self.rawData["ASM"])):
                    asmData[str(asmCounter)] = {
                        "DGNAME" : self.rawData["ASM"][asmCounter]["NAME"],
                        "TOTAL" : self.rawData["ASM"][asmCounter]["TOTAL"],
                        "USABLE" : self.rawData["ASM"][asmCounter]["USABLE"],
                        "REDUNDANCY" : self.rawData["ASM"][asmCounter]["REDUNDANCY"]
                    }
                    USEDPCT =round((float(asmData[str(asmCounter)]["TOTAL"])-float(asmData[str(asmCounter)]["USABLE"]))/float(asmData[str(asmCounter)]["TOTAL"])*100,2)
                    asmData[str(asmCounter)]["USEDPCT"] = USEDPCT
                    if USEDPCT > 90:
                        warnLevel = 'Critical'
                    elif USEDPCT > 80:
                        warnLevel = 'Warning'
                    else:
                        warnLevel = 'Normal'
                    asmData[str(asmCounter)]["WARN"] = warnLevel

                    return asmData

        def tbsAnalyze():
            tbsData = dict()
            for tbsCounter in range(0,len(self.rawData["TABLESPACE"])):
                tbsData[str(tbsCounter)] = {
                    "NAME"  : self.rawData["TABLESPACE"][tbsCounter]["NAME"],
                    "TOTAL" : self.rawData["TABLESPACE"][tbsCounter]["TOTAL"],
                    "USED"  : self.rawData["TABLESPACE"][tbsCounter]["USED"],
                    "USEDPCT" : round(float(self.rawData["TABLESPACE"][tbsCounter]["USED"])/float(self.rawData["TABLESPACE"][tbsCounter]["TOTAL"])*100,2)
                }
                if tbsData[str(tbsCounter)]["USEDPCT"] > 90:
                    tbsData[str(tbsCounter)]["WARN"] = "Critical"
                elif tbsData[str(tbsCounter)]["USEDPCT"] > 80:
                    tbsData[str(tbsCounter)]["WARN"] = "Warning"
                else:
                    tbsData[str(tbsCounter)]["WARN"] = "Normal"

            return tbsData

        def backupAnalyze():
            backupData = dict()
            if self.rawData["BACKUP"] == "NoData":
                backupData["0"] = "NoData"
            else:
                for backupCounter in range(0,len(self.rawData["BACKUP"])):
                    backupData[str(backupCounter)] = self.rawData["BACKUP"][backupCounter]
            return backupData

        def alertAnalyze():
            alertData = dict()

            if self.rawData["ALERT"] == "NoData":
                alertData["0"] = self.rawData["ALERT"]
            else:
                for alertCounter in range(0,len(self.rawData["ALERT"])):
                    alertData[str(alertCounter)] = self.rawData["ALERT"][alertCounter]
            return alertData

        dailyCheckData = dict()
        dailyCheckData["CHECKDATE"]      = self.rawData["DIAGDATE"]
        dailyCheckData["DBID"]           = objectID
        dailyCheckData["MEMORYSTAT"]     = pgaAnalyze()
        dailyCheckData["SGAOPER"]        = sgaOperAnalyze()
        dailyCheckData["DATAGUARD"]      = dataguardAnalyze()
        dailyCheckData["ASMSTAT"]        = asmAnalyze()
        dailyCheckData["TABLESPACESTAT"] = tbsAnalyze()
        dailyCheckData["ALERT"]          = alertAnalyze()


        return dailyCheckData
