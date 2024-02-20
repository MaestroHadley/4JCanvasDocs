// These helper functions check the first character of the sis_user_id of a Canvas User object.
//All our Staff SIS'Id's start with Staff, so 'S'

function isEmployee(CanvasUser) {
    return(CanvasUser.sis_user_id[0] == 'S' || CanvasUser.sis_user_id[0] == 's');
  }
  function isAux(CanvasUser) {
    return(CanvasUser.sis_user_id[0] == 'A' || CanvasUser.sis_user_id[0] == 'a');
  }
  function isParent(CanvasUser) {
    return(CanvasUser.sis_user_id[0] == 'P' || CanvasUser.sis_user_id[0] == 'p');
  }