import Controllers.MainController as MC
import sys
import argparse
# if len(sys.argv) <= 1:
#     print("HelpMsg")
#     quit()

if len(sys.argv) < 2:
    print ("-h to Help")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Daily Database Diag Program')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', help='Show Database List', metavar='<dbUniqueName> or All')
    group.add_argument('-a', nargs='*', help='add Diaglog file.', metavar='logfilename')
    group.add_argument('-e', help='make Excel file. Output filename will be \'DailyCheck_<date>.xlsx\'.', metavar='dbunqname or all')
    parser.add_argument('-v', help='verbose', action='store_true')
    args=parser.parse_args()

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
        print(x)
        App.addDiagData(x)

if args.e :
    if args.e.upper() == 'ALL':
        param = {}
    else:
        param = { 'DBUNQNAME' : args.e.upper() }
    App = MC.MainController()
    resultSet = App.getDbList(param)

    if len(resultSet) == 0:
        print("No Database found")
    else:
        for dbName in resultSet:
            print("Generating : ", dbName['DBUNQNAME'])
            App.genExcel(dbName['DBUNQNAME'])

if args.l :
    if args.l.upper() == 'ALL':
        param = {}
    else:
        param = { 'DBUNQNAME' : args.l.upper() }
    App = MC.MainController()
    resultSet = App.getDbList(param)
    print("DATABASE LIST")
    print("=====================")
    print("DB UNIQUE NAME              VERSION")
    print("--------------------------- --------------------")
    if len(resultSet) == 0:
        print("No Database found")
    else:
        for dbName in resultSet:
            print('%-19s'%dbName['DBUNQNAME'],'%20s'%dbName['VERSION'])



# Option " -add"

# Start Application
# Imsi -a 이면 분석
# if sys.argv[1] == '-a':








# App = DC.DataController()
# App.getDiagData('BOKGWON')
#
# # EXCEL
# App = DC.DataController()
# App.writeExcel(App.getDiagData('BOKGWON'))
