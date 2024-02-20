/**
* @function This function uses the canvasAPI function to copy course settings from
*           a Source Course to a Destination Course. Only Settings are copied.
* @param  {Number}
*           destination_course_id - The Canvas course_id TO which settings will be copied.
* @param  {Number}
*           source_course_id - The Canvas course_id FROM which settings will be copied.
* @return {Object}
*           Canvas ContentMigration object [https://canvas.instructure.com/doc/api/content_migrations.html#ContentMigration]
*
*/
function importCourseSettings(destination_course_id, source_course_id) {
    //IMPORT DEFAULT SETTINGS FROM "MCC_DefaultSettingsCourseId" COURSE
    var obj = {
      ":course_id" : destination_course_id,
      "migration_type" : "course_copy_importer",
      "selective_import" : true,
      "settings" : {
        'source_course_id' : source_course_id
      }
    };
    var contentMigration = canvasAPI("POST /api/v1/courses/:course_id/content_migrations", obj);
    
    var migrationId = contentMigration["id"];
    var obj = {
      ":course_id" : destination_course_id,
      ":id" : migrationId,
      "type" : "course_settings"
    };
    var updatedContentMigration = canvasAPI("PUT /api/v1/courses/:course_id/content_migrations/:id", obj);
    return updatedContentMigration;
  }
  
  /**
  * @function This function uses the canvasAPI function to copy course settings from
  *           a Source Course to a Destination Course. Only Settings are copied.
  * @param  {Number}
  *           destination_course_id - The Canvas course_id TO which settings will be copied.
  * @param  {Number}
  *           source_course_id - The Canvas course_id FROM which settings will be copied.
  * @param  {Number}
  *           module_id - The module_id to copy from the source course.
  * @return {Object}
  *           Canvas ContentMigration object [https://canvas.instructure.com/doc/api/content_migrations.html#ContentMigration]
  *
  */
  function importCourseModule(destination_course_id, source_course_id, module_id) {
    var obj = {
      ":course_id" : destination_course_id,
      "migration_type" : "course_copy_importer",
      //"selective_import" : true,
      "select" : {"modules" : [module_id]},
      "settings" : {
        'source_course_id' : source_course_id
      }
    };
    var contentMigration = canvasAPI("POST /api/v1/courses/:course_id/content_migrations", obj);
    return contentMigration;
  }
  
  