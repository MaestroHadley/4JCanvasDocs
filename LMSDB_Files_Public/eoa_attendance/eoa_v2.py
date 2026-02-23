#!/home/scripts/.local/pipx/shared/bin/python 
"""Enhanced attendance-report pipeline that queries Canvas Data, writes Excel reports, and sends email notifications."""

import dblogin
import os
import psycopg2
import pandas as pd
import ssl
import smtplib
import time
from pytz import timezone
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import openpyxl
import xlsxwriter

# Constants for email and file paths
EMAIL_SENDER = "redacted_email@example.com"
SMTP_SERVER = 'smtp.4j.lane.edu'
SMTP_PORT = int(os.getenv("SMTP_PORT", 25))  # Default to 25 if not set
COMPANION_FILE = "/home/scripts/eoa_attendance/eoa_sis.CSV"
REPORT_DIR = "/home/scripts/eoa_attendance/reports/"
LOG_FILE = "/home/scripts/eoa_attendance/report_generation.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def run_query_and_generate_report(sis_id, report_file):
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
            AND c.sis_source_id LIKE '2026%'
    ),
    student_last_active AS (
        SELECT
            u.sortable_name,
            sec.section_name,
            sec.course_name,
            COALESCE(sec.original_building_name, sec.building_name) AS original_building_name,
            e.course_section_id,
            e.user_id,
            e.last_activity_at,
            e.created_at AS enrollment_start_at
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
        COALESCE(TO_CHAR(sl.last_activity_at, 'YYYY-MM-DD HH24:MI:SS'), 'No Activity') AS last_active_at,
        TO_CHAR(sl.enrollment_start_at, 'YYYY-MM-DD HH24:MI:SS') AS enrollment_start_at
    FROM
        student_last_active sl
    ORDER BY
        sl.section_name, sl.sortable_name ASC;
    """

    # Execute the query and load data into a DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Convert timestamps from UTC to PST
    pst_tz = timezone('America/Los_Angeles')
    df['last_active_at'] = df['last_active_at'].apply(
        lambda x: "No Activity" if x == "No Activity" else 
                  datetime.strptime(x, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone('UTC')).astimezone(pst_tz).strftime('%Y-%m-%d %H:%M:%S')
    )
    df['enrollment_start_at'] = df['enrollment_start_at'].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone('UTC')).astimezone(pst_tz).strftime('%Y-%m-%d %H:%M:%S')
    )

    # Set up dates for conditional formatting
    now = datetime.now(pst_tz)
    day_before = (now - timedelta(days=1)).date()
    five_days_ago = (now - timedelta(days=5)).date()

    # Generate Excel report with conditional formatting
    excel_writer = pd.ExcelWriter(report_file, engine='xlsxwriter')
    df.to_excel(excel_writer, index=False, sheet_name='Attendance Report')
    workbook = excel_writer.book
    worksheet = excel_writer.sheets['Attendance Report']
    
    # Define formats
    highlight_format_light_red = workbook.add_format({'bg_color': '#FFCCCC'})  # Light red for inactive
    highlight_format_dark_red = workbook.add_format({'bg_color': '#CC0000', 'font_color': 'white'})  # Dark red for 'No Activity'
    highlight_format_blue = workbook.add_format({'bg_color': '#7eb0fe'})  # Blue for recent enrollments
    wrap_format = workbook.add_format({'text_wrap': True})  # Text wrapping for all cells

    # Apply conditional formatting based on activity status and enrollment date
    for row in range(1, len(df) + 1):
        last_active_value = df.at[row - 1, "last_active_at"]
        enrollment_start_at = df.at[row - 1, "enrollment_start_at"]

        # Apply dark red for 'No Activity'
        if last_active_value == "No Activity":
            worksheet.set_row(row, None, highlight_format_dark_red)
        else:
            # Apply light red for inactivity older than a day
            last_active_date = datetime.strptime(last_active_value, '%Y-%m-%d %H:%M:%S').date()
            if last_active_date <= day_before - timedelta(days=1):
                worksheet.set_row(row, None, highlight_format_light_red)

        # Apply blue formatting for recent enrollments within the last 5 days
        if enrollment_start_at is not None:
            enrollment_start_date = datetime.strptime(enrollment_start_at, '%Y-%m-%d %H:%M:%S').date()
            if enrollment_start_date >= five_days_ago:
                worksheet.write(row, df.columns.get_loc('sortable_name'), df.at[row - 1, 'sortable_name'], highlight_format_blue)
                worksheet.write(row, df.columns.get_loc('enrollment_start_at'), enrollment_start_at, highlight_format_blue)

    # Auto-adjust column widths with wrap format
    for idx, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2  # Add padding
        worksheet.set_column(idx, idx, max_len, wrap_format)

    # Save the Excel file
    excel_writer.close()

    return df

def send_email(report_file, recipient_emails, extracted_data_df):
    if isinstance(recipient_emails, str):
        recipient_emails = [recipient_emails]

    previous_day = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = ", ".join(recipient_emails)
    msg['Subject'] = f"Student Enrollment and Activity Report for {previous_day}"

    body = (
        f"Please find the attached student enrollment and activity report for {previous_day}.\n\n"
        "In the attached file, light blue indicates students joining in the last 5 days, and light red is absent. "
    )
    body += extracted_data_df.to_html(index=False) if not extracted_data_df.empty else "No students were flagged for inactivity."
    msg.attach(MIMEText(body, 'html'))

    with open(report_file, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(report_file)}')
        msg.attach(part)

    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT:@SECLEVEL=1")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.sendmail(EMAIL_SENDER, recipient_emails, msg.as_string())
            logging.info(f"Email sent to: {', '.join(recipient_emails)}")
    except Exception as e:
        logging.error(f"Failed to send email to {', '.join(recipient_emails)}: {e}")

if __name__ == "__main__":
    teachers = pd.read_csv(COMPANION_FILE)
    all_data_df = pd.DataFrame()

    for _, row in teachers.iterrows():
        sis_id = row['sis_id']
        recipient_email =  row['email']
        report_file = os.path.join(REPORT_DIR, f"report_{sis_id}.xlsx")

        try:
            report_df = run_query_and_generate_report(sis_id, report_file)
            logging.info(f"Generated report for {sis_id} ({recipient_email})")

            if not report_df.empty:
                report_df.insert(0, 'Teacher Email', recipient_email)
                all_data_df = pd.concat([all_data_df, report_df], ignore_index=True)
                send_email(report_file, recipient_email, report_df)
                logging.info(f"Email sent to {recipient_email}")
            else:
                logging.warning(f"No data for {sis_id} ({recipient_email}). Generated an empty report.")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Error processing {sis_id} ({recipient_email}): {e}")

    if not all_data_df.empty:
        large_report_file = os.path.join(REPORT_DIR, "full_attendance_report.xlsx")
        excel_writer = pd.ExcelWriter(large_report_file, engine='xlsxwriter')
        all_data_df.to_excel(excel_writer, index=False, sheet_name='Full Attendance Report')
        workbook = excel_writer.book
        worksheet = excel_writer.sheets['Full Attendance Report']

        # Define formats for different activity statuses
        highlight_format_light_red = workbook.add_format({'bg_color': '#FFCCCC'})  # Light red for general inactivity
        highlight_format_dark_red = workbook.add_format({'bg_color': '#CC0000', 'font_color': 'white'})  # Dark red for 'No Activity'
        highlight_format_blue = workbook.add_format({'bg_color': '#7eb0fe'})  # Blue for recent enrollments
        wrap_format = workbook.add_format({'text_wrap': True})  # Wrapping format for all cells

        # Set dates for conditional formatting
        now = datetime.now()
        day_before = (now - timedelta(days=1)).date()
        five_days_ago = (now - timedelta(days=5)).date()

        # Apply conditional formatting for "No Activity" and enrollment
        for row in range(1, len(all_data_df) + 1):
            last_active_value = all_data_df.at[row - 1, "last_active_at"]
            enrollment_start_at = all_data_df.at[row - 1, "enrollment_start_at"]

            # Apply dark red format for 'No Activity' rows
            if last_active_value == "No Activity":
                worksheet.set_row(row, None, highlight_format_dark_red)
            elif last_active_value and datetime.strptime(last_active_value, '%Y-%m-%d %H:%M:%S').date() <= day_before - timedelta(days=1):
                # Apply light red for general inactivity older than a day
                worksheet.set_row(row, None, highlight_format_light_red)

            # Apply blue formatting for recent enrollments within the last 5 days
            if enrollment_start_at:
                enrollment_start_date = datetime.strptime(enrollment_start_at, '%Y-%m-%d %H:%M:%S').date()
                if enrollment_start_date >= five_days_ago:
                    worksheet.write(row, all_data_df.columns.get_loc('sortable_name'), all_data_df.at[row - 1, 'sortable_name'], highlight_format_blue)
                    worksheet.write(row, all_data_df.columns.get_loc('enrollment_start_at'), enrollment_start_at, highlight_format_blue)

        # Auto-adjust column widths and apply wrapping
        for idx, col in enumerate(all_data_df.columns):
            max_len = max(all_data_df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(idx, idx, max_len, wrap_format)

        excel_writer.close()
        logging.info(f"Larger attendance report saved as {large_report_file}")

        # Send the larger report via email for testing
        try:
            recipients_list = ["redacted_email@example.com", "redacted_email@example.com, redacted_email@example.com","redacted_email@example.com", "redacted_email@example.com", "redacted_email@example.com", "redacted_email@example.com", "redacted_email@example.com"]  # For testing purposes
            send_email(large_report_file, recipients_list, all_data_df)
            logging.info("Larger attendance report emailed.")
        except Exception as e:
            logging.error(f"Failed to send the larger report: {e}")
