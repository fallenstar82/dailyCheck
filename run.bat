sqlplus -S sys/Ehdgoddba!23@pdc_statdb1 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_statdb2 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_lotg1 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_lotg2 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_pyunhap1 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_pyunhap2 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_elsdb1 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_elsdb2 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_bokgwon1 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@pdc_bokgwon2 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@bdc_lotg1 as sysdba @dayCheck.sql
sqlplus -S sys/Ehdgoddba!23@bdc_lotg2 as sysdba @dayCheck.sql

dailyCheck.exe CHECK_ppolgamedb01_LOTG1_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_ppolgamedb02_LOTG2_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_ppelissdb01_PYUNHAP1_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_ppelissdb02_PYUNHAP2_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_ppelselldb01_elsdb1_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_ppelselldb02_elsdb2_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_ppmnstatdb01_STATDB1_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_ppmnstatdb02_STATDB2_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_pppldb01_BOKGWON1_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_pppldb02_BOKGWON2_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_pbolgamedb01_LOTG1_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log CHECK_pbolgamedb02_LOTG2_%DATE:~0,4%_%DATE:~5,2%_%DATE:~8,2%.log
