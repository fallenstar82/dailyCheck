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

    def genExcel(self, dbUniqName, hostname):
        self.App.writeExcel(self.App.getDiagData(dbUniqName, hostname))

    def getDbList(self, dbName={}):
        resultSet = self.App.getDbList(dbName)
        return resultSet

    def makeDbList(self, data):
        return self.App.makeDbList(data)
