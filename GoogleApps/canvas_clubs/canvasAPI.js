//CANVAS API FUNCTION, THIS IS CALLED BY CODE.GS. 

//This token does not expire
var access_token = 'YOURAPIKEY' ;
var host = 'YOUR INSTRUCTURE LINK' ;

/**
* @function convert the parameters into a Query String
* @param {Object}
*          obj - the parameters to include
* @returns {String} the query string
*/
function makeQueryString(obj) {
  var q = [];
  var j;
  for ( var i in obj) {
    if (obj.hasOwnProperty(i)) {
      var item = obj[i];
      if (typeof item == 'object') {
        if (Array.isArray(item)) {
          for (j = 0; j < item.length; j++) {
            q.push(i + '[]=' + item[j]);
          }
        } else {
          for (j in item) {
            if (item.hasOwnProperty(j)) {
              q.push(i + '[' + j + ']=' + item[j]);
            }
          }
        }
      } else {
        q.push(i + '=' + item);
      }
    }
  }
  return q.join('&');
}

/**
* @function This function calls the CanvasAPI and returns any information as an
*           object.
* @param {string}
*          endpoint - The endpoint from the Canvas API Documentation, including
*          the GET, POST, PUT, or DELETE the /api/v1 version is optional and
*          will add the value specified within the function as a default if not
* @param {Object}
*          [opts] - The parameters that need passed to the API call Variable
*          substitution is done for values in the endpoint that begin with :
*          SIS variables can be specified as ":sis_user_id: 123" rather than
*          "user_id: ':sis_user_id:123'" Any other variables are added to the
*          querystring for a GET or the payload for a PUT or POST
* @param {Object[]}
*          [filter] - An array containing values to return. This allows you to
*          reduce storage by eliminating unnecessary objects
*/
function canvasAPI(endpoint, opts, filter) {
  if (typeof endpoint === 'undefined') {
    return;
  }
  if (typeof opts === 'undefined') {
    opts = {};
  }
  
  var PER_PAGE = 100;
  var API_VERSION = 1;
  
  var endpointRegex = /^(GET|POST|PUT|DELETE|HEAD)\s+(.*)$/i;
  var tokenRegex = new RegExp('^:([a-z_]+)$');
  var nextLinkRegex = new RegExp('<(.*?)>; rel="next"');
  //  var integerRegex = new RegExp('^[0-9]+$');
  var data;
  
  try {

    var parms = {
      'headers': {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    if (typeof endpoint !== 'string') {
      throw 'Endpoint specification must be a string. Received: ' + typeof endpoint;
    }
    var endpointMatches = endpointRegex.exec(endpoint);
    if (endpointMatches === null) {
      throw 'Invalid endpoint specified: ' + endpoint;
    }
    parms.method = endpointMatches[1].toLowerCase();
    var routes = endpointMatches[2].split('/');
    var route = [];
    var j;
    for (var i = 0; i < routes.length; i++) {
      if (routes[i]) {
        if (route.length == 0 && routes[i] != 'api') {
          route.push('api');
          route.push('v' + API_VERSION);
          i++;
        }
        var matches = tokenRegex.exec(routes[i]);
        if (matches !== null) {
          if (typeof opts !== 'object') {
            throw 'Options is not an object but variable substitutions is needed';
          }
          var tokens = [ routes[i], matches[1], ':sis_' + matches[1],
              'sis_' + matches[1] ];
          var tokenMatch = false;
          j = 0;
          while (!tokenMatch && j < tokens.length) {
            var token = tokens[j++];
            if (typeof opts[token] !== 'undefined') {
              tokenMatch = true;
              route.push(opts[token]);
              opts[token] = null;
            }
          }
          if (!tokenMatch) {
            throw 'Unable to find substitution for :' + matches[1] + ' in ' + endpointMatches[2];
          }
        } else {
          route.push(routes[i]);
        }
      }
    }
    var payload = {};
    if (typeof opts === 'object') {
      for ( var field in opts) {
        if (opts.hasOwnProperty(field) && opts[field] !== null && !/^:/.test(field)) {
          payload[field] = opts[field];
        }
      }
    }
    var url = 'https://' + host + '/' + route.join('/');
    data = [];
    if (parms.method == 'get' || parms.method == 'delete') {
      if (parms.method == 'get' && !payload.per_page) {
        payload.per_page = PER_PAGE;
      }
      var queryStr = makeQueryString(payload);
      if (queryStr) {
        url += '?' + queryStr;
        url = encodeURI(url);
      }
    } else if (parms.method == 'post' || parms.method == 'put') {
      parms.payload = JSON.stringify(payload);
    }
    while (url !== null) {
      var response = UrlFetchApp.fetch(url, parms);
      url = null;
      if (response.getResponseCode() == 200) {
        var headers = response.getAllHeaders();
        if (parms.method == 'get' && typeof headers.Link !== 'undefined') {
          var links = headers.Link.split(',');
          if (typeof links === 'object') {
            for (var l = 0; l < links.length; l++) {
              var linkMatch = nextLinkRegex.exec(links[l]);
              if (linkMatch !== null) {
                url = linkMatch[1];
              }
            }
          }
        }
        var json = JSON.parse(response.getContentText());
        var key;
        if (typeof json === 'object') {
          if (Array.isArray(json)) {
            for ( var item in json) {
              if (json.hasOwnProperty(item)) {
                var entry = json[item];
                if (typeof filter !== 'undefined') {
                  var row = {};
                  for (j in filter) {
                    if (filter.hasOwnProperty(j)) {
                      key = filter[j];
                      if (typeof entry[key] !== 'undefined') {
                        if (Array.isArray(entry[key])) {
                          row[key] = entry[key].slice(0);
                        } else {
                          row[key] = entry[key];
                        }
                      }
                    }
                  }
                  data.push(row);
                } else {
                  data.push(entry);
                }
              }
            }
          } else {
            if (typeof filter === 'undefined') {
              data = json;
            } else {
              for (j in filter) {
                if (filter.hasOwnProperty(j)) {
                  key = filter[j];
                  if (typeof json[key] !== 'undefined') {
                    if (Array.isArray(json[key])) {
                      data[key] = json[key].slice(0);
                    } else {
                      data[key] = json[key];
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  } catch (e) {
    Logger.log(e);
    return;
  }
  return data;
}
