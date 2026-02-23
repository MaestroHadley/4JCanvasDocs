"""Reads course IDs from CSV, enables nightly SIS sync, and creates an Incompletes section in each Canvas course."""

from canvasapi import Canvas
import pandas as pd

API_URLBeta = 'https://4j.beta.instructure.com'
API_KEYBeta = 'add_your_canvas_beta_api_key'


API_KEYLive = 'add_your_canvas_live_api_key'
API_URLLive = 'https://4j.instructure.com'

#Change FILENAME HERE TO MATCH CURRENT PROJECT
report_file = '/Users/your_user/Documents/CanvasAPIScripts/create_section/created_sections.csv'
source_file = pd.read_csv('/Users/your_user/Documents/CanvasAPIScripts/create_section/create_section.csv')
df= pd.DataFrame(source_file)

canvas = Canvas(API_URLLive, API_KEYLive)#DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE

print("You are currently running",canvas)

def create_section(courseID):
    
    account = canvas.get_account(1)
    course = canvas.get_course(courseID)
    incompletes = course.create_course_section(
        course_section = {
            'name':'Incompletes',
            'start_at': '2024-01-31T00:00:00Z',
            'end_at': '2024-04-13T00:00:00Z',
            'restrict_enrollments_to_section_dates': True
            }
        )
    record = [{
        'Course ID': courseID,
        'Section ID': incompletes,
        }]
    dfr = pd.DataFrame(record)
    dfr.to_csv(report_file, mode ='a', index = False , header = False )
    print("Section created", incompletes)

report_file_path = '/home/your_user/pd_enroll/jobs/jobs_report.txt'
failed_courses = []
response = input("proceed?:")
if response == 'yes':
    for index, row in df.iterrows():
        courseID = row['CourseID']
        try:
            course = canvas.get_course(courseID)
            #print(course)
            update = course.update(
                course={
                    'grade_passback_setting': 'nightly_sync'
                }
            )
            create_section(courseID)
        except Exception as e:
            print(f"Error updating course {courseID}: {e}")
            failed_courses.append(courseID)
else:
    print("exited program")
    exit()

if failed_courses:
    print("Courses that raised exceptions:")
    with open(report_file_path, 'w') as report_file:
        for course_id in failed_courses:
            print(course_id)
            report_file.write(str(course_id) + '\n')
