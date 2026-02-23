#!/home/scripts/.local/pipx/shared/bin/python 
"""Ensures Canvas assignments are set to post_to_sis=True across a course list, skipping omitted assignments."""
from canvasapi import Canvas
from datetime import datetime
import pandas as pd
import os


#Version Notes: 
#Updated 4/15/24 to include clause to omit sync on assignments where 'does not count towards final grade' is marked in Canvas. -NSH

API_URLBeta = 'https://4j.beta.instructure.com'


API_KEYLive = os.getenv('API_KEYLIVE')
API_URLLive = 'https://4j.instructure.com'

#Change FILENAME HERE TO MATCH CURRENT PROJECT
source_file = '/home/scripts/admin/grade_sync/all_courses.csv'
df= pd.read_csv(source_file)
canvas = Canvas(API_URLLive, API_KEYLive)#DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE

account = canvas.get_account(1)

def update_assignments_post_to_sis():
    course_count = 0  # Initialize counter for courses

    print(f"Number of rows in df: {len(df)}")

    for index, row in df.iterrows():
        raw_course_id = row["course_id"]
        course_id = str(raw_course_id)
        try:
            course = canvas.get_course(course_id, use_sis_id=True)
            course_count += 1  # Increment course count for each course processed
            
            # Iterate through assignments in the course
            for assignment in course.get_assignments():
                # Skip assignments omitted from the final grade
                if assignment.omit_from_final_grade:
                    continue
                
                # Update post_to_sis if False
                if not assignment.post_to_sis:
                    assignment.edit(assignment={"post_to_sis": True})

        except Exception as e:
            error_message = str(e)
            # Ignore "due_at" error, log all other errors
            if "cannot be blank when Post to Sis is checked" not in error_message:
                print(f"Error processing course ID {course_id}: {e}")

    print(f"Total courses processed: {course_count}")
    return course_count

def time_recorder(course_count):
    # Get the current time
    now = datetime.now()
    # Format it as a string
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Log completion time and course count to the report file
    with open('/home/scripts/admin/grade_sync/grade_sync_report.txt', 'a') as log_file:
        log_file.write(f'Completed at {time_string}. Total courses processed: {course_count}\n')

# Run the functions
course_count = update_assignments_post_to_sis()
time_recorder(course_count)
