
#!/home/scripts/.local/pipx/shared/bin/python 
"""Processes licensed staff data and mass-enrolls users into PD courses/sections in Canvas."""
#Script updated on 8/25/25 to no longer use sections, but retained logic just in case. 
#instead, all users are enrolled in root course and root section, need only to update section ids below in Mass Enrollment function. 
from datetime import datetime
print(datetime.now)
from canvasapi import Canvas
import pandas as pd
import sys
import os
import logging


#Beta Keys
API_URLBeta = 'https://4j.beta.instructure.com'

API_KEYLive = os.getenv('API_KEYLIVE')
API_URLLive = 'https://4j.instructure.com'

#Change FILENAME HERE TO MATCH CURRENT PROJECT
source_file = '/mnt/canvasreports/canvas-licensed-staff-report.csv'
report_file = '/home/scripts/admin/pd_enroll/report_file.csv'
section_file = '/home/scripts/admin/pd_enroll/sections_created.csv'

df = pd.read_csv(source_file)

canvas = Canvas(API_URLLive,API_KEYLive) #DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE
account = canvas.get_account(1)

logging.info(canvas)

#school sites for ea enrollment, list needs to be updated to match sheet
schools= {
    "Sheldon High" : 140,
    "North Eugene High" : 160,
    "South Eugene High" : 157,
    "Early College & Career Options" : 178,
    "Churchill High" : 143,
    "Cal Young Middle" : 133,
    "Arts And Technology Academy" : 163,
    "Kelly Middle" : 156,
    "Kennedy Middle" : 161,
    "Madison Middle" : 141,
    "Monroe Middle" : 158,
    "Roosevelt Middle" : 153,
    "Spencer Butte Middle": 142,
    "Adams Elementary": 137,
    "Awbrey Park Elementary": 163,
    "Buena Vista Spanish Immersion" : 146,
    "Camas Ridge Elementary": 144, 
    "Charlemagne Elementary": 2,
    "Chavez Elementary": 147,
    "Chinese Immersion Elem": 138,
    "Edgewood Elementary": 129,
    "Edison Elementary": 127,
    "Family School Elementary" : 149,
    "Fox Hollow" : 150,
    "Gilham Elementary": 139,
    "Holt Elementary": 134,
    "Howard Elementary" : 128,
    "Mccornack Elementary": 145,
    "River Road Elementary": 126,
    "Spring Creek Elementary" : 135,
    "Twin Oaks Elementary" : 132,
    "Willagillespie Elementary"  : 148,
    "Yujin Gakuen Alternative" : 130
}

school_names = []
school_names = list(schools.keys())

def section_creation(school_names):
    courseid = input("Enter course ID: ")
    account = canvas.get_account(1)
    course = canvas.get_course(courseid)
    for x in school_names:
        newSection = course.create_course_section(
            course_section = {
                'name': x ,
                
                }
            )
        record = [{
            'Section ID': newSection.id,
            'Section Name': newSection.name


        }]
        dfr = pd.DataFrame(record)
        dfr.to_csv(section_file, mode ='a', index = False , header = False )
        #create sections dictionary to pull from
   



not_found= []

def mass_enroll(user,site,sections_enroll):
    #UPDATE IDs here for course and section for PD Enrollment
    courseid = 56862
    default = 70240
    course = canvas.get_course(courseid)
    
    try :
        
        
        section_id = default 
        print(section_id, site )


    except KeyError:
        
        section_id = default
        

    print('enrolled',site, section_id,user)
    course.enroll_user(user, enrollment_type = 'StudentEnrollment', enrollment = {'enrollment_state': 'active', 'course_section_id': section_id})


   
sections_enroll = []
#input("Double check you named the columns Name and SID for the sections_created file")
s_f_df = pd.read_csv(section_file)
pd.DataFrame(s_f_df)
sections_enroll = dict(zip(s_f_df.Name, s_f_df.SID))
#print('School Enrollment List Zipped', sections_enroll)


#Finds the user in Canvas and then sends them to the mass_enroll with the correct site name as well as the correct list for section enrollment. 
def user_find(sections_enroll):
    



    for row in df.itertuples():
        firstname = row[4]
        lastname = row[3]
        username = row[1]
        site = row[6]
        email = username+'@4j.lane.edu'
        name = firstname+' '+lastname
        #print(firstname, lastname, username)
        username = str(username)
        search_results_empty = False
        search_results = account.get_users(search_term=email)
        try:
            search_results[0]
        except IndexError:
            search_results_empty = True

        matching_user_id = -1
        if (not search_results_empty):
            
            for result in search_results:

                this_user = canvas.get_user(result.id)
                if(email == this_user.email):
                    matching_user_id = this_user.id
                    user = this_user
                    mass_enroll(user,site,sections_enroll)
                    break
            
        if ((matching_user_id == -1 ) or (search_results_empty)):
            print("user not found", email)
            not_found.append(email)


    print('complete')
    print("Emails not found in Canvas",not_found)


def time_recorder():
    from datetime import datetime

    # Get the current time
    now = datetime.now()

    # Format it as a string
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode ('a')
    with open('/home/scripts/admin/pd_enroll/Pd_enroll_records.txt', 'a') as log_file:
        # Write a message to the file
        log_file.write(f'Completed at {time_string}\n')


user_find(sections_enroll)
time_recorder()
