# Synergy Grade Passback # 

## Summary ##
The connection between Canvas and Synergy is driven by the SIS Import that happens each night between 10pm-11pm. During the import, a collection of files from Synergy are imported to Canvas, including students, teachers, courses (sections), and other updates. Once the import is complete, Canvas issues a push command to Synergy via it's backbone process called, Kimono (rebranded to *Elevate Data Sync*). Elevate Data Sync helps synchronize data between LMS platforms and other sources via the OneRoster protocol. In our instance, Synergy accepts inbound information via this process in the form of grades and assignments. 

Synergy will accept four data points from Canvas as inbound information: 
- Assignment Title
- Total points for the assignment
- Due date for the assignment
- Current score for the student on the assignment
 
In order to **sync** from Canvas to Synergy the following requirements must be met: 
- The assignement has: a title, due-date, and point value. 
- The due-date has passed for the assignment. 
- At least one student in an active section has *received a score* on the assignment. 
- The "Sync to Synergy" option is active for the assignment. [More on this later]. 

---
## Implementation ##
At this time if a teacher is using one grading category (Assignments), and the above criteria are met, an assignment will automatically sync to Synergy without any interference on the teacher's part. 

If a teacher is using differentiated categories and/or weighted categories, extra setup is required. The teacher will need to establish those categories in Canvas, enable the weights, and then in Synergy mirror those weights on the chosen Assignment Types under the Gradebook Setup sub-menu. In Canvas, they will then need to establish the 'Sync SIS Categories' option on the Assignments tab in their course(s) under the 3-dot menu. Utilizing the drop-dowm menu for each grading category, they are able to select the corresponding Synergy Assignment Type that they selected, note that custom values are found at the bottom of the list.

**Admin Setup**

Once teachers have cross-listed their courses, navigate to reports at the root account. Generate a Provisioning report set to Courses.csv. Open the file and filter down to the current term(s) and `published_by_SIS = True`. Delete all columns aside from `Canvas_Course_Id` and rename it to `CourseID`. Save the file. You may want to encapsulte the follwoing script in another function etc, but this will activate the Nightly Sync for the entirety of the courses. Unfortunately, though our templates have this active, it does not blueprint to the end-courses, therefore we have the process outlined in the [Start of Semester](Start_of_Sem.md) documentation. That process is to be run at the beginning of each semester as outlined above. 
