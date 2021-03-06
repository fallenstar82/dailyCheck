SET SERVEROUTPUT ON SIZE UNLIMITED
SET FEEDBACK OFF
SET TRIMSPOOL ON
SET TIMING OFF
SET HEADING OFF
SET LINES 300
COLUMN INST_NAME NEW_VALUE INST_NAME_VAL
COLUMN TODAY NEW_VALUE TODAY_VAL
COLUMN HOST_NAME NEW_VALUE HOST_NAME_VAL
SELECT INSTANCE_NAME INST_NAME, HOST_NAME HOST_NAME FROM V$INSTANCE;
SELECT TO_CHAR(SYSDATE,'YYYY_MM_DD') TODAY FROM DUAL;
SPOOL CHECK_&HOST_NAME_VAL._&INST_NAME_VAL._&TODAY_VAL..log
BEGIN
  DECLARE
    V_CHECK_DATE               VARCHAR2(10);
    V_RAC_INFO                 VARCHAR2(1);
    V_INSTANCE_NUMBER          BINARY_INTEGER;
    V_ONI_COUNT                BINARY_INTEGER;
    V_ONI_COUNTER              BINARY_INTEGER;
    CURSOR C_DBINFO IS
    SELECT INSTANCE_NAME,
           HOST_NAME,
           VERSION||EDITION AS VERSION,
           DATABASE_TYPE,
           INSTANCE_NUMBER,
           NAME,
           DB_UNIQUE_NAME,
           STARTUP_TIME
      FROM V$INSTANCE, V$DATABASE;
  BEGIN
    -- TODAY 출력
    SELECT TO_CHAR(SYSDATE,'YYYY_MM_DD') INTO V_CHECK_DATE FROM DUAL;
    -- START JSON AND CHECKDATE
    DBMS_OUTPUT.PUT_LINE('{');
    DBMS_OUTPUT.PUT_LINE('"DIAGDATE" : "'||V_CHECK_DATE||'",');
    DBMS_OUTPUT.PUT_LINE('"DIAGDATA_VERSION" : "0.1",');
    -- DB 기본정보 입력
    DBMS_OUTPUT.PUT_LINE('"DBINFO" : {');
    FOR DBINFO IN C_DBINFO LOOP
        DBMS_OUTPUT.PUT_LINE('"DBNAME" : "'||DBINFO.NAME||'",');
        DBMS_OUTPUT.PUT_LINE('"DBUNQNAME" : "'||DBINFO.DB_UNIQUE_NAME||'",');
        DBMS_OUTPUT.PUT_LINE('"INSTANCE_NAME" : "'||DBINFO.INSTANCE_NAME||'",');
        DBMS_OUTPUT.PUT_LINE('"HOSTNAME" : "'||DBINFO.HOST_NAME||'",');
        DBMS_OUTPUT.PUT_LINE('"VERSION" : "'||DBINFO.VERSION||'",');
        DBMS_OUTPUT.PUT_LINE('"DATABASE_TYPE" : "'||DBINFO.DATABASE_TYPE||'",');
        IF DBINFO.DATABASE_TYPE = 'RAC' THEN
          SELECT COUNT(*) INTO V_ONI_COUNT FROM GV$INSTANCE WHERE INST_ID != DBINFO.INSTANCE_NUMBER;
          DBMS_OUTPUT.PUT_LINE('"INSTANCE_NUMBER" : '||DBINFO.INSTANCE_NUMBER||',');
          DBMS_OUTPUT.PUT_LINE('"OTHER_NODE_INFO" : [');
          V_ONI_COUNTER := 1;
          FOR ONI IN (
            SELECT INSTANCE_NUMBER,
                   INSTANCE_NAME,
                   HOST_NAME
              FROM GV$INSTANCE
             WHERE INST_ID != DBINFO.INSTANCE_NUMBER
          ) LOOP
            DBMS_OUTPUT.PUT_LINE('{');
            DBMS_OUTPUT.PUT_LINE('"INSTANCE_NUMBER" :'||ONI.INSTANCE_NUMBER||',');
            DBMS_OUTPUT.PUT_LINE('"INSTANCE_NAME" : "'||ONI.INSTANCE_NAME||'",');
            DBMS_OUTPUT.PUT_LINE('"HOSTNAME" : "'||ONI.HOST_NAME||'"');
            IF V_ONI_COUNTER = V_ONI_COUNT THEN
              DBMS_OUTPUT.PUT_LINE('}');
            ELSE
              DBMS_OUTPUT.PUT_LINE('},');
              V_ONI_COUNTER := V_ONI_COUNTER + 1;
            END IF;
          END LOOP;
          DBMS_OUTPUT.PUT_LINE(']');
        ELSE
          DBMS_OUTPUT.PUT_LINE('"INSTANCE_NUMBER" : '||DBINFO.INSTANCE_NUMBER);
        END IF;
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('},');
  END;
  -- 메모리 시작
  DBMS_OUTPUT.PUT_LINE('"MEMORY" : {');
  DECLARE
    V_VERSION            BINARY_INTEGER;
    V_TOTAL_SGA          NUMBER(10,2);
    V_USED_PGA           NUMBER(10,2);
    V_LIMIT_PGA          NUMBER(10,2);
    V_ALLOC_PGA          NUMBER(10,2);
    V_FREEABLE_PGA       NUMBER(10,2);
    V_TARGET_PGA         NUMBER(10,2);
    V_USE_RATE           NUMBER(5,2);
    V_PGA_RESULT         VARCHAR2(25);
  BEGIN
    -- GET VERSION
    SELECT TO_NUMBER(SUBSTR(VERSION,1,INSTR(VERSION,'.',1)-1)) INTO V_VERSION
      FROM V$INSTANCE;
    -- GET pga_aggregate_target PARAMETER IN MB
    SELECT VALUE/1024/1024 INTO V_TARGET_PGA
      FROM V$PARAMETER
     WHERE NAME = 'pga_aggregate_target';
    -- GET TOTAL SGA SIZE IN MB
    SELECT SUM(VALUE)/1024/1024 INTO V_TOTAL_SGA
      FROM V$SGA;
    SELECT SUM(PGA_USED_MEM)/1024/1024,
           SUM(PGA_ALLOC_MEM)/1024/1024,
           SUM(PGA_FREEABLE_MEM)/1024/1024
      INTO V_USED_PGA, V_ALLOC_PGA, V_FREEABLE_PGA
     FROM V$PROCESS;
    -- Version >= 12
    IF V_VERSION >= 12 THEN
      SELECT VALUE/1024/1024 INTO V_LIMIT_PGA
        FROM V$PARAMETER
       WHERE NAME = 'pga_aggregate_limit';
    END IF;
    DBMS_OUTPUT.PUT_LINE('"SGA" : '||V_TOTAL_SGA||',');
    DBMS_OUTPUT.PUT_LINE('"PGA" : '||V_TARGET_PGA||',');
    DBMS_OUTPUT.PUT_LINE('"ALLOCATE" : '||V_ALLOC_PGA||',');
    DBMS_OUTPUT.PUT_LINE('"USED" : '||V_USED_PGA||',');
    -- 12버전 이상일 경우 pga limit 기준으로 사용율 조회, 이하일 경우 pga target 기준.
    IF V_VERSION >=12 THEN
      DBMS_OUTPUT.PUT_LINE('"PGALIMIT" : '||V_LIMIT_PGA||',');
      V_USE_RATE := ROUND(V_ALLOC_PGA/V_LIMIT_PGA * 100,2);
    ELSE
      V_USE_RATE := ROUND(V_ALLOC_PGA/V_TARGET_PGA * 100,2);
    END IF;
    DBMS_OUTPUT.PUT_LINE('"FREEABLE" : '||V_FREEABLE_PGA);
    DBMS_OUTPUT.PUT_LINE('},');
  END;
  -- 메모리 종료
  -- SGA OPERATION 시작
  DECLARE
    V_DO_SGA_OPER            BINARY_INTEGER;
    V_DO_SGA_OPER_CNT        BINARY_INTEGER;
    V_COMP_ACTIVE_CNT        BINARY_INTEGER;
    V_COMP_ACTIVE_CNT_CHECK  BINARY_INTEGER;
  BEGIN
    -- 1일동안 SGA 내 풀들의 변경여부 확인
    SELECT COUNT(DISTINCT COMPONENT) INTO V_DO_SGA_OPER
      FROM V$SGA_RESIZE_OPS
     WHERE START_TIME >= TRUNC(SYSDATE-1)
        OR END_TIME >= TRUNC(SYSDATE-1);

    IF V_DO_SGA_OPER > 0 THEN
      DBMS_OUTPUT.PUT_LINE('"SGAOPER" : {');
      V_DO_SGA_OPER_CNT := 1;
      FOR C_COMP_NAME IN (SELECT DISTINCT COMPONENT COMP_NAME
                            FROM V$SGA_RESIZE_OPS
                           WHERE START_TIME >= TRUNC(SYSDATE-1)
                              OR END_TIME >= TRUNC(SYSDATE-1)
      ) LOOP
        -- 각 개별 컴포넌트의 활동이 몇건인지 센다.
        SELECT COUNT(*) INTO V_COMP_ACTIVE_CNT
          FROM V$SGA_RESIZE_OPS
         WHERE COMPONENT = C_COMP_NAME.COMP_NAME
           AND (START_TIME >= TRUNC(SYSDATE-1) OR END_TIME >= TRUNC(SYSDATE-1));
        V_COMP_ACTIVE_CNT_CHECK := 1;
        DBMS_OUTPUT.PUT_LINE('"'||C_COMP_NAME.COMP_NAME||'" : [');
        FOR C_COMP_DATA IN (SELECT TO_CHAR(START_TIME,'YYYY/MM/DD HH24:MI:SS') STARTDATE,
                                   TO_CHAR(END_TIME,'YYYY/MM/DD HH24:MI:SS') ENDDATE,
                                   OPER_TYPE OPERATION,
                                   OPER_MODE OPERTYPE,
                                   INITIAL_SIZE/1024/1024 INITIAL_SZ,
                                   TARGET_SIZE/1024/1024  TARGET_SZ,
                                   FINAL_SIZE/1024/1024   FINAL_SZ,
                                   STATUS
                              FROM V$SGA_RESIZE_OPS
                             WHERE COMPONENT = C_COMP_NAME.COMP_NAME
                               AND (START_TIME >= TRUNC(SYSDATE-1) OR
                                    END_TIME >= TRUNC(SYSDATE-1))
        ) LOOP
          DBMS_OUTPUT.PUT_LINE('{');
          DBMS_OUTPUT.PUT_LINE('"STARTDATE" : "'||C_COMP_DATA.STARTDATE||'",');
          DBMS_OUTPUT.PUT_LINE('"ENDDATE" : "'||C_COMP_DATA.ENDDATE||'",');
          DBMS_OUTPUT.PUT_LINE('"OPERATION" : "'||C_COMP_DATA.OPERATION||'",');
          DBMS_OUTPUT.PUT_LINE('"OPERTYPE" : "'||C_COMP_DATA.OPERTYPE||'",');
          DBMS_OUTPUT.PUT_LINE('"INITIAL" : '||C_COMP_DATA.INITIAL_SZ||',');
          DBMS_OUTPUT.PUT_LINE('"TARGET" : '||C_COMP_DATA.TARGET_SZ||',');
          DBMS_OUTPUT.PUT_LINE('"FINAL" : '||C_COMP_DATA.FINAL_SZ||',');
          DBMS_OUTPUT.PUT_LINE('"STATUS" : "'||C_COMP_DATA.STATUS||'"');
          IF V_COMP_ACTIVE_CNT_CHECK < V_COMP_ACTIVE_CNT THEN
            DBMS_OUTPUT.PUT_LINE('},');
            V_COMP_ACTIVE_CNT_CHECK := V_COMP_ACTIVE_CNT_CHECK + 1;
          ELSE
            DBMS_OUTPUT.PUT_LINE('}');
          END IF;
        END LOOP;
        IF V_DO_SGA_OPER_CNT < V_DO_SGA_OPER THEN
          DBMS_OUTPUT.PUT_LINE('],');
          V_DO_SGA_OPER_CNT := V_DO_SGA_OPER_CNT + 1;
        ELSE
          DBMS_OUTPUT.PUT_LINE(']');
        END IF;
      END LOOP;
      DBMS_OUTPUT.PUT_LINE('},');
    ELSE
      DBMS_OUTPUT.PUT_LINE('"SGAOPER" : "NoData",');
    END IF;
  END;
  -- SGA OPERATION 종료
  -- TABLESPACE 시작
  DECLARE
    V_TABLESPACE_CNT            BINARY_INTEGER;
    V_TABLESPACE_CNT_CHECK      BINARY_INTEGER;
  BEGIN
    SELECT COUNT(*) INTO V_TABLESPACE_CNT
      FROM DBA_TABLESPACES
     WHERE CONTENTS != 'TEMPORARY';
    V_TABLESPACE_CNT_CHECK := 1;
    DBMS_OUTPUT.PUT_LINE('"TABLESPACE" : [');
    FOR C_TBS IN (SELECT TABLESPACE_NAME NAME,
                         TMB             TOTAL,
                         TMB-FMB         USED
                    FROM (SELECT DF.TABLESPACE_NAME,
                                 ROUND(DF.MB,2) TMB,
                                 ROUND(FS.MB,2) FMB
                            FROM (SELECT TABLESPACE_NAME,
                                         SUM(BYTES)/1024/1024 AS MB
                                    FROM DBA_DATA_FILES
                                  GROUP BY TABLESPACE_NAME) DF,
                                  (SELECT TABLESPACE_NAME,
                                          SUM(BYTES)/1024/1024 AS MB
                                     FROM DBA_FREE_SPACE
                                   GROUP BY TABLESPACE_NAME) FS
                            WHERE DF.TABLESPACE_NAME = FS.TABLESPACE_NAME(+))
    ) LOOP
      DBMS_OUTPUT.PUT_LINE('{');
      DBMS_OUTPUT.PUT_LINE('"NAME" : "'||C_TBS.NAME||'",');
      DBMS_OUTPUT.PUT_LINE('"TOTAL" : '||C_TBS.TOTAL||',');
      DBMS_OUTPUT.PUT_LINE('"USED" : '||C_TBS.USED);
      IF V_TABLESPACE_CNT_CHECK < V_TABLESPACE_CNT THEN
        DBMS_OUTPUT.PUT_LINE('},');
        V_TABLESPACE_CNT_CHECK := V_TABLESPACE_CNT_CHECK + 1;
      ELSE
        DBMS_OUTPUT.PUT_LINE('}');
      END IF;
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('],');
  END;
  -- TABLESPACE 종료
  -- ASM 시작
  DECLARE
    V_ASM_CNT          BINARY_INTEGER;
    V_ASM_CNT_CHECK    BINARY_INTEGER;
  BEGIN
    SELECT COUNT(*) INTO V_ASM_CNT
      FROM V$ASM_DISKGROUP;
    V_ASM_CNT_CHECK := 1;
    IF V_ASM_CNT > 0 THEN
      DBMS_OUTPUT.PUT_LINE('"ASM" : [');
      FOR C_ASM IN (SELECT GROUP_NUMBER,
                           NAME,
                           TOTAL_MB,
                           USABLE_FILE_MB,
                           TYPE
                      FROM V$ASM_DISKGROUP) LOOP
        DBMS_OUTPUT.PUT_LINE('{');
        DBMS_OUTPUT.PUT_LINE('"GROUP_NUMBER" : '||C_ASM.GROUP_NUMBER||',');
        DBMS_OUTPUT.PUT_LINE('"NAME" : "'||C_ASM.NAME||'",');
        DBMS_OUTPUT.PUT_LINE('"TOTAL" : '||C_ASM.TOTAL_MB||',');
        DBMS_OUTPUT.PUT_LINE('"USABLE" : '||C_ASM.USABLE_FILE_MB||',');
        DBMS_OUTPUT.PUT_LINE('"REDUNDANCY" : "'||C_ASM.TYPE||'"');
        IF V_ASM_CNT_CHECK < V_ASM_CNT THEN
          DBMS_OUTPUT.PUT_LINE('},');
          V_ASM_CNT_CHECK := V_ASM_CNT_CHECK + 1;
        ELSE
          DBMS_OUTPUT.PUT_LINE('}');
        END IF;
      END LOOP;
      DBMS_OUTPUT.PUT_LINE('],');
    ELSE
      DBMS_OUTPUT.PUT_LINE('"ASM" : "NoData",');
    END IF;
  END;
  -- ASM 종료
  -- BACKUP 시작
  DECLARE
    V_BACKUP_CNT        BINARY_INTEGER;
    V_BACKUP_CNT_CHECK  BINARY_INTEGER;
  BEGIN
    SELECT COUNT(*) INTO V_BACKUP_CNT
      FROM V$RMAN_BACKUP_JOB_DETAILS
     WHERE START_TIME >= TRUNC(SYSDATE-2);

    IF V_BACKUP_CNT > 0 THEN
      DBMS_OUTPUT.PUT_LINE('"BACKUP" : [');
      V_BACKUP_CNT_CHECK := 1;
      FOR C_RB IN (
                   SELECT TO_CHAR(START_TIME,'YYYY/MM/DD HH24:MI:SS') START_TIME,
                          OUTPUT_BYTES_DISPLAY,
                          STATUS
                     FROM V$RMAN_BACKUP_JOB_DETAILS
                    WHERE START_TIME >= TRUNC(SYSDATE-2)
                   ORDER BY 1 DESC
      ) LOOP
        DBMS_OUTPUT.PUT_LINE('{');
        DBMS_OUTPUT.PUT_LINE('"STARTDATE" : "'||C_RB.START_TIME||'",');
        DBMS_OUTPUT.PUT_LINE('"SIZE" : "'||C_RB.OUTPUT_BYTES_DISPLAY||'",');
        DBMS_OUTPUT.PUT_LINE('"STATUS" : "'||C_RB.STATUS||'"');
        IF V_BACKUP_CNT_CHECK < V_BACKUP_CNT THEN
          DBMS_OUTPUT.PUT_LINE('},');
          V_BACKUP_CNT_CHECK := V_BACKUP_CNT_CHECK + 1;
        ELSE
          DBMS_OUTPUT.PUT_LINE('}');
        END IF;
      END LOOP;
      DBMS_OUTPUT.PUT_LINE('],');
    ELSE
      DBMS_OUTPUT.PUT_LINE('"BACKUP" : "NoData",');
    END IF;
  END;
  -- BACKUP 종료
  -- DG 체크
  DECLARE
      V_USE_DG           BINARY_INTEGER;
      V_CNT_CHECK        BINARY_INTEGER;
      V_PRI_SCN          DATE;
      V_DIFF             NUMBER(10,3);
  BEGIN
    SELECT COUNT(*) INTO V_USE_DG FROM V$DATAGUARD_CONFIG;
    IF V_USE_DG > 0 THEN
      V_CNT_CHECK := 1;
      DBMS_OUTPUT.PUT_LINE('"DG" : [');
      FOR DG_VALUE IN (
        SELECT LEVEL,
               INDX,
               INST_ID,
               DGCDBUN  DB_UNIQ_ID,
               DGCPDBUN PARENT_DB_UNIQ_ID,
               DECODE(DGCDROLE, 1, 'PRIMARY DATABASE' ,
                                2, 'PHYSICAL STANDBY' ,
                                3, 'SNAPSHOT STANDBY' ,
                                4, 'FAR SYNC INSTANCE',
                                5, 'LOGICAL STANDBY'  ,
                                6, 'BACKUP APPLIANCE' ,
                                'UNKNOWN') DB_ROLE,
               TO_CHAR(SCN_TO_TIMESTAMP(DGCSCN),'YYYY/MM/DD HH24:MI:SS') CURRENT_SCN
          FROM X$KRSTDGC
        CONNECT BY PRIOR DGCDBUN = DGCPDBUN
        START WITH DGCPDBUN = 'NONE'
      ) LOOP
        DBMS_OUTPUT.PUT_LINE('{');
        DBMS_OUTPUT.PUT_LINE('"LEVEL" : '||DG_VALUE.LEVEL||',');
        DBMS_OUTPUT.PUT_LINE('"INST_ID" : '||DG_VALUE.INST_ID||',');
        DBMS_OUTPUT.PUT_LINE('"DBUNIQNAME" : "'||DG_VALUE.DB_UNIQ_ID||'",');
        DBMS_OUTPUT.PUT_LINE('"PARENTDB" : "'||DG_VALUE.PARENT_DB_UNIQ_ID||'",');
        DBMS_OUTPUT.PUT_LINE('"ROLE" : "'||DG_VALUE.DB_ROLE||'",');
        DBMS_OUTPUT.PUT_LINE('"SCN" : "'||DG_VALUE.CURRENT_SCN||'"');
        IF V_CNT_CHECK = V_USE_DG THEN
          DBMS_OUTPUT.PUT_LINE('}');
        ELSE
          DBMS_OUTPUT.PUT_LINE('},');
          V_CNT_CHECK := V_CNT_CHECK + 1;
        END IF;
      END LOOP;
      DBMS_OUTPUT.PUT_LINE('],');
    ELSE
      DBMS_OUTPUT.PUT_LINE('"DG" : "NoData",');
    END IF;
  END;
  -- DG 종료
  -- ALERT 시작
  DECLARE
    V_ALERT_CNT         BINARY_INTEGER;
    V_ALERT_CNT_CHECK   BINARY_INTEGER;
  BEGIN
    SELECT COUNT(*) INTO V_ALERT_CNT
      FROM V$DIAG_ALERT_EXT
     WHERE ORIGINATING_TIMESTAMP BETWEEN TRUNC(SYSDATE-1) AND SYSDATE
       AND MESSAGE_TEXT LIKE '%ORA-%';

    IF V_ALERT_CNT > 0 THEN
      V_ALERT_CNT_CHECK := 1;
      DBMS_OUTPUT.PUT_LINE('"ALERT" : [');
      FOR C_ALERT IN (
        SELECT TO_CHAR(ORIGINATING_TIMESTAMP,'YYYY/MM/DD-HH24:MI:SS') DT,
               REPLACE(SUBSTR(REPLACE(REPLACE(MESSAGE_TEXT,CHR(10),''),CHR(13),''),1,150),'"','\"') MESSAGE_TEXT
          FROM V$DIAG_ALERT_EXT
         WHERE ORIGINATING_TIMESTAMP BETWEEN TRUNC(SYSDATE-1) AND SYSDATE
           AND MESSAGE_TEXT LIKE '%ORA-%'
      ) LOOP
        DBMS_OUTPUT.PUT_LINE('{');
        DBMS_OUTPUT.PUT_LINE('"LOGDATE" : "'||C_ALERT.DT||'",');
        DBMS_OUTPUT.PUT_LINE('"LOGMESSAGE" : "'||C_ALERT.MESSAGE_TEXT||'"');
        IF V_ALERT_CNT_CHECK < V_ALERT_CNT THEN
          DBMS_OUTPUT.PUT_LINE('},');
          V_ALERT_CNT_CHECK := V_ALERT_CNT_CHECK + 1;
        ELSE
          DBMS_OUTPUT.PUT_LINE('}');
        END IF;
      END LOOP;
      DBMS_OUTPUT.PUT_LINE(']');
    ELSE
      DBMS_OUTPUT.PUT_LINE('"ALERT" : "NoData"');
    END IF;
  END;
  -- ALERT 종료
  -- jSON 끝
  DBMS_OUTPUT.PUT_LINE('}');
END;
/
SPOOL OFF
EXIT
