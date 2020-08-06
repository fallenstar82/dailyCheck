import json
import DBModels.DataModel as DataModel
import operator
from bson.objectid import ObjectId
class DataController:
    def setFile(self, fileName):
        with open(fileName,'r') as f:
            self.rawData = json.load(f)

    def getObjectId(self, dbUniqName):
        dbConn = DataModel.DataModel('monitoring_db')
        resultSet=dbConn.getData('dblist', { "DBUNQNAME" : dbUniqName }, countYN='N', mDocs='N')
        return resultSet

    def getDiagData(self, dbUniqName):
        import datetime
        today = datetime.datetime(
            datetime.date.today().year,
            datetime.date.today().month,
            datetime.date.today().day
        )
        # 임시로 날짜 특정. 이후에 삭제. 위 커멘트는 해제
        diagData = dict()
        nodeInfoSource = dict()

        dbConn = DataModel.DataModel('monitoring_db')
        dbInfo = dbConn.getData(
            'dblist',
            { "DBUNQNAME" : dbUniqName},
            countYN='N',
            mDocs='N'
        )
        # DB 기본정보
        diagData["DATABASE_INFO"] = {
            "DBNAME" : dbInfo["DBNAME"],
            "DBUNQNAME" : dbInfo["DBUNQNAME"],
            "DATABASE_TYPE" : dbInfo["DATABASE_TYPE"],
            "VERSION" : dbInfo["VERSION"]

        }
        # RAC 일 경우 연관된 노드들의 정보 가져와.
        # 첫 노드의 정보를 넣는다.
        nodeInfoSource[dbInfo["INSTANCE_NUMBER"]] = dbInfo
        # 다른 노드의 정보를 넣는다.
        if dbInfo["DATABASE_TYPE"]=='RAC':
            for otherNodeInfo in dbInfo["CLUSTER_NODES"]:
                nodeInfo = dbConn.getData('dblist', {"_id" : otherNodeInfo}, countYN='N', mDocs='N')
                if nodeInfo is not None:
                    nodeInfoSource[nodeInfo["INSTANCE_NUMBER"]] = nodeInfo

        # 노드 정보를 리턴할 데이터에 합치자. 싱글도 예외 없다.
        diagData["INSTANCE_INFO"] = {}
        infoKeys=list(nodeInfoSource.keys())
        infoKeys.sort()
        for instanceInfo in infoKeys:
            diagData["INSTANCE_INFO"][instanceInfo] = {
                "INSTANCE_NUMBER" : nodeInfoSource[instanceInfo]["INSTANCE_NUMBER"],
                "INSTANCE_NAME"   : nodeInfoSource[instanceInfo]["INSTANCE_NAME"],
                "HOSTNAME"        : nodeInfoSource[instanceInfo]["HOSTNAME"]
            }

        # 진단 데이터 가져오자!
        diagRawData = dict()
        infoKeys=list(diagData["INSTANCE_INFO"].keys())
        infoKeys.sort()
        for index in infoKeys:
            resultSet = dbConn.getData(
                                 'dailyCheck',
                                 {"DBID" : nodeInfoSource[index]["_id"], "DIAGDATE" : today }
                       )
            if resultSet is not None:
                diagRawData[index] = resultSet

        # 각 부분별로 진단데이터의 공통부분, 개별부분 넣는다.
        diagData["MEMORYSTAT"] = {}
        diagData["SGAOPER"] = {}
        diagData["DATAGUARD"] = {}
        diagData["ALERT"] = {}
        diagData["TABLESPACE"] = {}
        diagData["ASMSTAT"] = {}

        # 공통부분 (테이블스페이스, ASM)
        # diagData["TABLESPACE"] = diagRawData[instIdx]["TABLESPACESTAT"]
        for instIdx in diagRawData.keys():
            if 'ASMSTAT' in diagRawData[instIdx]:
                for asmNum in diagRawData[instIdx]["ASMSTAT"]:
                    diagData["ASMSTAT"][diagRawData[instIdx]["ASMSTAT"][asmNum]["DGNAME"]] = {
                        "DGNAME" : diagRawData[instIdx]["ASMSTAT"][asmNum]["DGNAME"],
                        "TOTAL" : diagRawData[instIdx]["ASMSTAT"][asmNum]["TOTAL"],
                        "USABLE" : diagRawData[instIdx]["ASMSTAT"][asmNum]["USABLE"],
                        "REDUNDANCY" : diagRawData[instIdx]["ASMSTAT"][asmNum]["REDUNDANCY"],
                        "USEDPCT" : diagRawData[instIdx]["ASMSTAT"][asmNum]["USEDPCT"],
                        "WARN" : diagRawData[instIdx]["ASMSTAT"][asmNum]["WARN"],
                    }
            for tsNum in diagRawData[instIdx]["TABLESPACESTAT"].keys():
                diagData["TABLESPACE"][diagRawData[instIdx]["TABLESPACESTAT"][tsNum]["NAME"]] = {
                    "NAME" : diagRawData[instIdx]["TABLESPACESTAT"][tsNum]["NAME"],
                    "TOTAL" : diagRawData[instIdx]["TABLESPACESTAT"][tsNum]["TOTAL"],
                    "USED" : diagRawData[instIdx]["TABLESPACESTAT"][tsNum]["USED"],
                    "USEDPCT" : diagRawData[instIdx]["TABLESPACESTAT"][tsNum]["USEDPCT"],
                    "WARN" : diagRawData[instIdx]["TABLESPACESTAT"][tsNum]["WARN"]
                }
            break
        # 개별부분
        # MEMORY, SGAOP, DG, ALERT

        for instIdx in diagRawData.keys():
            diagData["MEMORYSTAT"][instIdx] = {
                "INSTANCE_NUMBER" : instIdx
            }
            diagData["MEMORYSTAT"][instIdx].update(diagRawData[instIdx]["MEMORYSTAT"])
            ## SGA Operation. SGA Operation 이 없을 경우 값을 빼버린다.
            if '0' in diagRawData[instIdx]["SGAOPER"]:
                pass
            else:
                diagData["SGAOPER"][instIdx] = diagRawData[instIdx]["SGAOPER"]

            ## Dataguard Gap Check. DG 구성이 아니면 암것도 안 넣는다.
            if diagRawData[instIdx]["DATAGUARD"]['0'] == "NoData":
                pass
            else:
                diagData["DATAGUARD"][instIdx] = {}
                for index in diagRawData[instIdx]["DATAGUARD"].keys():
                    print(diagRawData[instIdx]["DATAGUARD"])
                    diagData["DATAGUARD"][instIdx][index] = {
                        "INSTANCE_NUMBER" : diagRawData[instIdx]["DATAGUARD"][index]["INST_ID"],
                        "DBUNIQNAME" : diagRawData[instIdx]["DATAGUARD"][index]["DBUNIQNAME"],
                        "PARENTDB" : diagRawData[instIdx]["DATAGUARD"][index]["PARENTDB"],
                        "ROLE" : diagRawData[instIdx]["DATAGUARD"][index]["ROLE"],
                        "SCN" : diagRawData[instIdx]["DATAGUARD"][index]["SCN"]
                    }
                    if 'DELAY' in diagRawData[instIdx]["DATAGUARD"][index]:
                        diagData["DATAGUARD"][instIdx][index]["DELAY"] = diagRawData[instIdx]["DATAGUARD"][index]["DELAY"]

            if '0' in diagRawData[instIdx]["ALERT"]:
                pass
            else:
                diagData["ALERT"][instIdx] = diagRawData[instIdx]["ALERT"]
        return diagData

    def getDbList(self, dbName={}):
        dbConn = DataModel.DataModel('monitoring_db')
        return dbConn.getData('dblist',dbName, returnColumn = {'DBUNQNAME':True, '_id':False,'VERSION':True}, mDocs='Y')

    def writeExcel(self, dataSource):
        import Controllers.ExcelController as EC
        Exc = EC.ExcelController(dataSource)
        Exc.writeTitle()        # 타이틀 정보를 그린다.
        Exc.writeDbInfo()       # 기본 정보를 그린다.
        Exc.writeInstanceInfo() # Instance 정보를 그린다.
        Exc.writeMemoryDiag()   # 메모리 점검 정보를 그린다.
        Exc.writeSgaOperDiag()
        Exc.writeDataGuardDiag()
        if dataSource["DATABASE_INFO"]["DATABASE_TYPE"] == "RAC":
            Exc.writeAsmDiag()
        Exc.writeTablespaceDiag()
        Exc.writeAlertDiag()
        Exc.closeExcel()

    def addDatabaseInfo(self):
        sourceDBInfo = self.rawData['DBINFO']
        del sourceDBInfo['OTHER_NODE_INFO']
        # RAC 일 경우 기존 노드가 있는지 확인한다.
        if sourceDBInfo["DATABASE_TYPE"] == 'RAC':
            sourceDBInfo["CLUSTER_NODES"] = []
            for nodeinfo in otherDBInfo:
                relatedNodeList = dbConn.getData('dblist',nodeinfo,"_id")
                if relatedNodeList is not None:
                    sourceDBInfo["CLUSTER_NODES"].append(relatedNodeList["_id"])
            resultSet = dbConn.addData('dblist',sourceDBInfo)
            # 기존 노드가 있다면 기존 노드에 신규 노드의 _id 를 추가한다.
            for oldOne in sourceDBInfo["CLUSTER_NODES"]:
                searchCondition = {"_id" : oldOne}
                updateValue = { "CLUSTER_NODES" : resultSet.inserted_id }
                oldDbUpdate = dbConn.updateData('dblist',searchCondition, updateValue,'PUSH')
        else:
            resultSet = dbConn.addData('dblist',sourceDBInfo)
        return resultSet.inserted_id

    def getObjectId(self):
        sourceDBInfo = self.rawData['DBINFO']
        if 'OTHER_NODE_INF' in self.rawData:
            otherDBInfo = sourceDBInfo['OTHER_NODE_INFO']
            del sourceDBInfo['OTHER_NODE_INFO']
        # monitoring_db 에 연결한다.
        dbConn = DataModel.DataModel('monitoring_db')
        # 기존에 등록된 데이터베이스인지 확인한다.
        resultSet = dbConn.getData(
            'dblist',
            sourceDBInfo,
            countYN='Y'
        )
        if resultSet == 0:
            # RAC DB 라면 기존에 다른 노드가 등록되어 있는지 확인한다.
            # 있다면, 해당 DB 들을 _id 로 서로 연결한다.
            if sourceDBInfo["DATABASE_TYPE"] == 'RAC':
                sourceDBInfo["CLUSTER_NODES"] = []
                for nodeinfo in otherDBInfo:
                    relatedNodeList = dbConn.getData('dblist',nodeinfo,"_id")
                    if relatedNodeList is not None:
                        sourceDBInfo["CLUSTER_NODES"].append(relatedNodeList["_id"])
                resultSet = dbConn.addData('dblist',sourceDBInfo)
                #기존 데이터베이스에도 신규 노드의 정보를 업데이트 한다.
                for oldOne in sourceDBInfo["CLUSTER_NODES"]:
                    searchCondition = {"_id" : oldOne}
                    updateValue = { "CLUSTER_NODES" : resultSet.inserted_id }
                    oldDbUpdate = dbConn.updateData('dblist',searchCondition, updateValue,'PUSH')
                    return resultSet.inserted_id
            else:
                # RAC DB가 아닐경우 그냥 추가
                resultSet = dbConn.addData('dblist', sourceDBInfo)
                return resultSet.inserted_id
        else:
            resultSet = dbConn.getData('dblist', sourceDBInfo)
            return resultSet["_id"]

    def addAnalyzeData(self, analyzedData):
        checkCondition = dict()
        dateSource = dict()
        dbConn = DataModel.DataModel('monitoring_db')
        checkCondition = {
            "DBID"      : analyzedData["DBID"],
            "DIAGDATE" : analyzedData["DIAGDATE"]
        }
        resultSet = dbConn.replaceData('dailyCheck',checkCondition, analyzedData, True)
        return resultSet

    def doAnalyze(self, objectID):
        def diagDate():
            import datetime
            diagDate = datetime.datetime(
                int(self.rawData["DIAGDATE"].split('_')[0]),
                int(self.rawData["DIAGDATE"].split('_')[1]),
                int(self.rawData["DIAGDATE"].split('_')[2])
            )
            return diagDate

        def pgaAnalyze():
            pgaData = dict()
            pgaData["SGA"]      = self.rawData["MEMORY"]["SGA"]
            pgaData["PGA"]      = self.rawData["MEMORY"]["PGA"]
            pgaData["ALLOCATE"] = self.rawData["MEMORY"]["ALLOCATE"]
            pgaData["USED"] = self.rawData["MEMORY"]["USED"]
            pgaData["FREEABLE"] = self.rawData["MEMORY"]["FREEABLE"]

            if "PGALIMIT" in self.rawData["MEMORY"].keys():
                # pga limit 값이 설정되어 있을 경우 - 12c 이상
                # pga_aggregate_limit 에서 allocate 의 사용 비율을 구한다.
                pgaData["PGALIMIT"] = self.rawData["MEMORY"]["PGALIMIT"]
                pgaData["USEDPCT"]  = round(float(pgaData["ALLOCATE"])/float(pgaData["PGALIMIT"])*100,2)
            else:
                # pga_aggreate_target 에서 allocate 의 사용 비율을 구한다.
                pgaData["USEDPCT"]  = round(float(pgaData["ALLOCATE"])/float(pgaData["PGA"])*100,2)

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
                import datetime
                primaryScnDate = dict()
                for cntVal in range(0,len(self.rawData["DG"])):
                    dataguardData[str(cntVal)] = self.rawData["DG"][cntVal]
                    # 날짜를 Python 의 형식에 맞게 datetime 형으로 변경한다.
                    timeSplit = dict()
                    timeSplit["DATE"] = dataguardData[str(cntVal)]["SCN"].split(' ')[0]
                    timeSplit["TIME"] = dataguardData[str(cntVal)]["SCN"].split(' ')[1]
                    scnToDate = datetime.datetime(
                        int(timeSplit["DATE"].split('/')[0]),
                        int(timeSplit["DATE"].split('/')[1]),
                        int(timeSplit["DATE"].split('/')[2]),
                        int(timeSplit["TIME"].split(':')[0]),
                        int(timeSplit["TIME"].split(':')[1]),
                        int(timeSplit["TIME"].split(':')[2]),
                    )
                    dataguardData[str(cntVal)]["SCN"] = scnToDate
                    if "PRIMARY" in dataguardData[str(cntVal)]["ROLE"]:
                        # Primary 일 경우, 현재 SCN 을 저장한다.
                        # Primary - Standby - Standby 가 될 수 있나?
                        # 어쨌든 그래서, Primary 의 Uniqu 이름과 SCN 을 저장한다.
                        primaryScnDate[dataguardData[str(cntVal)]["DBUNIQNAME"]] = dataguardData[str(cntVal)]["SCN"]
                    else:
                        dataguardData[str(cntVal)]["DELAY"] = str(
                            primaryScnDate[dataguardData[str(cntVal)]["PARENTDB"]] - scnToDate
                        )
            return dataguardData

        def asmAnalyze():
            asmData = dict()

            if self.rawData["ASM"] == "NoData":
                self.asmData["0"] = self.rawData["ASM"]
            else:
                for asmCounter in range(0,len(self.rawData["ASM"])):
                    asmData[str(asmCounter)] = {
                        "GROUP_NUMBER" : self.rawData["ASM"][asmCounter]["GROUP_NUMBER"],
                        "DGNAME"     : self.rawData["ASM"][asmCounter]["NAME"],
                        "TOTAL"      : self.rawData["ASM"][asmCounter]["TOTAL"],
                        "USABLE"     : self.rawData["ASM"][asmCounter]["USABLE"],
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
        dailyCheckData["DIAGDATE"]       = diagDate()
        dailyCheckData["DBID"]           = objectID
        dailyCheckData["MEMORYSTAT"]     = pgaAnalyze()
        dailyCheckData["SGAOPER"]        = sgaOperAnalyze()
        dailyCheckData["DATAGUARD"]      = dataguardAnalyze()
        if self.rawData["DBINFO"]["DATABASE_TYPE"] == "RAC":
            dailyCheckData["ASMSTAT"]        = asmAnalyze()
        dailyCheckData["TABLESPACESTAT"] = tbsAnalyze()
        dailyCheckData["ALERT"]          = alertAnalyze()

        return dailyCheckData
