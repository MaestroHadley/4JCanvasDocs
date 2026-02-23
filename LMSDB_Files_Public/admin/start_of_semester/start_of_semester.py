"""Start-of-semester automation that updates grade passback settings and creates a timed Incompletes section for each course."""
#!/home/scripts/.local/pipx/shared/bin/python 
from canvasapi import Canvas
import pandas as pd
import os

API_KEYBeta = os.getenv('API_KEYBETA')
API_KEYLive = os.getenv('API_KEYLIVE')

#Be sure to change to your actual instance. 
API_URLBeta = 'https://4j.beta.instructure.com'
API_URLLive = 'https://4j.instructure.com'

#Change FILENAME HERE TO MATCH CURRENT PROJECT
report_file = '/home/scripts/admin/start_of_semester/sem_report.csv'
source_file = pd.read_csv('/home/scripts/admin/start_of_semester/all_courses.csv')
df = pd.DataFrame(source_file)

canvas = Canvas(API_URLLive, API_KEYLive)  # DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE

print("You are currently running", canvas)

def create_section(courseID):
    account = canvas.get_account(1)
    course = canvas.get_course(courseID, use_sis_id=True)
    incompletes = course.create_course_section(
        course_section={
            'name': 'Incompletes S1 25-26',
            'start_at': '2026-02-02T08:00:00Z',  # you must have the correct time/date per ZULU time.
            'end_at': '2026-04-11T06:59:00Z',
            'restrict_enrollments_to_section_dates': True
        }
    )
    record = [{
        'Course ID': courseID,
        'Section ID': incompletes,
    }]
    dfr = pd.DataFrame(record)
    dfr.to_csv(report_file, mode='a', index=False, header=False)
    print("Section created", incompletes)

# here the script continues to also activate the nightly sync for the course, while it's there anyway.
failed_courses = []

print("Auto-proceed enabled. Beginning updates...")

for index, row in df.iterrows():
    raw_courseID = row['course_id']
    courseID = str(raw_courseID)
    try:
        course = canvas.get_course(courseID, use_sis_id=True)
        update = course.update(
            course={
                'grade_passback_setting': 'nightly_sync'
            }
        )
        create_section(courseID)
    except Exception as e:
        print(f"Error updating course {courseID}: {e}")
        failed_courses.append(courseID)

if failed_courses:
    msg = "Courses that raised exceptions:\n" + "\n".join(str(course_id) for course_id in failed_courses)
    print(msg)  # still print to stdout
    with open("/home/scripts/crontab_logs.txt", "a") as logf:
        logf.write(msg + "\n")
