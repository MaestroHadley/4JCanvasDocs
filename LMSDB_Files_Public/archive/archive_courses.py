#!/home/scripts/.local/pipx/shared/bin/python 

"""Coordinates course archival by generating Canvas reports, preparing SIS imports, uploading them, and cleaning old terms."""

from canvasapi import Canvas
import time
import requests
import os
import pandas as pd
from datetime import datetime
import logging


LOG_FILE = "/home/scripts/archive/archive_log.log"


# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Canvas API setup
API_URL = 'https://4j.instructure.com'
API_KEY = os.getenv('API_KEYLIVE')
canvas = Canvas(API_URL, API_KEY)
account = canvas.get_account(1)

# Global variable for term prefix
term_prefix = f"{datetime.now().year - 2}/{datetime.now().year - 1}"
logging.info(f"Global term_prefix set to: {term_prefix}")

def request_report(report_type, params, output_file):
    """Generic function to request and download a report."""
    report = account.create_report(report_type, parameters=params)
    logging.info(f"Report requested, ID: {report.id}")
    
    while True:
        report_status = account.get_report(report_type, report.id)
        progress, status = report_status.progress, report_status.status
        logging.info(f"Progress: {progress}%, Status: {status}")
        
        if status == 'complete':
            file_url = report_status.attachment.get('url')
            if file_url:
                response = requests.get(file_url)
                with open(output_file, 'wb') as file:
                    file.write(response.content)
                logging.info(f"Report downloaded: {output_file}")
            return
        elif status == 'failed':
            logging.error("Report generation failed.")
            return
        time.sleep(5)

def download_terms():
    """Download terms provisioning report."""
    request_report('provisioning_csv', {'terms': "1", 'locale': "en"}, '/home/scripts/archive/terms_report.csv')

def get_terms():
    """Retrieve term IDs matching term_prefix for filtering courses."""
    df = pd.read_csv('/home/scripts/archive/terms_report.csv')
    matching_terms = df[df['name'].str.startswith(term_prefix, na=False)]
    return matching_terms['term_id'].tolist()

def get_canvas_term_ids():
    """Retrieve Canvas term IDs matching term_prefix for deletion."""
    df = pd.read_csv('/home/scripts/archive/terms_report.csv')
    matching_terms = df[df['name'].str.startswith(term_prefix, na=False)]
    return matching_terms['canvas_term_id'].tolist()

def download_sis_export():
    """Download SIS export report for course data."""
    request_report('sis_export_csv', {'courses': "1", 'locale': "en"}, '/home/scripts/archive/sis_export.csv')

def process_sis_import(term_names):
    """Filter SIS export and create SIS import archive for automated upload."""
    df = pd.read_csv('/home/scripts/archive/sis_export.csv')
    filtered_courses = df[df['term_id'].isin(term_names)]
    filtered_courses['term_id'] = '4JArchive'

    # Append the term suffix to course names
    filtered_courses['short_name'] = filtered_courses['short_name'].astype(str) + f"_{term_prefix}"
    filtered_courses['long_name'] = filtered_courses['long_name'].astype(str) + f"_{term_prefix}"

    archive_file = '/home/scripts/archive/courses.csv'  # Renamed for SIS import
    filtered_courses.to_csv(archive_file, index=False)
    logging.info(f"SIS import archive created: {archive_file}")
    upload_sis_import(archive_file)

def upload_sis_import(file_path):
    """Uploads the SIS import file to Canvas and waits for it to process."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"attachment": open(file_path, 'rb')}
    url = f"{API_URL}/api/v1/accounts/{account.id}/sis_imports"
    
    params = {
        "override_sis_stickiness": "true"
    }
    
    response = requests.post(url, headers=headers, files=files, params=params)
    
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
        
        time.sleep(300)  # Wait before checking again

def download_courses():
    """Download courses provisioning report."""
    request_report('provisioning_csv', {'courses': "1", 'include_deleted':"1", 'locale': "en"}, '/home/scripts/archive/courses_provisioning.csv')

def cleanup(term_names):
    """Filter and update courses via API to new term (4JArchive)."""
    df_courses = pd.read_csv('/home/scripts/archive/courses_provisioning.csv')
    filtered_courses = df_courses[df_courses['term_id'].isin(term_names)]
    
    for _, row in filtered_courses.iterrows():
        try:
            course = canvas.get_course(row['canvas_course_id'])
            course.update(course={'term_id': 406})
            logging.info(f"Updated course {row['canvas_course_id']} to term 406")
        except Exception as e:
            logging.error(f"Failed to update course {row['canvas_course_id']}: {e}")
    
    filtered_courses.to_csv('/home/scripts/archive/filtered_courses_cleanup.csv', index=False)

def delete_empty_terms(canvas_term_ids):
    """Deletes terms from Canvas after ensuring they are empty."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    account_id = 1  # Set the correct account ID manually
    
    for term_id in canvas_term_ids:
        try:
            courses = list(account.get_courses(enrollment_term_id=term_id))
            if not courses:
                delete_url = f"{API_URL}/api/v1/accounts/{account_id}/terms/{term_id}"
                response = requests.delete(delete_url, headers=headers)
                if response.status_code == 200:
                    logging.info(f"Successfully deleted term {term_id}")
                else:
                    logging.error(f"Failed to delete term {term_id}, Response: {response.text}")
        except Exception as e:
            logging.error(f"Error deleting term {term_id}: {e}")

def main():
    logging.info("SIS Import Automation Script for Canvas LMS started. This script filters and updates courses based on terms and provisioning files.")
    
    download_terms()
    term_names = get_terms()
    canvas_term_ids = get_canvas_term_ids()
    download_sis_export()
    process_sis_import(term_names)  # Creates SIS Import archive & uploads it
    download_courses()
    cleanup(term_names)  # Moves courses to 4JArchive
    delete_empty_terms(canvas_term_ids)
    logging.info("Completed Archive- Clear Logs")
    logging.shutdown()

if __name__ == "__main__":
    main()
