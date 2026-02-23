#!/bin/bash

# Get variables from .profile
source /home/scripts/.profile

# Define the directory where you want to save the log files
LogDir="/home/scripts/CD2/logs"

# Get the current date and time in YYYY-MM-DD format
CurrentDate=$(date +'%Y-%m-%d')
CurrentTime=$(date +'%H%M')

# Define the log file path with the current date and time
LogFile="$LogDir/CD2_Table_Log_[$(date +'%Y-%m-%d %H:%M:%S')].txt"

# Define the list of table names
tableNames=("account_users" "attachments" "accounts" "assignment_groups" "assignments" "content_participation_counts" "content_participations" "context_module_progressions" "course_sections" "courses" "enrollment_terms" "enrollments" "grading_periods" "grading_standards" "late_policies" "pseudonyms" "quiz_submissions" "score_statistics" "scores" "submissions" "users" "user_account_associations" "course_account_associations" "communication_channels")
# "account_users" "attachments" "accounts" "assignment_groups" "assignments" "content_participation_counts" "content_participations" "context_module_progressions" "course_sections" "courses" "enrollment_terms" "enrollments" "grading_periods" "grading_standards" "late_policies" "pseudonyms" "quiz_submissions" "score_statistics" "scores" "submissions" "users" "user_account_associations" "course_account_associations" "communication_channels"
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

