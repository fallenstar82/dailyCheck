sqlplus -S sys/Ehdgoddba!23@pdc_statdb1 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_statdb2 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_lotg1 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_lotg2 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_pyunhap1 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_pyunhap2 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_elsdb1 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_elsdb2 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_bokgwon1 as sysdba @check.sql
sqlplus -S sys/Ehdgoddba!23@pdc_bokgwon2 as sysdba @check.sql

dailyCheck.exe check_LOTG1.log check_LOTG2.log check_elsdb1.log check_elsdb2.log check_PYUNHAP1.log check_PYUNHAP2.log check_STATDB1.log check_STATDB2.log check_BOKGWON1.log check_BOKGWON2.log