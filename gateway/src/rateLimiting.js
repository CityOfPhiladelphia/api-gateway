const Limiter = require('ratelimiter');

const utils = require('./utils');

const DEFAULT_RATE_LIMIT_WINDOW = 900000; // default 15 minutes
const DEFAULT_RATE_LIMIT_MAX = 100; // requests per window

function getKey(endpoint, tokenId, req) {
  var user;
  if (tokenId)
    user = tokenId;
  else
    user = req.userIP || utils.getUserIp(req);

  return 'limits:' + user + ':' + endpoint.name;
}

function setRatelimit(limitConfig, endpoint, tokenId) {
  if (tokenId && endpoint.rateLimit && endpoint.rateLimit.authenticated) {
    limitConfig.duration = endpoint.rateLimit.authenticated.windowMs || DEFAULT_RATE_LIMIT_WINDOW;
    limitConfig.max = endpoint.rateLimit.authenticated.max || DEFAULT_RATE_LIMIT_MAX;
  } else if (endpoint.rateLimit && endpoint.rateLimit.anonymous) {
    limitConfig.duration = endpoint.rateLimit.anonymous.windowMs || DEFAULT_RATE_LIMIT_WINDOW;
    limitConfig.max = endpoint.rateLimit.anonymous.max || DEFAULT_RATE_LIMIT_MAX;
  } else {
    limitConfig.duration = DEFAULT_RATE_LIMIT_WINDOW;
    limitConfig.max = DEFAULT_RATE_LIMIT_MAX;
  }
}

module.exports.rateLimit = function (redisclient, endpoint, tokenId, req, res, callback) {
  var limitKey = getKey(endpoint, tokenId, req)

  var limitConfig = {
    id: limitKey,
    db: redisclient
  }

  setRatelimit(limitConfig, endpoint, tokenId);

  var limit = new Limiter(limitConfig);

  limit.get(function (err, limit) {
    if (err) return callback(err);

    res.setHeader('X-RateLimit-Limit', limit.total);
    res.setHeader('X-RateLimit-Remaining', limit.remaining - 1);
    res.setHeader('X-RateLimit-Reset', limit.reset);

    if (limit.remaining) return callback();

    var delta = (limit.reset * 1000) - Date.now() | 0;
    var after = limit.reset - (Date.now() / 1000) | 0;
    res.setHeader('Retry-After', after);

    utils.abort(req, res, 429, { message: 'Too many requests, retry in ' + ms(delta, { long: true }) })
  });
}
