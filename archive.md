# Archival Process
## Eugene SD 4J Canvas Archival Process and Scripts ##


While Canvas does provide instructions on how to do this via an SIS Import, often times that SIS import may miss courses, for whatever reason. 

Therefore, a script has been developed to scrape through Canvas and correct based off current terms. 
First you need to run the Admin>Terms report so you can identify the correct Term codes you want to utilize for the Archive as well as which Term Codes to cmd+f Replace with the Archive Term Code. 

Hone the CSV down to a singular column by course_ids, this is done by filtering a provisioning report by `Created by SIS=True` and the current `term_id`.   


### Code Snip ##
**Be sure to include imports and canvas tokens**

    #Change FILENAME HERE TO MATCH CURRENT PROJECT
    source_file = '/Users/4JStaff/Documents/CanvasAPIScripts/archive/to_archive.csv'
    df= pd.read_csv(source_file)
    #canvas = Canvas(API_URLBeta, API_KEYBeta)#DOUBLE CHECK YOUR KEYS TO BETA OR LIVE FOR USE-CASE


    class CanvasCourseUpdater:
        def __init__(self, api_url, api_key, source_file):
            self.canvas = Canvas(api_url, api_key)
            self.account = self.canvas.get_account(1)
            self.df = pd.read_csv(source_file)

        def update_courses(self):
            print("Updating Courses...")
            count = 0
            for index, row in self.df.iterrows():
                try:
                    course = self.canvas.get_course(row['course_id'])
                    if course.enrollment_term_id != 406:  # Only update the course if necessary: Archive term. 
                        term_object = self.account.get_enrollment_term(course.enrollment_term_id)
                        term_splice = term_object.name[0:4]
                        course.update(
                            course={
                                'name': course.name + '_' + term_splice,
                                'term_id': 406  # Make sure you have the right ID from prov. report, this is archive term.
                            }
                        )
                        count += 1
                        if count % 100 == 0:  # Print progress every 100 courses
                            print(f"Updated {count} courses")
                except Exception as e:
                    print(f"Failed to update course {row['course_id']}: {str(e)}")
            print("Process complete")

    # Use the class:
    updater = CanvasCourseUpdater(API_URLLive, API_KEYLive, '/Users/4JStaff/Documents/CanvasAPIScripts/archive/to_archive.csv')
    updater.update_courses()

This script will rename the course as well by appending the correct current Term to the end. This was used in our mass archival process so we could archive 3 years at one time. I had decided to do this rather than using the SIS Import option to move over the courses because we needed to append the year from the *various* terms. Now that courses belong to a singular term, I may move to utilizing the SIS Import option. 

[More info can be found here](CanvasScripts/Supporting_Files/move_courses.pdf)