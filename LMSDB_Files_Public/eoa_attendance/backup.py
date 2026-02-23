#!/usr/bin/python3
"""Legacy backup version of the attendance report/email workflow using Canvas Data queries."""

import dblogin
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
import openpyxl
import xlsxwriter
'''
# Get settings from environment variables| Old version. 
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
'''

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
        host=dblogin.DB_HOST,
        database=dblogin.DB_NAME,
        user=dblogin.DB_USER,
        password=dblogin.DB_PASSWORD
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
            p.sis_user_id = {sis_id}
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

    # Run the query and load the data into a DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Get the current date and the day before
    now = datetime.now()
    day_before = (now - timedelta(days=1)).date()
    five_days_ago = (now - timedelta(days=5)).date()

    # Extract rows where 'No Activity' or last_active_at is older than the day before yesterday
    condition_met_df = df[
        (df['last_active_at'] == 'No Activity') | 
        (df['last_active_at'].apply(lambda x: x != 'No Activity' and datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date() <= (day_before - timedelta(days=1))))
    ]

    # Create an Excel writer using XlsxWriter
    excel_writer = pd.ExcelWriter(report_file, engine='xlsxwriter')

    # Write the DataFrame to the Excel file
    df.to_excel(excel_writer, index=False, sheet_name='Attendance Report')

    # Get the workbook and worksheet objects for further customization
    workbook = excel_writer.book
    worksheet = excel_writer.sheets['Attendance Report']

    # Define formats
    highlight_format_light_red = workbook.add_format({'bg_color': '#FFCCCC'})  # Light red for inactive
    highlight_format_dark_red = workbook.add_format({'bg_color': '#CC0000', 'font_color': 'white'})  # Dark red for 'No Activity'
    highlight_format_blue = workbook.add_format({'bg_color': '#7eb0fe'})  # Blue for enrollment within the last 5 days
    wrap_format = workbook.add_format({'text_wrap': True})  # Text wrapping for all cells

    # Iterate through the rows and apply conditional formatting
    for row in range(1, len(df) + 1):
        last_active_value = df.at[row - 1, "last_active_at"]
        enrollment_start_at = df.at[row - 1, "enrollment_start_at"]

        # Check for 'No Activity' and apply dark red highlight to the entire row
        if last_active_value == 'No Activity':
            worksheet.set_row(row, None, highlight_format_dark_red)  # Highlight 'No Activity' rows in dark red
        else:
            # Check for inactive students with a date older than the day before yesterday
            last_active_date = datetime.strptime(last_active_value, '%Y-%m-%d %H:%M:%S').date()
            if last_active_date <= day_before - timedelta(days=1):
                worksheet.set_row(row, None, highlight_format_light_red)  # Highlight rows older than the day before in light red

        # Apply blue formatting to the "sortable_name" and "enrollment_start_at" cells if the enrollment date is within the last 5 days
        if enrollment_start_at is not None:
            enrollment_start_date = datetime.strptime(enrollment_start_at, '%Y-%m-%d %H:%M:%S').date()
            if enrollment_start_date >= five_days_ago:
                # Highlight the student's name in blue
                worksheet.write(row, df.columns.get_loc('sortable_name'), df.at[row - 1, 'sortable_name'], highlight_format_blue)
                # Highlight the enrollment start date in blue
                worksheet.write(row, df.columns.get_loc('enrollment_start_at'), enrollment_start_at, highlight_format_blue)

    # Auto-adjust the width of the columns to fit the contents
    for idx, col in enumerate(df.columns):
        # Calculate the maximum width needed for the column (based on the max length of any value)
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2  # Add a little padding
        worksheet.set_column(idx, idx, max_len, wrap_format)  # Apply wrap format and set column width

    # Save the Excel file
    excel_writer.save()

    return condition_met_df




def send_email(report_file, recipient_email, extracted_data_df):
    # Calculate the previous day's date
    previous_day = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg['Subject'] = f"Student Enrollment and Activity Report for {previous_day}"

    # Compose the email body with extracted data
    body = (
        f"Please find the attached student enrollment and activity report for {recipient_email}, "
        f"covering attendance for {previous_day}. Below are the students who were inactive on {previous_day}:\n\n"
        f"In the attached file, light blue indicates students joining in the last 5 days, light red is absent, "
        f"and dark red indicates no activity or dropped. No highlight indicates present."
    )

    # Convert extracted data to HTML table if there are any rows meeting the condition
    if not extracted_data_df.empty:
        body += extracted_data_df.to_html(index=False)
    else:
        body += "No students were flagged for inactivity."

    # Attach the email body to the message
    msg.attach(MIMEText(body, 'html'))  # Send as HTML

    # Attach the XLSX file
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
        report_file = os.path.join(REPORT_DIR, f"report_{sis_id}.xlsx")

        try:
            # Run the query and generate the report for the current sis_id
            condition_met_df = run_query_and_generate_report(sis_id, report_file)
            logging.info(f"Generated report for {sis_id} ({recipient_email})")

            # Check if the report file is not empty
            if os.path.getsize(report_file) > 0:
                # Send the report via email
                send_email(report_file, recipient_email, condition_met_df)
                logging.info(f"Email sent to {recipient_email}")
            else:
                logging.warning(f"No data for {sis_id} ({recipient_email}). Generated an empty report.")
            
            # Sleep for 10 seconds between processing
            time.sleep(10)

        except Exception as e:
            logging.error(f"Error processing {sis_id} ({recipient_email}): {e}")

    logging.info("Process completed at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
