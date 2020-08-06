import Controllers.DataController as DC
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
              pass
        else:
              objectId = self.App.addDatabaseInfo()
        analyzedData = self.App.doAnalyze(objectId)
        result = self.App.addAnalyzeData(analyzedData)

    def genExcel(self, dbname):
        self.App.writeExcel(self.App.getDiagData(dbname))

    def getDbList(self, dbName={}):
        dbList = list()
        temp   = list()
        resultSet = self.App.getDbList(dbName)
        for rs in resultSet:
            if rs['DBUNQNAME'] in temp:
                pass
            else:
                dbList.append(rs)
                temp.append(rs['DBUNQNAME'])
        return dbList
