const request = require('request'),
      cacheManager = require('cache-manager'),
      redisStore = require('cache-manager-redis');

const utils = require('./utils');

var memoryCache = cacheManager.caching({ store: 'memory', max: 10000, ttl: 60 /*seconds*/ });
var redisCache = cacheManager.caching({
  store: redisStore,
  url: utils.GATEWAY_REDIS_URL,
  ttl: 600 // seconds
});

redisCache.store.events.on('redisError', function(err) {
  utils.logger.error(err);
});

var banCache = cacheManager.multiCaching([memoryCache]);

function fetchBan(ip, callback) {
  request(
    utils.GATEWAY_API_BASE_URL + '/bans/cidr-blocks',
    {
      auth: {
        bearer: utils.GATEWAY_API_TOKEN
      },
      qs: {
        cidr__contains: ip
      }
    },
    function (err, banRes, body) {
      if (err) return callback(err);

      if (banRes.statusCode != 200)
        return callback(new Error('Error checking bans'));

      var data = JSON.parse(body);

      if (data && data.count === 0)
        return callback(null, false);

      callback(null, true);
    });
}

function checkBanCached(ip, callback) {
  const cacheKey = 'bans:' + ip;

  banCache.get(cacheKey, function (err, data) {
    if (err) return callback(err);

    if (data === undefined)
      return callback(null, data);

    fetchBan(ip, function (err, data) {
      if (err) return callback(err);

      banCache.set(cacheKey, data);

      callback(null, data);
    });
  });
}

module.exports.checkBan = function (req, res, callback) {
  const ip = req.userIP || utils.getUserIp(req);
  
  checkBanCached(ip, function (err, banned) {
    if (err) return callback(err);

    if (banned === true)
      return utils.abort(req, res, 403, { message: 'Your IP has been banned.' });

    callback();
  });
}
