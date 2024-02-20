
function onFormSubmit(e) {

    // READ FORM RESPONSES
    var formResponse = e.response;
    var email = formResponse.getRespondentEmail();
  
  
    //To-do document the expected itemResponses order
  //  var course_with_students = itemResponses[0].getResponses();
  // Get from form: 
   const form = FormApp.getActiveForm(),
      formResponses = form.getResponses(),
      latestFR = formResponses[form.getResponses().length-1];
   const itemResponses = latestFR.getItemResponses(),
      course_long_name      = itemResponses[0].getResponse(),
      course_short_name     = itemResponses[1].getResponse(),
      sub_account           = itemResponses[2].getResponse();
  
        
  
   console.log(itemResponses)
  
   
   
    for(var i = 0; i < itemResponses.length; i++ ) {
      Logger.log("Response #" + String(i) + ": " + itemResponses[i].getResponse());
    }
  
 //this term isn't the same as the # pulled in Terms, I have a special term for YR courses that are manually created. 
 //this is really important so they will actually close.  
    var term_id = "Eugene4J2024YR"; 
    Logger.log("Sub_account is = "+JSON.stringify(sub_account));
    find_sub(sub_account, email, term_id, course_long_name, course_short_name)
  }
  
  // We have all our sub accounts here so that it exists in the correct school. 
  function find_sub(sub_account, email, term_id, course_long_name, course_short_name){
    if(sub_account === "[Sheldon]") { canvas_account = 140;}
      else 
        if(sub_account === "[North]") { canvas_account = 160;}
          else
            if(sub_account === "[South]") { canvas_account = 157;}
              else
                if(sub_account === "[ECCO]") { canvas_account = 162;}
                else
                  if(sub_account === "[Churchill]") { canvas_account = 143;}
                    else
                      if(sub_account === "[Cal Young]") { canvas_account = 133;}
                        else
                          if(sub_account === "[ATA]") { canvas_account = 163;}
                            else
                              if(sub_account === "[Kelly]") { canvas_account = 156;}
                                else
                                  if(sub_account === "[Kennedy]") { canvas_account = 161;}
                                    else
                                      if(sub_account === "[Madison]") { canvas_account = 141;}
                                        else
                                          if(sub_account === "[Monroe]") { canvas_account = 158;}
                                            else
                                              if(sub_account === "[Roosevelt]") { canvas_account = 153;}
                                                else
                                                  if(sub_account === "[Spencer Butte]") { canvas_account = 142;}
                                                    else
                                                      if(sub_account === "[Training and PD]") { canvas_account = 167;}
      
      Logger.log("Canvas Account is now " +JSON.stringify(canvas_account));
  
      createCanvasCourse(email, term_id, course_long_name, canvas_account, course_short_name, default_settings = true);
  }
  
  
  function createCanvasCourse(email, term_id, course_long_name, canvas_account, course_short_name, default_settings=true ) {
    
    Logger.log("InFunctionCanvasAccount "+JSON.stringify(canvas_account));
    var matching_user = emailSearchEmployee(email);
    
    Logger.log("matching_user="+matching_user);
    if(matching_user == null) {
      Logger.log("-> No user to process. Halting execution.");
      return;
    } else {
      var ShortName = matching_user.name;
      var split     = ShortName.split(" ");
      var firstname = split[0];
      var lastname  = split[1];
      var user_id   = matching_user.id;
      Logger.log("-> User Processed: ShortName="+ShortName+" | "+"firstname="+firstname+" | "+"lastname="+lastname+" | "+"user_id="+user_id);
    }
    
    //EMAIL ADMIN IF UNABLE TO SPLIT RESULTS
    if(!split) {
      MailApp.sendEmail( {
          to: "adminemail@here.com", //add your email or other person supporting. 
          subject: "Course Creator Error: Unable to Split results",
          htmlBody: "Email="+email
          });
      return;
    }
  
  
  
  
  
  
    //SET COURSE NAME
    var new_course_name = course_long_name;
    Logger.log("--> NewCourseName= "+new_course_name);
  
  
    
  
  Logger.log("Canvas Acct Before Creating course ="+JSON.stringify(canvas_account));
    //SET UP COURSE OBJECT AND CREATE COURSE
    var obj = {
      "account_id" : canvas_account,
      "course"  : {
        "name"        : new_course_name,
        "term_id"     : "sis_term_id:"+term_id,
        "course_code" : course_short_name
      }
    };
  
    Logger.log("CourseObject="+obj);
    var createCourse = canvasAPI("POST /api/v1/accounts/:account_id/courses", obj);
  
    Logger.log("CreateCourseDetails"+JSON.stringify(createCourse));
  
  
  
    var course_ids = createCourse["id"];
    Logger.log("Course_ID Value "+JSON.stringify(course_ids));
    
    var source_id = #####;// You need to add a course ID for the template import. 
    if(default_settings) {
      //IMPORT DEFAULT SETTINGS TO NEWLY CREATED COURSE
      var contentMigration = importCourseSettings(course_ids, source_id);
      //EMAIL ADMIN IF SETTINGS IMPORT FAILED, AND CONTINUE PROCESSING
      if(contentMigration.workflow_state == 'failed') {
        MailApp.sendEmail({
          to: "reportingemail@here.com",// Add in your reporting email here. 
          subject: "Course Creator Warning: Settings Migration Failed Immediately",
          htmlBody: "Email="+email+", course_id"+course_id
        });
      }
    }
  
  
  
    //SET UP ENROLLMENT OBJECT AND ENROLL USER SUBMITTING FORM INTO THE COURSE
    // You need to have the corrected ROLE ID- mine is for a CourseAdmin
    var obj = {
      "course_id" : course_ids,
      "enrollment" : {
        "user_id" : user_id,
        "enrollment_state": "active",
        "role_id" : '119' //Use correct ID here. 
      }
    };
    var enrollUser = canvasAPI("POST /api/v1/courses/:course_id/enrollments", obj);
  
    //DEBUG LOGGING
    Logger.log("CanvasAccount="+canvas_account+", CourseName="+new_course_name+", TermID="+term_id);
    Logger.log(createCourse);
  //Add email down here. 
    MailApp.sendEmail({
           to: "reportemail@here.com",
           cc: email,
  
           subject: "Your Canvas club has been created:"+email,
           htmlBody: "<B>User Properties:</B> <ul><li>Email= "+email+"</li>  <li>ShortName= "+ShortName+"</li> <li>Firstname= "+firstname+"</li> <li>Lastname= "+lastname+"</li> <li>UserID= "+user_id+"</li><BR><BR><li> Please allow 3-4 minutes for your course to be populated into Canvas with the relevant Course Template</li><b>Course Properties:</b><ul><li>CourseName= "+new_course_name+"</li> <li> Course Link =  https://4j.instructure.com/courses/"+course_ids+"</li><li>TermID= "+term_id+"</li> <li>CourseID= "+course_ids+"</li> <li>EnrollUserResponse= "+enrollUser+"</li></ul>"
     });
     return createCourse;
  }
  
  
  
  
  
  
  
  