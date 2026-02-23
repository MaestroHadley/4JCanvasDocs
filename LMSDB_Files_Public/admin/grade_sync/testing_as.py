#!/usr/bin/python3
"""Test harness for assignment SIS-posting sync with optional DB connectivity checks."""
from canvasapi import Canvas
import csv
import pandas as pd
import os
import psycopg2

#Version Notes: 
#Updated 4/15/24 to include clause to omit sync on assignments where 'does not count towards final grade' is marked in Canvas. -NSH
print('db name', os.getenv("DB_NAME"))
def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST")
        )
        print("Connected to database successfully!")
        return connection
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)

   



API_URLBeta = 'https://4j.beta.instructure.com'
API_KEYBeta = 'add_your_canvas_beta_api_key'

API_KEYLive = 'add_your_canvas_live_api_key'
API_URLLive = 'https://4j.instructure.com'

#Change FILENAME HERE TO MATCH CURRENT PROJECT
source_file = '/home/your_user/grade_sync/all_courses.csv'
df= pd.read_csv(source_file)
canvas = Canvas(API_URLBeta, API_KEYBeta)#DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE

account = canvas.get_account(1)


def update_assignments_post_to_sis():


    print(f"Number of rows in df: {len(df)}")

    for index, row in df.iterrows():

        raw_course_id = row["course_id"]
        course_id = str(raw_course_id)
        try:
            course = canvas.get_course(course_id,use_sis_id=True)
            print("Running Course: ", course.name)
        
            for assignment in course.get_assignments():
                # Filter for assignments based on visibility in gradebook 
                if assignment.omit_from_final_grade == True:
                    continue
                else:              
                    # Update post_to_sis if it's False
                    if not assignment.post_to_sis:  
                        assignment.edit(assignment={"post_to_sis": True})  
                    else:
                        continue

        except Exception as e:
            print(f"Error processing course ID {course_id}: {e}")



def time_recorder():
    from datetime import datetime

    # Get the current time
    now = datetime.now()

    # Format it as a string
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode ('a')
    with open('/home/your_user/grade_sync/grade_sync_report.txt', 'a') as log_file:
        # Write a message to the file
        log_file.write(f'Completed at {time_string}\n')



get_db_connection()
#time_recorder()
#update_assignments_post_to_sis()
