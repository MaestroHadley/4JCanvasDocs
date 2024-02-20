/**
* @function This function uses the canvasAPI function to search for a user matching
*           an email address. The function will only return a Canvas User object if
*           a matching user was found with a SIS ID beginning with "E".
* @param  {string}
*           email - Email to be used as search term for user lookup.
* @return {Object}
*           If match found, return Canvas User object in JSON format from canvasAPI call.
*           If no match found, return null.
*
* @to-do  Allow optional parameter for 'E-number only' or 'E / A numbers'
*/
function emailSearchEmployee(email) {

    var o = { "search_term": email };
    var self = canvasAPI("GET /api/v1/accounts/1/users", o);
  
    // CHECK SEARCH RESULTS FOR EXACT EMAIL MATCH AND EMPLOYEE STATUS
    // 'index' will be -1 if the user's email did not match any BLEND users or if not an Employee (E-#)
    var index = -1;
    for (var i = 0; i < self.length; i++) {
      var obj = { ":id": "" + self[i].id };
      var usercheck = canvasAPI("GET /api/v1/users/:id", obj);
      if (usercheck.email == email && isEmployee(usercheck)) {
        index = i;
        Logger.log("Employee found: Sortable Name="+self[index].sortable_name+" | "+"Canvas ID="+self[index].id);
      }
    }
  
    // If no matching Employee-user found, return null
    if( index == -1) {
      Logger.log("EXITING -- No S#-associated user found for email:"+email);
      return null;
    }
    // Otherwise, return the correct search result.
    return self[index];
  
  }