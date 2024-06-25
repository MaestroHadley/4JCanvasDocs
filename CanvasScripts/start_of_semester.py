'''
This file will read a spreadsheet of course IDs from the provisioning report,
filtered to this term/semester. Reach into Canvas, activate the nightly sync
and also add an Incompletes section with proper dates. Remember to convert
the date/time from PST to Zulu Military time. 
'''

from canvasapi import Canvas
import pandas as pd
import os

API_KEYBeta = os.getenv('API_KEYBeta')
API_KEYLive = os.getenv('API_KEYLive')

#Be sure to change to your actual instance. 
API_URLBeta = 'https://4j.beta.instructure.com'
API_URLLive = 'https://4j.instructure.com'



#Change FILENAME HERE TO MATCH CURRENT PROJECT
report_file = '/Users/4JStaff/Documents/CanvasAPIScripts/create_section/created_sections.csv'
source_file = pd.read_csv('/Users/4JStaff/Documents/CanvasAPIScripts/create_section/create_section.csv')
df= pd.DataFrame(source_file)

canvas = Canvas(API_URLLive, API_KEYLive)#DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE

print("You are currently running",canvas)

def create_section(courseID):
    
    account = canvas.get_account(1)
    course = canvas.get_course(courseID)
    incompletes = course.create_course_section(
        course_section = {
            'name':'Incompletes',
            'start_at': '2024-06-15T00:00:00Z', #you must have the correct time/date per ZULU time. 
            'end_at': '2024-11-09T00:00:00Z',
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

#here the script continues to also activate the nightly sync for the course, while it's there anyway.  
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
    for course_id in failed_courses:
        print(course_id)
