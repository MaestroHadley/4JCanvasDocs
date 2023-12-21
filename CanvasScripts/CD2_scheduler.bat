@echo off
SETLOCAL EnableDelayedExpansion

REM Define the directory where you want to save the log files
SET LogDir=C:\Users\hadley_n\Documents\CD2\logs

REM Get the current date and time in YYYY-MM-DD format
FOR /F "tokens=2-4 delims=/ " %%A IN ('DATE /T') DO (
    SET CurrentDate=%%C-%%A-%%B
)

FOR /F "tokens=1-2 delims=/:" %%A IN ("%TIME%") DO (
    SET CurrentTime=%%A%%B
)

REM Define the log file path with the current date and time
SET LogFile=%LogDir%\CD2_Table_Log_%CurrentDate%.rtf

REM Define the list of table names
SET tableNames=account_users accounts assignment_groups assignments content_participation_counts content_participations context_module_progressions course_sections courses enrollment_terms enrollments grading_periods grading_standards late_policies pseudonyms quiz_submissions score_statistics scores submissions users

REM Loop through each table name
FOR %%T IN (%tableNames%) DO (
    REM Record the start time
    echo [%CurrentDate%_%CurrentTime%] Starting operations for table %%T >> %LogFile%

    REM Initialize the database table (if needed)
   REM dap initdb --namespace canvas --table %%T --connection-string "%DAP_CONNECTION_STRING%"
   REM IF !ERRORLEVEL! NEQ 0 (
   REM     echo [%CurrentDate%_%CurrentTime%] Failed to initialize table %%T >> %LogFile%
   REM ) ELSE (
   REM     echo [%CurrentDate%_%CurrentTime%] Successfully initialized table %%T >> %LogFile%
   REM )

    REM Synchronize the database table
     dap syncdb --namespace canvas --table %%T --connection-string "%DAP_CONNECTION_STRING%"
     IF !ERRORLEVEL! NEQ 0 (
         echo [%CurrentDate%_%CurrentTime%] Failed to synchronize table %%T >> %LogFile%
     ) ELSE (
         echo [%CurrentDate%_%CurrentTime%] Successfully synchronized table %%T >> %LogFile%
     )

    REM Optional: Add a delay between operations for each table (20 seconds here)
    TIMEOUT /T 5
)

ENDLOCAL