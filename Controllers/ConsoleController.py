import json
import Controllers.DataController as DC
import operator
from bson.objectid import ObjectId

class ConsoleController():
    def __init__(self):
        self.dc = DC.DataController()

    def drawTop(self, termWidth, selectedMenu, dbName):
        spacing=termWidth-(len(selectedMenu)+len(dbName))
        print(selectedMenu, end='')
        for x in range(0,spacing):
            print(' ', end='')
        print(dbName)
        for x in range(0,termWidth):
            print('=', end='')
        print('\n')


    def selectMenu(self, maxNumber):
        inputValue = int(input("Choose : "))
        if inputValue < 1 or inputValue > maxNumber:
            return 0
        else:
            return inputValue

    # Menu View
    def getMenu(self, categoryName):
        from Modules.Utilities import clearScreen
        while True:
            currentPage=__import__('Controllers.console_menu_tree',globals(),locals(),[categoryName],0)
            menuList=getattr(currentPage,categoryName)
            keySet=dict()
            menuSeq = 1
            for menuKeys in menuList:
                print(
                    "%5s"%" ",
                    "%3s"%menuSeq,
                    menuList[menuKeys]
                )
                keySet[menuSeq]=menuKeys
                menuSeq = menuSeq + 1
            try:
                selectedMenu = self.selectMenu(menuSeq)
                if selectedMenu == 0:
                    pass
                else:
                    return keySet[selectedMenu]                 
            except Exception as e:
                pass

    def runAction(self, selectedAction):
        print("We will run : " + selectedAction)
        quit()
            

    def showDBList(self, data):
        for index in range(0,len(data)):
             print(
                  '%3s'%index,
                  '%-14s'%data[index]['DBUNQNAME'],
                  '%-12s'%data[index]['VERSION'],
                  '%-14s'%data[index]['INSTANCE_NAME'],
                  '%-12s'%data[index]['HOSTNAME'])
        
    def setDatabaseList(self):
        dbList = []
        resultSet = self.dc.getDbList({})
        if resultSet == None:
            return dbList
        else:
            # list = 1
            for dbName in resultSet:
                dbList.append(dbName)
                # list = list + 1
        return dbList
    
    def showMenuList(self):
        print("0  Tablespace Trend")
