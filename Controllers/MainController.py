import Controllers.DataController as DC
import Controllers.TrendController as TC
class MainController():
    def __init__(self):
        self.App = DC.DataController()

    def addDiagData(self, fileName):
        self.App=DC.DataController()
        self.App.setFile(fileName)
        # get Target Database ObjectID
        # 신규 DB 인지 기존 DB 인지 확인
        objectId = self.App.getObjectId()
        if objectId is not None:
              objectId = objectId["_id"]
        else:
              objectId = self.App.addDatabaseInfo()
        analyzedData = self.App.doAnalyze(objectId)
        result = self.App.addAnalyzeData(analyzedData)

    def genExcel(self, dbUniqName, hostname):
        self.App.writeExcel(self.App.getDiagData(dbUniqName, hostname))

    def getDbList(self, dbName={}):
        resultSet = self.App.getDbList(dbName)
        return resultSet

    def makeDbList(self, data):
        return self.App.makeDbList(data)

    def textReportTablesapceUsage(self, data):
        dbList = self.makeDbList(self.getDbList())
        reportData = self.App.textReport(dbList, 'TS')
        print("%-25s"%"DATABASE NAME","%10s"%"USED","%10s"%"TOTAL","%10s"%"USEDPCT")
        print("----------------------------------------------------------")
        for x in reportData.keys():
            print("%-25s"%x,"%10s"%reportData[x]["USEDGB"],"%10s"%reportData[x]["TOTAL"],"%10s"%reportData[x]["USEDPCT"])

    def trendView(self, dbName, hostName):
        App = TC.TrendController()
        trendInfo = App.getTrend(dbName, hostName)
        print(
            "%-25s"%"TABELSPACE NAME",
            "%13s"%"TOTAL",
            "%13s"%"BEGIN SIZE",
            "%13s"%"END SIZE",
            "%13s"%"TREND",
            "%13s"%"EXHAUST"
            )
        print("-----------------------------------------------------------------------------------------------")
        for data in trendInfo.keys():
            if trendInfo[data]["EXHAUST"] > 0.0:
                print("%-25s"%data,
                      "%13s"%trendInfo[data]["TOTAL"],
                      "%13s"%trendInfo[data]["MIN"],
                      "%13s"%trendInfo[data]["MAX"],
                      "%13s"%trendInfo[data]["TREND"],
                      "%13s"%trendInfo[data]["EXHAUST"]
                      )
            else:
                continue
