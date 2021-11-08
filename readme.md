# ORACLE DAILYCHECK SCIRIPT  V 2.0

## Version History

### Up to 0.3

0.1.0 - 최초 개발
0.2.0 - ASM 및 BACKUP 없을시 Index Range Error 수정
0.2.1 - SGA Operation 추가
0.3.0 - 로그에 대하여 Json 방식으로 변경함.
0.3.1 - Dataguard 부문 추가.

### Up to 2

#### 2.0.0

* RAC 통합.
* MongoDB를 이용한 데이터 저장
* Alert log 관련 문제 해결



## Dependancy

* openpyxl
* Mongodb

### Files

#### No Compiled

##### Controllers

- DataController.py
- ExcelController.py
- excel_header_define.py

##### DBModels

* DataModel.py

##### Main

* dbCheck.sql
* checkdb.py
* readme.md
* HelpMessage.py

#### Compiled

* dailyCheck.exe


## Usage Note
### OPTIONS
| option | description |
|--------|-------------|
| -a     | Add logfiles to Database. example : <br> checkdb -a db1.log db2.log ..|
| -e     | Generat Excel files. options are <i><b> all</b></i> or <i> db_name </i> example : <br> checkdb -e all <i>or</i> checkdb -e db_name.. |
| -l     | Show database List. <i><b> all</b></i> or <i>db_name</i>|
