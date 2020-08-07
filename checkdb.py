import Controllers.MainController as MC
import sys
import argparse
if __name__ == "__main__":
    parser_main = argparse.ArgumentParser(description = 'Daily Database Diag Program', prog='checkdb')
    group_main = parser_main.add_mutually_exclusive_group()
    group_main.add_argument('-l', help='Show Database List', metavar='<dbUniqueName> or All')
    group_main.add_argument('-a', nargs='*', help='add Diaglog file.', metavar='logfilename')
    group_main.add_argument('-e', help='make Excel file. Output filename will be \'DailyCheck_<date>.xlsx\'.', metavar='dbunqname or all')
    # group_main.add_argument('-r', help='Report Diag Stats',choices=['ts','pga'])
    args=parser_main.parse_args()

if args.a :
    App = MC.MainController()
    if args.a[0].find('*') != -1:
        import pathlib
        import os
        import pprint
        p_temp = pathlib.Path(os.getcwd())
        fnames = list(p_temp.glob(args.a[0]))
    else:
        fnames = args.a
    for x in fnames:
        print('logfile processing : ',x)
        App.addDiagData(x)

if args.e :
    if args.e.upper() == 'ALL':
        param = {}
    else:
        param = { 'DBUNQNAME' : args.e }
    App = MC.MainController()
    resultSet = App.getDbList(param)
    if resultSet == None:
        print("No Database found")
    else:
        # DB NAME - HOSTNAME 및 RAC 로 리스트 정리.
        orderedDbList = App.makeDbList(resultSet)
        for index in orderedDbList.keys():
            print("Generating : DBUNQNAME - ","%-14s"%orderedDbList[index]['DBUNQNAME'],"%-12s"%orderedDbList[index]['HOSTNAME'])
            App.genExcel(orderedDbList[index]['DBUNQNAME'], orderedDbList[index]['HOSTNAME'])

if args.l :
    if args.l.upper() == 'ALL':
        param = {}
    else:
        param = { 'DBUNQNAME' : args.l.upper() }
    App = MC.MainController()
    resultSet = App.getDbList(param)
    print("DATABASE LIST")
    print("=====================")
    print("%-14s"%"DB UNIQUE NAME","%-12s"%"VERSION","%-14s"%"INSTANCE_NAME","%-12s"%"HOSTNAME")
    print("-------------- ------------ -------------- ------------")
    if resultSet == None:
        print("No Database found")
    else:
        for dbName in resultSet:
            print('%-14s'%dbName['DBUNQNAME'],
                  '%-12s'%dbName['VERSION'],
                  '%-14s'%dbName['INSTANCE_NAME'],
                  '%-12s'%dbName['HOSTNAME'])
#
# if args.r :
#     print("argument is : ",args.r)
#     if args.r == 'ts':
#         App = MC.MainController()
#         resultSet = App.reportTablesapceUsage(args.r)
