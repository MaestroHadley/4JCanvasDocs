'''
RELEASE NOTES:
This release (5/10/23) includes updates to the search function to determine if a user is "new" or not. 
Utilizing the method from Shane it will now search by email and username and then cross-reference those IDs. 
This allows for a much more accurate return on which accounts need to be created. This also includes updates to 
allow for SSD to be enrolled into its own sub account as well for admins etc. -NSH
Update 4/1/24- Included helper function: PD_Consult to allow for easier upload of custom users to specific courses/sections as needed. 
'''
import random
from canvasapi.exceptions import CanvasException

from canvasapi import Canvas
import pandas as pd
import csv
import os


API_KEYBeta = os.getenv('API_KEYBeta')
API_KEYLive = os.getenv('API_KEYLive')

API_URLBeta = 'https://4j.beta.instructure.com'
API_URLLive = 'https://4j.instructure.com'

#Change FILENAME HERE TO MATCH CURRENT PROJECT
report_file = '/Users/4JStaff/Documents/Canvas Documentation/4JCanvasDocs/CanvasScripts/Report_Files/new_users_report.csv'
source_df=pd.read_csv('/Users/4JStaff/Documents/Canvas Documentation/4JCanvasDocs/CanvasScripts/Source_Files/new_users_source.csv')

canvas = Canvas(API_URLLive, API_KEYLive)#DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE

account = canvas.get_account(1)



#school sites for ea enrollment
schools= {
    "sheldon" : 140,
    "north" : 160,
    "south" : 157,
    "ecco" : 178,
    "eoa" : 284,
    "churchill" : 143,
    "calyoung" : 133,
    "ata" : 163,
    "kelly" : 156,
    "kennedy" : 161,
    "madison" : 141,
    "monroe" : 158,
    "roosevelt" : 153,
    "spencerbutte": 142,
    "district": 1,
    "SSD": 171
}



def new_user(lastname,name,username,jobrole,pd_course_id,pd_section_id):
    global user
    sis_id = 'staff_'+lastname
    username = str(username)
    email_domain = {
        'interpreter': 'lesd.k12.or.us',
        'pd': None,  # Set to None for username only emails
        'default': '4j.lane.edu'
    }

    if jobrole == 'pd':
        email = username
    else:
        email = username + "@" + email_domain.get(jobrole, email_domain['default'])
                 
    account = canvas.get_account(1)

    user = account.create_user(
        user={
            'name': name,
            'initial_enrollment_type' : "teacher",
            "skip_registration": True,
            'force_validations' : True,
            'enable_sis_reactivation' : True,
            'skip_registration': True,
            'sis_id' : sis_id 
        
            
        },
        communication_channel={
            
            'type':'email',
            'address':email,
            'skip_confirmation': True
            
        },
        pseudonym={
            
            'sis_user_id': sis_id,
            'send_confirmation': True,
            'unique_id': username
            
        }
        
        
    )
    
    print("User",user,"Generated")
    create_course(lastname, user)
    resource_enroll(user)

    if jobrole == "EA": ea_enroll(site,user)
    if jobrole == "ea": ea_enroll(site,user)
    if jobrole =="office": office_enroll(site,user)
    if jobrole =="district": account_admin(site,user)
    if jobrole =="principal": principal(site,user)
    if jobrole =="interpreter": ea_enroll(site,user)
    if jobrole =="pd": pd_consult(user,pd_course_id,pd_section_id)

    
    record = [{
        'First Name' : user.sortable_name.split(", ")[1],
        'Last Name' : user.sortable_name.split(", ")[0],
        'User ID' : user.login_id,
        'Job Role' : jobrole,
        'School' : site
        }]
    dfr = pd.DataFrame(record)
    dfr.to_csv(report_file, mode='a', index=False, header=False)



def create_course(lastname, user):
    account = canvas.get_account(3)
    course_name = "Sandbox_" + lastname
    sis_course_id = course_name

    try:
        newCourse = account.create_course(
            course={
                'name': course_name,
                'sis_course_id': sis_course_id,
                'is_public': False
            }
        )
        print("Course created:", newCourse)
        sandbox_enroll(newCourse, user)
    except CanvasException as e:
        if 'is already in use' in str(e):
            print(f"Course with SIS ID '{sis_course_id}' already exists.")
            # Append a random digit to the sis_course_id and retry
            sis_course_id += str(random.randint(0, 9))
            create_course_with_new_sis_id(lastname, user, sis_course_id)
        else:
            print(f"An error occurred while creating the course: {e}")

def create_course_with_new_sis_id(lastname, user, sis_course_id):
    account = canvas.get_account(1)
    course_name = "Sandbox_" + lastname

    try:
        newCourse = account.create_course(
            course={
                'name': course_name,
                'sis_course_id': sis_course_id,
                'is_public': False
            }
        )
        print("Course created with new SIS ID:", newCourse)
        sandbox_enroll(newCourse, user)
    except CanvasException as e:
        print(f"An error occurred while creating the course with a new SIS ID: {e}")


def resource_enroll(user):
    target_account = canvas.get_account(1)
    course = canvas.get_course(34255)
    sectionid = 35063
    print("Enrolling in Resource Course")
    course.enroll_user(user, enrollment_type = "StudentEnrollment", enrollment={'enrollment_state': 'active', 'course_section_id' : sectionid})
    print("Completed Resource Enrollment")

def sandbox_enroll(newCourse,user):
    target_account = canvas.get_account(1)
    course = canvas.get_course(newCourse)
    print("Enrolling in Sandbox")
    course.enroll_user(user, enrollment_type = "TeacherEnrollment", enrollment={'enrollment_state': 'active'})
    print("Completed Sandbox Enrollment")


def user_found(user,jobrole,site,pd_course_id,pd_section_id):
    if jobrole == 'interpreter':
        response = 'n'
        ea_enroll(site,user)
    else:
        response = input("User found, proceed with Job Role Assignation?")
    if response == 'n' :
        record = [{
            'firstname' : user.sortable_name.split(", ")[1],
            'lastname' : user.sortable_name.split(", ")[0],
            'username' : user.login_id,
            'roletype' : jobrole
            }]
        dfr = pd.DataFrame(record)
        dfr.to_csv(report_file, mode='a', index=False, header=False)
        print("User not assigned, recorded")
        resource_enroll(user)
    else:
        resource_enroll(user)
        if jobrole == "EA": ea_enroll(site,user)
        if jobrole == "ea": ea_enroll(site,user)
        if jobrole =="office": office_enroll(site,user)
        if jobrole =="district": account_admin(site,user)
        if jobrole =="principal": principal(site,user)
        if jobrole =="interpreter": ea_enroll(site,user)
        if jobrole =="pd": pd_consult(user,pd_course_id,pd_section_id)
        
    

    
#helper function to enroll specialty users.
def pd_consult(user,pd_course_id,pd_section_id):
    #print('Course', pd_course_id, 'Section', pd_section_id)
    course = canvas.get_course(pd_course_id)
    course.enroll_user(user, enrollment_type = "TeacherEnrollment", enrollment={'enrollment_state': 'active'})
    print('PD User enrolled at Teacher', course)






def ea_enroll(site,user):
    user_ID= user
    role = 113
    sub_acct = schools[site]
    canvas.get_account(sub_acct).create_admin(user_ID,role_id=role)
    print("User Enrolled as EA at", site)

def office_enroll(site,user):
    user_ID= user
    role = 112
    sub_acct = schools[site]
    canvas.get_account(sub_acct).create_admin(user_ID,role_id=role)
    print("User Enrolled as Office Staff")


def account_admin(site,user):
    user_ID = user
    role = 118 #districtstaff/GG
    sub_acct = schools[site]
    canvas.get_account(sub_acct).create_admin(user_ID, role_id=role)
    print("User Enrolled as District Staff")

def principal(site,user):
    user_ID = user
    role = 110 #Principal
    sub_acct = schools[site]
    canvas.get_account(sub_acct).create_admin(user_ID, role_id=role)
    print("User Enrolled as Principal Staff")
          

input("Press any key to generate new user...")







for row in source_df.itertuples():
    firstname = row[1]
    lastname = row[2]
    username = row[3]
    jobrole = row[4]
    site = row[5]
    username = str(username)
    email_domain = {
        'interpreter': 'lesd.k12.or.us',
        'pd': None,  # Set to None for username only emails
        'default': '4j.lane.edu'
    }

    if jobrole == 'pd':
        email = username
    else:
        email = username + "@" + email_domain.get(jobrole, email_domain['default'])

    name = firstname+' '+lastname
    print(firstname, lastname, username, 'email',email)

    search_results_empty = False
    search_results = account.get_users(search_term=email)
#PD Tools, enter appropriate sections for PD Consultants or special users. 
    pd_course_id = 45550
    pd_section_id = None
    try:
        search_results[0]
    except IndexError:
        search_results_empty = True

    matching_user_id = -1
    if (not search_results_empty):
        
        for result in search_results:

            this_user = canvas.get_user(result.id)
            print(this_user)
            if(email == this_user.email):
                matching_user_id = this_user.id
                user = this_user
                user_found(user,jobrole,site,pd_course_id,pd_section_id) 
                break
        
    if ((matching_user_id == -1 ) or (search_results_empty)):

        print("Creating account for "+firstname,lastname,username)
        new_user(lastname,name,username,jobrole,pd_course_id,pd_section_id)
        
print("Finished")
