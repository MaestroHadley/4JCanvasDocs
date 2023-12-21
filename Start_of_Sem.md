# Start of Semester Documentation #
## Summary ##
At the beginning of each semester or grading period you'll need to implement the following- 


Once teachers have cross-listed their courses, navigate to reports at the root account. Generate a Provisioning report set to Courses.csv. Open the file and filter down to the current term(s) and `published_by_SIS = True`. Delete all columns aside from `Canvas_Course_Id` and rename it to `CourseID`. Save the file. You may want to encapsulte the follwoing script in another function etc, but this will activate the Nightly Sync for the entirety of the courses. Unfortunately, though our templates have this active, it does not blueprint to the end-courses. You will then run the [Start of Sememster](Start_of_Sem.py) Python script. 

The script will reach into Canvas and performs two functions, it will create a new section called `Incompletes` for which you will need to obtain a start and end date/time in Zulu time. I recommend using timeanddate.com, it's rather straight forward and you can set it to your current location to translate the time and date to Zulu format. Secondly, it will also activate the internal switch for the course's `Nightly Sync` for the grade passback. While there is a larger Nightly Sync that happens from the Canvas Admin side in the SIS Import, I have found from experience this ensures that *all* courses actually sync. 

---
# PD Information # 
TBD> 
