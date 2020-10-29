import DBModels.DataModel as DataModel
import datetime


class TrendController:
    def __init__(self):
        self.dbConn = DataModel.DataModel('monitoring_db')

    def _getTragetObjectID(self, dbName, hostName):
        condition = {
            "DBUNQNAME" : dbName,
            "HOSTNAME" : hostName
        }
        resultSet = self.dbConn.getData(
                                        'dblist',
                                        condition,
                                        )
        if resultSet == None:
            print("No match database & host found.")
            print("Check database unique name and host name")
            print("  Check database list using  '-l ALL' option")
            exit()
        else:
            return resultSet['_id']

    def _getTablespaceData(self, objectID):
        startDate = datetime.datetime.now() - datetime.timedelta(days=90)
        tbsData = dict()
        matchedLeft = list()
        matchFlag = False

        # Min 날짜와 Max 날짜 구함.
        condition = {
            "DBID" : objectID,
            "DIAGDATE" : {"$gte" : startDate}
        }

        resultSetStart = self.dbConn.getData(
                                        'dailyCheck',
                                        condition,
                                        { "TABLESPACESTAT" : 1, "DIAGDATE" : 1},
                                        sort=[("DIAGDATE",1)],
                                        mDocs='N'
                                        )

        resultSetEnd = self.dbConn.getData(
                                        'dailyCheck',
                                        condition,
                                        { "TABLESPACESTAT" : 1, "DIAGDATE" : 1},
                                        sort=[("DIAGDATE",-1)],
                                        mDocs='N'
                                        )

        dateIntervalCnt = (resultSetEnd["DIAGDATE"] - resultSetStart["DIAGDATE"]).days

        for dataIndex in resultSetStart["TABLESPACESTAT"].keys():
            tablespaceName = resultSetStart["TABLESPACESTAT"][dataIndex]["NAME"]
            tablespaceUseMin = resultSetStart["TABLESPACESTAT"][dataIndex]["USED"]
            for index in resultSetEnd["TABLESPACESTAT"].keys():
                # Matched
                if resultSetEnd["TABLESPACESTAT"][index]["NAME"] == tablespaceName:
                    tablespaceUseMax = resultSetEnd["TABLESPACESTAT"][index]["USED"]
                    tablespaceTotal = resultSetEnd["TABLESPACESTAT"][index]["TOTAL"]
                    tablespaceTrend = round((resultSetEnd["TABLESPACESTAT"][index]["USED"] - resultSetStart["TABLESPACESTAT"][index]["USED"] )/dateIntervalCnt,2)
                    tablespaceExhaust = round((tablespaceTotal-tablespaceUseMax)/tablespaceTrend,2) if tablespaceTrend > 0 else 0.0
                    # 시작과 끝에 해당 테이블스페이스가 존재하여 서로 매칭될 경우
                    # 매칭 플래그를 트루로 설정하고 매치 리스트에 넣는다.
                    # 끝 리스트에서 해당 테이블스페이스 정보를 삭제한다.
                    matchFlag = True
                    del resultSetEnd["TABLESPACESTAT"][index]
                    break
            # 매칭 플래그가 false 일 경우 삭제된 케이스이므로 넘어가고 매칭되었다면 정보를 업데이트 한다.
            if matchFlag == False:
                continue
            else:
                data = {
                    tablespaceName : {
                        "MIN" : tablespaceUseMin,
                        "MAX" : tablespaceUseMax,
                        "TOTAL" : tablespaceTotal,
                        "TREND" : tablespaceTrend if tablespaceTrend > 0.0 else 0.0,
                        "EXHAUST" : tablespaceExhaust
                    }
                }
                tbsData.update(data)
                matchFlag = False

        # 신규 생성되어 처음엔 없다가 나중에 생성된 케이스
        # 트렌드는 현재 사용량을 날짜수 만큼 나눈 추측값으로 설정
        if len(resultSetEnd["TABLESPACESTAT"]) > 0:
            for newIndex in resultSetEnd["TABLESPACESTAT"].keys():
                data = {
                    resultSetEnd["TABLESPACESTAT"][newIndex]["NAME"] : {
                        "MIN" : 0.0,
                        "MAX" : resultSetEnd["TABLESPACESTAT"][newIndex]["USED"],
                        "TOTAL" : resultSetEnd["TABLESPACESTAT"][newIndex]["TOTAL"],
                        "TREND" : resultSetEnd["TABLESPACESTAT"][newIndex]["USED"]/dateIntervalCnt if resultSetEnd["TABLESPACESTAT"][newIndex]["USED"] > 0 else 0.0,
                        "EXHAUST" : 0.0 if resultSetEnd["TABLESPACESTAT"][newIndex]["USED"] == 0 else round((resultSetEnd["TABLESPACESTAT"][newIndex]["TOTAL"]-resultSetEnd["TABLESPACESTAT"][newIndex]["USED"])/(resultSetEnd["TABLESPACESTAT"][newIndex]["USED"]/dateIntervalCnt),2)
                    }
                }
                tbsData.update(data)

        return(tbsData)


    def getTrend(self, dbName, hostName):
        objectID = self._getTragetObjectID(dbName, hostName)
        tablespaceData = self._getTablespaceData(objectID)
        return(tablespaceData)
