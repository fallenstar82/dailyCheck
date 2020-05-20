set serveroutput on
set feedback off
set timing off
set heading off
set trimspool on
set serveroutput on unlimitedw
set lines 250
column inst_name new_value inst_name_val
select instance_name inst_name from v$instance;
spool check_&inst_name_val..log
prompt # DBnameStart
prompt &inst_name_val
prompt # DBnameEnd
prompt # MemoryStart
declare
 oracleVersion BINARY_INTEGER;
 totalSGA number(10,2);
 totalPGA number(10,2);
 limitPGA number(10,2);
 allocPGA number(10,2);
 freePGA number(10,2);
 targetPGA number(10,2);
 useRate number(5,2);
 resultPGA varchar2(25);
begin
 select to_number(substr(version,1,2)) into oracleVersion from v$instance;
 select value/1024/1024 into targetPGA from v$parameter where name = 'pga_aggregate_target';
 -- Version : Higher then 12
 if oracleVersion >= 12 then
  select value/1024/1024 into limitPGA from v$parameter where name = 'pga_aggregate_limit';
 end if;
 select sum(pga_used_mem)/1024/1024,
        sum(pga_alloc_mem)/1024/1024,
        sum(pga_freeable_mem)/1024/1024
        into totalPGA, allocPGA, freePGA
   from v$process;
 select sum(value)/1024/1024 into totalSGA from v$sga;
 dbms_output.put_line('SGA:'||totalSGA||' MB');
 dbms_output.put_line('PGA:'||targetPGA||' MB');
 if oracleVersion >= 12 then
  dbms_output.put_line('PGALimit:'||limitPGA||' MB');
 end if;
 dbms_output.put_line('Used/Alloc:'||totalPGA||' / '||allocPGA||' MB');
 dbms_output.put_line('Freeable:'||freePGA||' MB');
 if oracleVersion >=12 then
  useRate := round(allocPGA/limitPGA * 100,2);
  if useRate <= 50 then
    resultPGA := 'Normal';
  elsif useRate <= 80 then
    resultPGA := 'Warning';
  else
    resultPGA := 'Critical';
  end if;
  dbms_output.put_line('Alloc/Lim:'||useRate||'% - '||resultPGA);
 else
  useRate := round(allocPGA/targetPGA * 100,2);
  if useRate <= 50 then
    resultPGA := 'Normal';
  elsif useRate <= 80 then
    resultPGA := 'Warning';
  else
    resultPGA := 'Critical';
  end if;
  dbms_output.put_line('Alloc/Aggr:'||useRate||'%'||resultPGA);
 end if;
end;
/
prompt # MemoryEnd
prompt # TablespaceStart
declare
begin
for tbschk in (select tablespace_name, tgb total_gb, tgb-fgb used_gb, fgb free_gb, round((tgb-fgb)/tgb*100,2) used_pct
                 from (select df.tablespace_name, round(df.gb,2) as tgb, round(fs.gb,2) as fgb
                         from (select tablespace_name, sum(bytes)/1024/1024 as gb
                                 from dba_data_files  df
                               group by tablespace_name) df,
                      (select tablespace_name, sum(bytes)/1024/1024 as gb
                         from dba_free_space  fs
                       group by tablespace_name) fs
              where df.tablespace_name = fs.tablespace_name)
    ) loop
dbms_output.put_line(
  tbschk.tablespace_name||':'||
  tbschk.total_gb||':'||
  tbschk.used_gb);
end loop;
end;
/
prompt # TablespaceEnd
prompt # SgaOperStart
declare
begin
 for sgaopdata in (select rownum||'|'||datalist as rawdt
                     from (select component||'|'||
                                  to_char(start_time,'YYYY/MM/DD HH24:MI:SS')||'|'||
                                  to_char(end_time,'YYYY/MM/DD HH24:MI:SS')||'|'||
                                  oper_type||'|'||
                                  oper_mode||'|'||
                                  initial_size/1024/1024||'|'||
                                  target_size/1024/1024||'|'||
                                  final_size/1024/1024||'|'||
                                  status datalist
                             from v$sga_resize_ops
                            where oper_mode is not null
                              and start_time >= trunc(sysdate)-1
                           order by component, start_time)
                   ) loop
   dbms_output.put_line(sgaopdata.rawdt);
 end loop;
end;
/
prompt # SgaOperEnd
prompt # AsmStart
declare
 isAsmUse BINARY_INTEGER;
begin
 select count(*) into isAsmUse from v$asm_diskgroup;
 if isAsmUse = 0 then
  null;
 else
  for asmuse in ( select name,total_mb,usable_file_mb from v$asm_diskgroup) loop
   dbms_output.put_line(asmuse.name||':'||asmuse.total_mb||':'||asmuse.usable_file_mb);
  end loop;
 end if;
end;
/
prompt # AsmEnd
prompt # BackupStatusStart
declare
 isRmanBackup BINARY_INTEGER;
begin
 select count(*) into isRmanBackup from v$rman_backup_job_details;
 if isRmanBackup = 0 then
  null;
 else
  for rb in (
              select TO_CHAR(START_TIME,'yyyy/mm/dd-hh24:mi:ss') start_time,
                     OUTPUT_BYTES_DISPLAY dub,
                     STATUS
              from V$RMAN_BACKUP_JOB_DETAILS
              where start_time >= trunc(sysdate-2)
              order by 1 desc ) loop
  dbms_output.put_line(
                rb.start_time||' '||
                rb.dub||' '||
                rb.status);
  end loop;
 end if;
end;
/
prompt # BackupStatusEnd
prompt # AlertStart
declare
 isAlertExists BINARY_INTEGER;
begin
 select count(*) into isAlertExists from v$diag_alert_ext where originating_timestamp between trunc(sysdate-1) and sysdate;
 if isAlertExists = 0 then
  null;
 else
  for al in (select to_char(originating_timestamp,'YYYY/MM/DD-HH24:MI:SS') dt,
                    replace(replace(message_text,chr(10),''),chr(13),'') message_text
               from v$diag_alert_ext
              where message_text like '%ORA-%'
                and originating_timestamp between trunc(sysdate-1) and sysdate
              ) loop
  dbms_output.put_line(
                al.dt||' '||
                al.message_text
                );
  end loop;
 end if;
end;
/
prompt # AlertEnd
spool off
exit
