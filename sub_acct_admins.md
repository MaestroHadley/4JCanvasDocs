# Canvas Sub-Account Admin Updates and Procedures #

## Summary ##
This process allows a *Root Admin* user to update building or sub-account admins en masse. This process can be lengthy and difficult, so the following scripts were developed to help root admin in their yearly tasks for maintenance. 

## Key Features ##
- Search Admins by sub-account
    - Print them to a CSV by site name
- Create new admin users
    - Add them to specific sites with specific roles
- Look up roles and return IDs to use in your own script
- Remove Admins from sub-accounts
- Use an excel workbook with sheets per sub-account for easy management

As an educational institution for K12 schools, naturally our implementation is rather specific. You'll note in the code specific use-cases or splicing of names etc of the spreadsheet, this is to match our schools and naming conventions. You'll need to modify for your uses. 
## Code Block ##


    from canvasapi import Canvas
    import sys
    sys.path.append('this is used to import other functions noted below')
    import pandas as pd
    from key_functions.resource_enroll import resource_enroll, sections_enroll
    import os

    API_KEYBeta = os.getenv('API_KEYBeta')
    API_KEYLive = os.getenv('API_KEYLive')

    #Be sure to change to your actual instance. 
    API_URLBeta = 
    API_URLLive = 

    report_file= 'Path to your file'

    canvas = Canvas(API_URLLive, API_KEYLive)

    #School definitions- add your own. 
    schools= {
        "SubAccount 1": keyvalue,
        "SubAccount 2": keyvalue,
        etc. 

    }

    def canvas_user_search(email):
        account = canvas.get_account(1)
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
                    user = this_user #assigns user to user_ID
                    #USER HAS BEEN FOUND DO THIS THING
                    return user
                    break
            
        if ((matching_user_id == -1 ) or (search_results_empty)):
            user = None
            return user



    role_list= {}

    def Get_Role_ID():
        #Will print all the associated acct admin types and id for Add_Admin_to_Sub():
        roles = canvas.get_account(1).get_roles()
        for role in roles:
            role_list[role.label] = role.id
        print(role_list)




    def remove_admins():
        for site in schools:
            print(site)

            account = canvas.get_account(schools[site])
            admins = account.get_admins()

            admin_list = []
            for admin in admins:
                user = canvas.get_user(admin.user['id'])
                email = user.email
                admin_list.append({
                    'Admin ID': admin.id,
                    'User ID': admin.user['id'],
                    'User' : admin.user['name'],
                    'Email': email,
                    'Site': site
                })

                role_id = admin.role_id
                if role_id == 110:
                    continue
                else:
                    account.delete_admin(user, role_id=admin.role_id)
                    print("Deleted", user, "from", site)

            df = pd.DataFrame(admin_list)
            df.to_csv(report_file, mode='a', index=False, header=True)



    def new_user(name,site, email, account, roleID):
        firstname, lastname = name.split()
        
        username = email.split('@')[0]
        
        
        user = account.create_user(
            user={
                'name': name,
                'initial_enrollment_type' : "teacher",
                "skip_registration": True,
                'force_validations' : True,
                'enable_sis_reactivation' : True,
                'skip_registration': True,
                'sis_id' : 'staff_'+lastname #Need to determine a random generator. 
            
                
            },
            communication_channel={
                
                'type':'email',
                'address':email,
                'skip_confirmation': True
                
            },
            pseudonym={
                
                'sis_user_id': username,
                'send_confirmation': True,
                'unique_id': username
                
            }
            
            
        )
        
        print("User",user,"Generated")
        user = canvas.get_user(user)
        account.create_admin(user, role_id=roleID)
        print("admin created", user,site, roleID)
        resource_enroll(user,site,sections_enroll) # We have a specific course that is used for training and PD all users are enrolled into it. 
        return user



    def find_site_by_name(schools, site_name_part):
        site_name_part = site_name_part.lower()  # Convert to lowercase for case-insensitive matching
        for site in schools:
            if site_name_part in site.lower():
                return site
        return None


    def add_adminsV2(schools):
        excel_file_path = '/Users/4JStaff/Downloads/admins.xlsx'
        xls = pd.ExcelFile(excel_file_path)
        for sheet_name in xls.sheet_names:

            source = pd.read_excel(xls, sheet_name=sheet_name)
            for index,row in source.iterrows(): 
                site_name_part = sheet_name[:-7]
                site = find_site_by_name(schools, site_name_part)
                print(site)
                name = row['Name']
                if pd.isna(name) or name.strip() == '':
                    break
                role_name = row['ROLE:']
                email = row['Email Address'].strip().lower()
                #email=email.strip()
                account = canvas.get_account(schools[site])
                # Determine the role ID based on the role name
                if role_name == 'Principal' or role_name == 'Assis Principal':
                    role = 110
                elif role_name == 'EA or GradeGuardian' or role_name == 'Specialist':
                    role = 113
                elif role_name == 'Office Staff':
                    role = 112
                else:
                    role = 113
                user = canvas_user_search(email)
                if user is None:
                    print(f"User {email} not found. Generating...")
                    new_user(name,site, email, account, role)

                    continue
                account.create_admin(user, role_id=role) #pickup if user is found. 
                resource_enroll(user,site,sections_enroll)
                print("admin created", user, role)

    #Call functions as you need to. 




## Sample Sheets ##

### New Users ###
| First Name | Last Name | JobRole | Location |
