const request = require('request'),
      querystring = require('querystring'),
      cacheManager = require('cache-manager');

const utils = require('./utils');

function checkKey(key, callback) {
  request(
    utils.GATEWAY_API_BASE_URL + '/keys',
    {
      auth: {
        bearer: utils.GATEWAY_API_TOKEN
      },
      qs: {
        key: key,
        active: true
      }
    },
    function (err, res, body) {
      if (err) return callback(err);

      if (res.statusCode != 200)
        return callback(new Error('Error checking key'));

      var data = JSON.parse(body);

      if (data && data.count > 0)
        callback(null, data.data[0]);

      callback(null, false);
    });
}

function unauthorized(req, res) {
  utils.abort(req, res, 401, { message: 'Unauthorized' });
}

var keyCache = cacheManager.caching({ store: 'memory', max: 10000, ttl: 60 /*seconds*/ });

function cachedCheckKey(key, callback) {
  keyCache.wrap(key, function (cacheCallback) {
    checkKey(key, cacheCallback);
  }, callback);
}

module.exports.authenticate = function (endpoint, req, res, callback) {
  var key = null;
  var keyUsed = false;

  var splitUrl = req.url.split('?');
  if (splitUrl.length > 1) {
    var qs = querystring.parse(splitUrl[1]);
    if (qs.gatekeeper) {
      key = qs.gatekeeper;
      keyUsed = true;
    }
  }

  if (key === null && !keyUsed)
    return process.nextTick(callback);

  if (!(/^[0-9a-f]{32,63}$/).test(key))
    return unauthorized(req, res);

  cachedCheckKey(key, function (err, key) {
    if (err) return callback(err);

    if (key === false) return unauthorized(req, res);

    callback(null, key.id);
  });
}
