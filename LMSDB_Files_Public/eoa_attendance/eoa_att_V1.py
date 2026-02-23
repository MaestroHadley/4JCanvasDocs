"""Generates per-staff attendance reports from Canvas Data (PostgreSQL) and emails each report."""

import os
import psycopg2
import pandas as pd
import ssl
import smtplib
import time
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Get settings from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")

EMAIL_SENDER = "redacted_email@example.com"
SMTP_SERVER = 'smtp.4j.lane.edu'
SMTP_PORT = int(os.getenv("SMTP_PORT", 25))  # Default to 587 if not set

# File paths for the reports
COMPANION_FILE = "/home/scripts/eoa_attendance/companion.csv"  # File containing the sis_id values
REPORT_DIR = "/home/scripts/eoa_attendance/reports/"  # Directory to store individual reports
LOG_FILE = "/home/scripts/eoa_attendance/report_generation.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def run_query_and_generate_report(sis_id, report_file):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    # Define the query with the sis_id passed
    query = f"""
      WITH teacher_sections AS (
        SELECT
            sec.id AS section_id,
            sec.name AS section_name,
            c.id AS course_id,
            c.name AS course_name,
            acc.name AS building_name,
            orig_acc.name AS original_building_name
        FROM
            canvas.enrollments e
        JOIN
            canvas.course_sections sec ON e.course_section_id = sec.id
        JOIN
            canvas.courses c ON sec.course_id = c.id
        JOIN
            canvas.pseudonyms p ON e.user_id = p.user_id
        JOIN
            canvas.accounts acc ON c.account_id = acc.id
        LEFT JOIN
            canvas.courses orig_c ON sec.nonxlist_course_id = orig_c.id
        LEFT JOIN
            canvas.accounts orig_acc ON orig_c.account_id = orig_acc.id
        WHERE
            p.sis_user_id = '{sis_id}'
            AND e.type = 'TeacherEnrollment'
            AND c.workflow_state = 'available'
            AND c.sis_source_id IS NOT NULL
            AND c.sis_source_id LIKE '2025%'
    ),
    student_last_active AS (
        SELECT
            u.sortable_name,
            sec.section_name,
            sec.course_name,
            COALESCE(sec.original_building_name, sec.building_name) AS original_building_name,
            e.course_section_id,
            e.user_id,
            TO_CHAR(e.last_activity_at, 'YYYY-MM-DD HH24:MI:SS') AS last_activity_formatted,
            TO_CHAR(e.created_at, 'YYYY-MM-DD HH24:MI:SS') AS enrollment_start_at
        FROM
            canvas.enrollments e
        JOIN
            canvas.users u ON e.user_id = u.id
        JOIN
            teacher_sections sec ON e.course_section_id = sec.section_id
        WHERE
            e.type = 'StudentEnrollment'
    )
    SELECT
        sl.sortable_name,
        sl.section_name,
        sl.course_name,
        sl.original_building_name,
        CASE
            WHEN sl.last_activity_formatted IS NULL THEN 'No Activity'
            ELSE sl.last_activity_formatted
        END AS last_active_at,
        sl.enrollment_start_at
    FROM
        student_last_active sl
    ORDER BY
        sl.section_name, sl.sortable_name ASC;
    """

    # Run the query and export to CSV
    df = pd.read_sql_query(query, conn)
    df.to_csv(report_file, index=False, header=True)
    conn.close()

def send_email(report_file, recipient_email):
    # Calculate the previous day's date
    previous_day = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg['Subject'] = f"Student Enrollment and Activity Report for {previous_day}"
    
    # Compose the email body
    body = (
        f"Please find the attached student enrollment and activity report for {recipient_email}, "
        f"covering attendance for {previous_day}. "
        "Please note that this email is sent early in the morning, but the report refers to the day prior. "
        "For example, if you receive this email on a Saturday, it will refer to Friday's attendance. "
        "If you receive this on a Tuesday, it will refer to Monday's attendance. "
        "The window cuts off at midnight for participation. Please do not reply to this email "
        "as it is unmonitored."
    )
    
    # Attach the email body to the message
    msg.attach(MIMEText(body, 'plain'))

    # Attach the CSV file
    with open(report_file, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(report_file)}')
        msg.attach(part)

    # Create a custom SSL context
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT:@SECLEVEL=1")

    # Send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())

if __name__ == "__main__":
    # Read the companion file with the sis_ids
    teachers = pd.read_csv(COMPANION_FILE)

    # Loop through each teacher and generate a report, then send an email
    for index, row in teachers.iterrows():
        sis_id = row['sis_id']
        recipient_email = 'redacted_email@example.com' # row['email']  # Assuming there's an 'email' column in the companion file

        # Generate the report file path
        report_file = os.path.join(REPORT_DIR, f"report_{sis_id}.csv")

        try:
            # Run the query and generate the report for the current sis_id
            run_query_and_generate_report(sis_id, report_file)
            logging.info(f"Generated report for {sis_id} ({recipient_email})")

            # Check if the report file is not empty
            if os.path.getsize(report_file) > 0:
                # Send the report via email
                send_email(report_file, recipient_email)
                logging.info(f"Email sent to {recipient_email}")
            else:
                logging.warning(f"No data for {sis_id} ({recipient_email}). Generated an empty report.")
            
            # Sleep for 10 seconds between processing
            time.sleep(10)

        except Exception as e:
            logging.error(f"Error processing {sis_id} ({recipient_email}): {e}")

    logging.info("Process completed at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
