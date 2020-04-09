from CDiagData import DiagData
from CGenExcel import GenExcel
import sys

# Daily Check Script.
# Version 0.1
#   Read logs, and generate Excel
#   Not support RAC
#   RAC will support on Version 0.2

if len(sys.argv) <= 1:
    print ("How to Usage : ")
    print ("    filename.py log1 log2 log3 .. logN")
else:
    for x in range(1,len(sys.argv)):
        a = DiagData(sys.argv[x])
        x = a.getAllData()
        print(x)
        z = GenExcel(x)
    # z.closeExcel()

# a = DiagData("C:\\Users\\GoodusData\\Documents\\Study\\daily\\sample.log")
# x = a.getAllData()
# print(x)
# z = GenExcel(x)
