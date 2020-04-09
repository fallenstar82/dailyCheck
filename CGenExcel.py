from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl import load_workbook
from datetime import date
import os.path
class GenExcel:
    def __init__(self, sourceData):
        # get Current Year/Month/day
        getToday = date.today()
        dateOfToday = getToday.strftime("%Y%m%d")
        self.fileName = "dailycheck_" + dateOfToday + ".xlsx"
        self.openType = "Unknown"
        if os.path.isfile(self.fileName):
            self.workBook = load_workbook(self.fileName)
            self.openType = "Old"
        else:
            self.workBook = Workbook()
            self.openType = "New"

        # self.workSheet = self.workBook.active
        z = sourceData
        self.__dataCollect(z)
        self.__setNewSheet()
        self.__writeDBName()
        self.__memoryStatic()
        self.__tablespaceStatic()
        self.__asmStatic()
        self.__backupStatic()
        self.__alertStatic()
        self.__closeExcel()

    def __dataCollect(self, dataSet):
        self.dbName = dataSet['DBNAME']
        self.tablespaceData = dataSet['TBSDATA']
        self.memoryData = dataSet['MEMORY']
        self.asmData = dataSet['ASM']
        self.backupData = dataSet['BKDATA']
        self.alertData = dataSet['ALERT']

    def __setNewSheet(self,):
        # 시트 새로 만들기
        self.workSheet = self.workBook.create_sheet(self.dbName)
        self.workBook.active
        self.workSheet.title = self.dbName

        self.workSheet.column_dimensions["B"].width = 4.57
        self.workSheet.column_dimensions["C"].width = 19.15
        self.workSheet.column_dimensions["D"].width = 19.15
        self.workSheet.column_dimensions["E"].width = 19.15
        self.workSheet.column_dimensions["F"].width = 19.15
        self.workSheet.column_dimensions["G"].width = 19.15

    def __writeDBName(self):
        self.rowPosition=3
        # DB 이름
        self.workSheet["B"+str(self.rowPosition)] = self.dbName
        setFont = self.workSheet["B"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=18, bold=True)


    def __memoryStatic(self):
        self.rowPosition = self.rowPosition + 2
        self.workSheet["B"+str(self.rowPosition)] = "MEMORY STATISTICS"
        setFont = self.workSheet["B"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=13, bold=True)

        keyValue = list(self.memoryData.keys())

        for x in range(0,len(self.memoryData)):
            self.rowPosition = self.rowPosition + 1
            self.workSheet["C"+str(self.rowPosition)] = keyValue[x]
            self.workSheet["D"+str(self.rowPosition)] = self.memoryData[keyValue[x]]
            setFont = self.workSheet["C"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11, bold=True)
            setFont = self.workSheet["D"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)

    def __tablespaceStatic(self):
        self.rowPosition = self.rowPosition + 2
        self.workSheet["B"+str(self.rowPosition)] = "TABLESPACE STATISTICS"
        setFont = self.workSheet["B"+str(self.rowPosition)]
        setFont.font = Font(name="Calibri",size=13, bold=True)

        self.rowPosition = self.rowPosition + 1
        self.workSheet["C"+str(self.rowPosition)] = "TABLESPACE NAME"
        self.workSheet["D"+str(self.rowPosition)] = "TOTAL SIZE(GB)"
        self.workSheet["E"+str(self.rowPosition)] = "USED SIZE(GB)"
        self.workSheet["F"+str(self.rowPosition)] = "USED PCT(%)"
        self.workSheet["G"+str(self.rowPosition)] = "WARNING LEVEL"

        setFont = self.workSheet["C"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["D"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["E"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["F"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["G"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)

        keyValue = list(self.tablespaceData.keys())
        for x in range(0,len(self.tablespaceData)):
            self.rowPosition = self.rowPosition + 1
            self.workSheet["C"+str(self.rowPosition)] = keyValue[x]
            self.workSheet["D"+str(self.rowPosition)] = self.tablespaceData[keyValue[x]]["Total"]
            self.workSheet["E"+str(self.rowPosition)] = self.tablespaceData[keyValue[x]]["Used"]
            self.workSheet["F"+str(self.rowPosition)] = self.tablespaceData[keyValue[x]]["PCT"]
            self.workSheet["G"+str(self.rowPosition)] = self.tablespaceData[keyValue[x]]["Level"]

            setFont = self.workSheet["C"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["D"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["E"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["F"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["G"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)



    def __asmStatic(self):
        self.rowPosition = self.rowPosition + 2
        self.workSheet["B"+str(self.rowPosition)] = "ASM STATISTICS"
        setFont = self.workSheet["B"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri', size=13, bold=True)

        self.rowPosition = self.rowPosition + 1
        self.workSheet["C"+str(self.rowPosition)] = "DG NAME"
        self.workSheet["D"+str(self.rowPosition)] = "TOTAL_MB"
        self.workSheet["E"+str(self.rowPosition)] = "USABLE_FILE_MB"
        self.workSheet["F"+str(self.rowPosition)] = "Free PCT"
        self.workSheet["G"+str(self.rowPosition)] = "WARNING LEVEL"

        setFont = self.workSheet["C"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["D"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["E"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["F"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["G"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)

        keyValue = list(self.asmData.keys())
        for x in range(0,len(self.asmData)):
            self.rowPosition = self.rowPosition + 1
            self.workSheet["C"+str(self.rowPosition)] = keyValue[x]
            self.workSheet["D"+str(self.rowPosition)] = self.asmData[keyValue[x]]["Total"]
            self.workSheet["E"+str(self.rowPosition)] = self.asmData[keyValue[x]]["Usable"]
            self.workSheet["F"+str(self.rowPosition)] = self.asmData[keyValue[x]]["FPCT"]
            self.workSheet["G"+str(self.rowPosition)] = self.asmData[keyValue[x]]["Level"]

            setFont = self.workSheet["F"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["D"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["E"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["F"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["G"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)

    def __backupStatic(self):
        self.rowPosition = self.rowPosition + 2
        self.workSheet["B"+str(self.rowPosition)] = "BACKUP STATISTICS"
        setFont = self.workSheet["B"+str(self.rowPosition)]
        setFont.font = Font(size=13, bold=True)

        self.rowPosition = self.rowPosition + 1
        self.workSheet["C"+str(self.rowPosition)] = "START DATE"
        self.workSheet["D"+str(self.rowPosition)] = "BACKUP SIZE"
        self.workSheet["E"+str(self.rowPosition)] = "BACKUP STATUS"
        setFont = self.workSheet["C"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["D"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)
        setFont = self.workSheet["E"+str(self.rowPosition)]
        setFont.font = Font(name='Calibri',size=11, bold=True)

        keyValue = list(self.backupData.keys())
        for x in range(0,len(self.backupData)):
            self.rowPosition = self.rowPosition + 1
            self.workSheet["C"+str(self.rowPosition)] = keyValue[x]
            self.workSheet["D"+str(self.rowPosition)] = self.backupData[keyValue[x]]["BackupSize"]
            self.workSheet["E"+str(self.rowPosition)] = self.backupData[keyValue[x]]["Status"]

            setFont = self.workSheet["C"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["D"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["E"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)

    def __alertStatic(self):
        self.rowPosition = self.rowPosition + 2
        self.workSheet["B"+str(self.rowPosition)] = "ALERTLOG STATISTICS"
        setFont = self.workSheet["B"+str(self.rowPosition)]
        setFont.font = Font(size=13, bold=True)

        self.rowPosition = self.rowPosition + 1
        self.workSheet["C"+str(self.rowPosition)] = "LOG DATE"
        self.workSheet["D"+str(self.rowPosition)] = "LOG MESSAGE"
        setFont = self.workSheet["C"+str(self.rowPosition)]
        setFont.font = Font(size=11, bold=True)
        setFont = self.workSheet["D"+str(self.rowPosition)]
        setFont.font = Font(size=11, bold=True)

        keyValue = list(self.alertData.keys())
        for x in range(0,len(keyValue)):
            self.rowPosition = self.rowPosition + 1
            self.workSheet["C"+str(self.rowPosition)] = keyValue[x]
            self.workSheet["D"+str(self.rowPosition)] = self.alertData[keyValue[x]]

            setFont = self.workSheet["C"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)
            setFont = self.workSheet["D"+str(self.rowPosition)]
            setFont.font = Font(name='Calibri',size=11)

    def __closeExcel(self):
        # 엑셀 닫기
        if self.openType == "New":
             del self.workBook["Sheet"]
        self.workBook.save(self.fileName)
        self.workBook.close()
