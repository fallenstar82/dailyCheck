import json
import sys #for Develop
class DiagData:
    def __init__(self, fileName):
        with open(fileName,'r') as f:
            self.rawData = json.load(f)

    def testData(self):
        self.tableSpaceDict = dict()

        print(len(self.rawData["TABLESPACE"]))
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

        print(self.tableSpaceDict)

    def getData(self):
        self.sgaOperDataDict = dict()

        sgaOperationComponentsKeys = self.rawData["SGAOPER"].keys()
        # print(self.rawData["SGAOPER"]["DEFAULT buffer cache"][0])
        # print(len(self.rawData["SGAOPER"]["DEFAULT buffer cache"][0]))
        # print(self.rawData["SGAOPER"]["DEFAULT buffer cache"])
        # quit()
        for compKeys in sgaOperationComponentsKeys:
            self.sgaOperDataDict[compKeys]=self.rawData["SGAOPER"][compKeys]

        # print(self.sgaOperDataDict)
        print(self.sgaOperDataDict["java pool"][0]["OPERATION"])
        print(self.sgaOperDataDict["java pool"][1]["OPERTYPE"])

a = DiagData(sys.argv[1])
data = a.testData()


# print(json_data["SGAOPER"].keys())
# print(len(json_data["SGAOPER"]["DEFAULT buffer cache"]))
