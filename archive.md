# Archival Process
## Eugene SD 4J Canvas Archival Process and Scripts ##

Canvas LMS provides instructions on how to archive courses based on Term ID from an SIS Export Report. These instructions can be found [here.](CanvasScripts/Supporting_Files/move_courses.pdf) In essence, you will need to first generate the SIS Export for all terms, the Terms report, as well as a Provisioning report with SIS Created active as a backup. 

Open the SIS Export report, filter to the courses you need. For us this is done by setting the Term to 'begin with' the current term year. I then copy all fields to a new sheet. Insert three columns after the *long-name* column. In the first of the new columns put _AcademicYear ie '_21/22'. Fill down by clicking the small square at the bottom right of the cell. In the next column concatenate the two rows, fill down. Copy those values and paste-Values in the third column. Now you can delete long-name and the first two columns and rename the third as long_name. Finally, fill down the SIS_ID for the archive term you have created. Save as CSV and upload into your BETA instance for testing as an SIS Import with "Override UI changes" and "Process as UI Changes" active. 

On your Terms.CSV change the inactive terms now to Deleted as a status and upload in the same method as above. 
You may get an error report stating a term cannot be deleted due to a course belonging to it. This is where a provisioning report can be leveraged to look for those courses. If there are many, you can use the script below to move them via the API. 

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
                                'term_id': 406  # Make sure you have the right ID from Terms report, this is archive term.
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

This script will rename the course as well by appending the correct current Term to the end. 