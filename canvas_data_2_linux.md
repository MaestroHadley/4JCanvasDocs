# Canvas Data 2 Setup in Linux #

Once you have installed your Python, DAP client, and PostgreSQL server, just as you would in any other environment, you can use the following shell scripts and commands to assist you. 

For setting up PostgreSQL or looking at this from a Windows environment, there is additional information [here](canvas_data_2.md).

For this to work automatically in a Linux environment you must set some additional system variables. One being the `PGPASSWORD` for your Postgres user in PostgreSQL. 


In this file there are two key functions: update_tables.sh and export_tsv.sh 

As their names indicate, their functions are to download and sync the database tables from CD2 and then export them to a destination folder on the same folder or other folder in your environment. 

## Update Tables##
Let's start with `update_tables.sh`-
    #!/bin/bash

    # Get variables from .profile you will need to define your own path to the profile in your system. 
    source /home/scripts/.profile

    # Define the directory where you want to save the log files
    LogDir="/home/scripts/CD2/logs"

    # Get the current date and time in YYYY-MM-DD format
    CurrentDate=$(date +'%Y-%m-%d')
    CurrentTime=$(date +'%H%M')

    # Define the log file path with the current date and time
    LogFile="$LogDir/CD2_Table_Log_[$(date +'%Y-%m-%d %H:%M:%S')].txt"

    # Define the list of table names
    tableNames=("account_users" "accounts" "assignment_groups" "assignments" "content_participation_counts" "content_participations" "context_module_progressions" "course_sections" "courses" "enrollment_terms" "enrollments" "grading_periods" "grading_standards" "late_policies" "pseudonyms" "quiz_submissions" "score_statistics" "scores" "submissions" "users")
    # "account_users" "accounts" "assignment_groups" "assignments" "content_participation_counts" "content_participations" "context_module_progressions" "course_sections" "courses" "enrollment_terms" "enrollments" "grading_periods" "grading_standards" "late_policies" "pseudonyms" "quiz_submissions" "score_statistics" "scores" "submissions" "users"

    # Loop through each table name
    for tableName in "${tableNames[@]}"; do
        # Record the start time
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting operations for table $tableName" >> "$LogFile"
    
        # Synchronize the database table
        dap syncdb --namespace canvas --table "$tableName" --connection-string "$DAP_CONNECTION_STRING" 2>&1 >> "$LogFile"
        
        if [ $? -ne 0 ]; then
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] Failed to synchronize table $tableName" >> "$LogFile"
        else
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] Successfully synchronized table $tableName" >> "$LogFile"
        fi
        
        # Optional: Add a delay between operations for each table (5 seconds here)
        sleep 5

    done

    # Log the completion time of all operations
    echo "Operation completed at: [$(date +'%Y-%m-%d %H:%M:%S')]" >> "$LogFile"

In this function we are **syncing** the database wiht the tables in our server. If you have not yet **initialized** your tables, you will need to modify the line: 
`dap syncdb --namespace canvas --table "$tableName" --connection-string "$DAP_CONNECTION_STRING" 2>&1 >> "$LogFile"` and swap `syncdb` with `initdb`. Be sure to switch it back once the tables are initialized, otherwise it will skip them and you won't get new data. 
Be sure to update the `LogDir` and `OutputDir` variables. 

## Exporting TSVs ##
For our needs, we are exporting our tables from the PostgreSQL database to TSV files to be imported to other systems and databases across our system. 

The first setup piece is establishin in PostgreSQL a function to export all tables to a TSV file (or file of your choosing). 
To do so, log into PSQL as a user with root access. 

`psql -U postres -h localhost -W -d #name_of_database` 

Once logged in, you can execute the following SQL command, note that you'll want to update the destination as well as if you want to alter the export type. 

    CREATE OR REPLACE FUNCTION export_all_tables_to_tsv()
    RETURNS void AS $$
    DECLARE
        table_name_alias text;  -- Renamed the variable for clarity
    BEGIN
        -- Loop through all tables in the schema
        FOR table_name_alias IN
            SELECT table_name FROM information_schema.tables WHERE table_schema = 'canvas'
        LOOP
            -- Construct the dynamic SQL query with the updated directory path
            EXECUTE format('COPY (SELECT * FROM canvas.%I) TO ''#OUTPUTDESTINATION/%I.tsv'' WITH DELIMITER E''\t'' CSV HEADER', table_name_alias, table_name_alias);

            -- You can add additional logic or logging here if needed
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;

Exit psql with `\q`. You are almost there. 

The shell script is as follows, and it is crucial that you have the environmental variable for `PGPASSWORD` available to all users on the server. 

    #!/bin/bash
    source /home/scripts/.profile #Here I am setting the source for the environment. Yours is different. 
    # Define the directory where you want to save the log files.
    LogDir="/home/scripts/CD2/tsv_logs"
    OutputDir="/mnt/canvasimport"  # Specify your desired output directory
    echo "Script is open" 
    # Ensure the log directory exists
    if [ ! -d "$LogDir" ]; then
        mkdir -p "$LogDir"
    fi

    # Ensure the output directory exists
    if [ ! -d "$OutputDir" ]; then
        echo "Creating output directory: $OutputDir"
        mkdir -p "$OutputDir"
    fi
    echo "$LogDir"
    echo "$OutputDir"

    # Get the current date and time in YYYY-MM-DD_HHMM format.
    CurrentDate=$(date +'%Y-%m-%d')
    CurrentTime=$(date +'%H%M')
    echo "$CurrentDate"
    echo "$CurrentTime"

    # Define the log file path with the current date and time.
    LogFile="$LogDir/CD2_Table_Export_[$(date +'%Y-%m-%d %H:%M:%S')].txt"
    echo "$LogFile"

    # Log the start of operations.
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting TSV export" >> "$LogFile"

    # Execute the PostgreSQL command with the output directory and redirect both stdout and stderr to the log file. Be sure to change the database name -d to yours. 
    psql -U postgres -h localhost -p 5432 -d canvasdata2 -c "SELECT export_all_tables_to_tsv();" >> "$LogFile" 2>&1

    # Log the completion of operations.
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] TSV export completed" >> "$LogFile"

This function will now export TSV files to your `OutputDir` so be sure to set that directory as well as the LogDir for logging. 

You may also run into permission issues. All the folders in this project need to be given full RWX permissions, I believe that is done with `chmod 777 /path to element/folder`. 


If you would like to run these tasks automatically with Cron you will need to pass your pgPASSWORD through Cron. For example: 


    PATH=/home/scripts/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games

    00 23 * * *  /home/scripts/scripts/update_tables.sh 
    30 23 * * * export PGPASSWORD=YOUR_PASSWORD_HERE && /home/scripts/scripts/export_tsv.sh

We had to modify our version to include the PATH to the scripts and other elements as noted above in the PATH variable, you may not need to include/or customize it, depending on your server setup. 