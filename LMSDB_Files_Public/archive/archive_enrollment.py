#!/home/scripts/.local/pipx/shared/bin/python 
"""Builds and uploads SIS imports to deactivate old enrollments using Canvas Data query output."""
from canvasapi import Canvas
import dblogin
import os
import psycopg2
import pandas as pd
import requests
import time
from datetime import datetime
import logging
print("Canvas Archive running",datetime.now())
# Canvas API setup
API_URL = 'https://4j.instructure.com'
API_KEY = os.getenv('API_KEYLIVE')
canvas = Canvas(API_URL, API_KEY)
account = canvas.get_account(1)


LOG_FILE = "/home/scripts/archive/enrollment_log.log"


# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable for term prefix
term_prefix = f"{datetime.now().year - 2}"
logging.info(f"Global term_prefix set to: {term_prefix}")


#Connect and generate sql query for archiving enrollments
def run_query_and_generate_report(term_prefix):
    """Run SQL query for a specific sis_id and generate a report."""
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=dblogin.DB_HOST,
        database=dblogin.DB_NAME,
        user=dblogin.DB_USER,
        password=dblogin.DB_PASSWORD
    )

    # Define the SQL query with the sis_id
    query = f"""
    SELECT courses.sis_source_id  AS course_id,
        pseudonyms.sis_user_id AS user_id,
        enrollments.role_id,
        sections.sis_source_id AS section_id
    FROM canvas.pseudonyms pseudonyms
            JOIN canvas.enrollments enrollments ON pseudonyms.user_id = enrollments.user_id
            JOIN canvas.courses courses ON enrollments.course_id = courses.id
            JOIN canvas.course_sections sections ON enrollments.course_section_id = sections.id
    WHERE pseudonyms.sis_user_id::text ~~ 'staff_%'::text
    AND (pseudonyms.user_id IN (SELECT pseudonyms_1.user_id
                                FROM canvas.pseudonyms pseudonyms_1
                                WHERE pseudonyms_1.sis_user_id::text ~~ 'staff_%'::text))
    AND (enrollments.workflow_state::text ~~ 'active'::text OR enrollments.workflow_state::text ~~ 'completed'::text)
    AND courses.sis_source_id IS NOT NULL
    AND enrollments.role_id::text ~~ '4'::text
    AND courses.sis_source_id::text ~~ '{term_prefix}_%'::text
    ORDER BY pseudonyms.user_id, courses.sis_source_id, sections.sis_source_id;
    """
    df = pd.read_sql_query(query,conn)
    conn.close()
    df['status'] = 'inactive'
    enrollment_import_file = '/home/scripts/archive/enrollments.csv'
    df.to_csv(enrollment_import_file, index=False)
    logging.info(f"Preview of enrollment CSV:\n{pd.read_csv(enrollment_import_file).head()}")
    upload_sis_import(enrollment_import_file)

    

def upload_sis_import(file_path):
    """Uploads the SIS import file to Canvas and waits for it to process."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"attachment": open(file_path, 'rb')}
    url = f"{API_URL}/api/v1/accounts/{account.id}/sis_imports"
    
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        import_data = response.json()
        import_id = import_data.get("id")
        logging.info(f"SIS Import successfully uploaded. Import ID: {import_id}")
        
        # Polling to check the status
        check_sis_import_status(import_id)
    else:
        logging.error(f"Failed to upload SIS Import. Response: {response.text}")

def check_sis_import_status(import_id):
    """Polls Canvas to check the status of the SIS import."""
    url = f"{API_URL}/api/v1/accounts/{account.id}/sis_imports/{import_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            import_data = response.json()
            status = import_data.get("workflow_state", "unknown")
            progress = import_data.get("progress", 0)
            logging.info(f"SIS Import {import_id} Status: {status}, Progress: {progress}%")
            
            if status in ["imported", "completed", "imported_with_messages"]:
                logging.info(f"SIS Import {import_id} finished processing.")
                break
            elif status in ["failed", "aborted"]:
                logging.error(f"SIS Import {import_id} failed or was aborted.")
                break
        else:
            logging.error(f"Error checking SIS import status: {response.text}")
        
        time.sleep(30)  # Wait before checking again


if __name__ == "__main__":
    #run query and archive teacher enrollments from 2 years ago.
    run_query_and_generate_report(term_prefix)
    #run the archive_courses script to archive last year's courses. 
    logging.info("Calling Archive Script")
    logging.shutdown()
    os.system("/home/scripts/.local/pipx/shared/bin/python /home/scripts/archive/archive_courses.py")
