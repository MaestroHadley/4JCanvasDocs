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

## Teacher Enrollment Archive ##

After more than 4 years of Canvas usage in our district, it's apparent we needed a way to offload teacher course enrollments from previous years. Teachers were experiencing large and confusing lists of past courses when attempting to import content year to year. Leveraging Canvas Data 2, I was able to create an SIS Import to *inactivate* those enrollments for teachers. 

By inactivating the enrollment, the course stays in the teacher's account but is hidden from their view and can be restored at any time by an account admin. 

For information on setting up Canvas Data 2 see [here.](canvas_data_2.md)

Create a new View in your CD2 Database with the following: 

    SELECT courses.sis_source_id  AS course_id,
        pseudonyms.sis_user_id AS user_id,
        enrollments.role_id,
        sections.sis_source_id AS section_id
    FROM canvas.pseudonyms pseudonyms
            JOIN canvas.enrollments enrollments ON pseudonyms.user_id = enrollments.user_id
            JOIN canvas.courses courses ON enrollments.course_id = courses.id
            JOIN canvas.course_sections sections ON enrollments.course_section_id = sections.id
    WHERE pseudonyms.sis_user_id::text ~~ 'staff_%'::text
    AND (pseudonyms.user_id IN (SELECT pseudonyms_1.user_id
                                FROM canvas.pseudonyms pseudonyms_1
                                WHERE pseudonyms_1.sis_user_id::text ~~ 'staff_%'::text))
    AND (enrollments.workflow_state::text ~~ 'active'::text OR enrollments.workflow_state::text ~~ 'completed'::text)
    AND courses.sis_source_id IS NOT NULL
    AND enrollments.role_id::text ~~ '4'::text
    AND (courses.sis_source_id::text ~~ '2020_%'::text OR courses.sis_source_id::text ~~ '2021_%'::text OR
        courses.sis_source_id::text ~~ '2022_%'::text)
    ORDER BY pseudonyms.user_id, courses.sis_source_id, sections.sis_source_id

**Note** that our identifier for all staff in Canvas is in their SIS_ID which begins with "Staff_". You may need to use a different identifier. Additionally, our courses are transported from Synergy SIS with the current year's academic ending year appended to the front, ie 2021 is the 2020/2021 academic year. 

## Reactivate Courses ## 

In the event that a teacher would like to have their courses restored to them, the easiest way to do so is by using the function below which will pull all inactive courses for a teacher, we can then funnel down based on sis_id or other factor, and re-import it to Canvas via SIS Import. 

    CREATE OR REPLACE FUNCTION get_inactives(input_user_id TEXT)
    RETURNS TABLE(
        course_id TEXT,
        user_id TEXT,
        role_id TEXT,
        section_id TEXT,
        status TEXT
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT courses.sis_source_id::text AS course_id,
            pseudonyms.sis_user_id::text AS user_id,
            enrollments.role_id::text,
            sections.sis_source_id::text AS section_id,
            enrollments.workflow_state::text AS status
        FROM canvas.pseudonyms pseudonyms
        JOIN canvas.enrollments enrollments ON pseudonyms.user_id = enrollments.user_id
        JOIN canvas.courses courses ON enrollments.course_id = courses.id
        JOIN canvas.course_sections sections ON enrollments.course_section_id = sections.id
        WHERE pseudonyms.user_id::text = input_user_id
        AND (pseudonyms.user_id IN (SELECT pseudonyms_1.user_id
                                    FROM canvas.pseudonyms pseudonyms_1
                                    WHERE pseudonyms_1.sis_user_id::text LIKE 'staff_%'))
        AND (enrollments.workflow_state::text LIKE 'inactive'
            OR enrollments.workflow_state::text LIKE 'completed')
        AND courses.sis_source_id IS NOT NULL
        AND pseudonyms.sis_user_id IS NOT NULL
        AND enrollments.role_id::text LIKE '4'
        ORDER BY pseudonyms.user_id, courses.sis_source_id, sections.sis_source_id;
    END $$ LANGUAGE plpgsql;

## Call as ##
    -- Replace '2228' with the actual user_id you want to filter by
    SELECT * FROM get_inactives('2228');


You can also use the function below to get a more wholistic list based of Canvas User ID. 

    SELECT courses.sis_source_id  AS course_id,
        pseudonyms.sis_user_id AS user_id,
        enrollments.role_id,
        sections.sis_source_id AS section_id,
        enrollments.workflow_state AS status
    FROM canvas.pseudonyms pseudonyms
            JOIN canvas.enrollments enrollments ON pseudonyms.user_id = enrollments.user_id
            JOIN canvas.courses courses ON enrollments.course_id = courses.id
            JOIN canvas.course_sections sections ON enrollments.course_section_id = sections.id
    WHERE pseudonyms.user_id::text ~~ '#CANVASUSERID'::text
    AND (pseudonyms.user_id IN (SELECT pseudonyms_1.user_id
                                FROM canvas.pseudonyms pseudonyms_1
                                WHERE pseudonyms_1.sis_user_id::text ~~ 'staff_%'::text))
    AND (enrollments.workflow_state::text ~~ 'inactive'::text OR enrollments.workflow_state::text ~~ 'completed'::text)
    AND courses.sis_source_id IS NOT NULL
    AND pseudonyms.sis_user_id IS NOT NULL
    AND enrollments.role_id::text ~~ '4'::text

    ORDER BY pseudonyms.user_id, courses.sis_source_id, sections.sis_source_id