import DataController

# Start Application
App=DataController.DataController()

# Input Logfile
App.setFile()

# get Target Database ObjectID
#  데이터베이스가 신규로 판명되면 목록에 추가하고 오브젝트 아이디를 Return 한다.
#  기존의 데이터베이스일 경우 오브젝트 아이디를 리턴한다.
# 데이터를 정제하고 오브젝트 아이디를 통해 모니터링 데이터를 입력한다.
objectID = App.getObjectId()
analyzedData = App.analyzeData(objectID)
ddd = App.addAnalyzeData(analyzedData)
print(ddd)
