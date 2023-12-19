from canvasapi import Canvas
import pandas as pd
from datetime import date
today = date.today()
import os


API_KEYBeta = os.getenv('API_KEYBeta')
API_KEYLive = os.getenv('API_KEYLive')

API_URLBeta = 'https://4j.beta.instructure.com'
API_URLLive = 'https://4j.instructure.com'





#Change FILENAME HERE TO MATCHeta CURRENT PROJECT
source_file = '/Users/4JStaff/Documents/Canvas Documentation/4JCanvasDocs/CanvasScripts/Source_Files/suspend_users_source.csv'
report_file = '/Users/4JStaff/Documents/Canvas Documentation/4JCanvasDocs/CanvasScripts/Report_Files/suspended_users_report.csv'
global user
canvas = Canvas(API_URLLive, API_KEYLive)#DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE




df= pd.read_csv(source_file)

account = canvas.get_account(1)

email_list = df['emails'].values.tolist()

not_found = []

input('Press enter to continue')
print(email_list)
if input("Press enter to continue otherwise type terminate: ") == "terminate":
    exit()
for email in email_list:
    email = email.strip()
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
                user.edit(user={'event': 'suspend'})
                print ("User",user,"suspended")
                record = [{
                'firstname' : user.sortable_name.split(", ")[1],
                'lastname' : user.sortable_name.split(", ")[0],
                'username' : user.login_id,
                'date': today
                }]
                dfr = pd.DataFrame(record)
                dfr.to_csv(report_file, mode='a', index = False, header=False)
            print(email,"suspended")
            break
    if ((matching_user_id == -1 ) or (search_results_empty)):
        print("user not found", email)
        not_found.append(email)



print('File written, process complete.')
print("Users not found", not_found)