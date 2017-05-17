'use strict';

const fs = require('fs'),
      http = require('http'),
      querystring = require('querystring');

const yaml = require('js-yaml'),
      httpProxy = require('http-proxy'),
      winston = require('winston'),
      forwarded = require('forwarded'),
      Limiter = require('ratelimiter'),
      redis = require('redis'),
      request = require('request'),
      uuid = require('node-uuid');

const DEFAULT_RATE_LIMIT_WINDOW = 900000; // default 15 minutes
const DEFAULT_RATE_LIMIT_MAX = 100; // requests per window

const GATEWAY_API_BASE_URL = process.env.GATEWAY_API_BASE_URL || 'http://localhost:5000';
const GATEWAY_API_TOKEN = process.env.GATEWAY_KEY;

const logger = new (winston.Logger)({
  transports: [
    new (winston.transports.Console)({ handleExceptions: true })
  ]
});

const redisclient = redis.createClient({
  url: process.env.GATEWAY_REDIS_URL || 'redis://127.0.0.1:6379'
});

const configPath = process.env.GATEWAY_CONFIG_PATH || '../config/config.yml';

const config = yaml.safeLoad(fs.readFileSync(configPath, 'utf8'));

// compile regexs
for (var i in config.endpoints) {
  config.endpoints[i].pattern = new RegExp(config.endpoints[i].pattern);
}

function getEndpoint(url) {
  for (var i in config.endpoints) {
    if (config.endpoints[i].pattern.test(url))
      return config.endpoints[i];
  }
  throw new Error('No endpoint pattern matches: ' + url); // TODO: callback error?
}

const proxy = httpProxy.createProxyServer({});

proxy.on('error', function(err) {
  logger.error('Error proxying request: ' + err);
});

proxy.on('proxyReq', function(proxyReq, req, res, options) {
  var requestId = uuid.v4();
  proxyReq.setHeader('X-Request-ID', requestId);
  res.setHeader('X-Request-ID', requestId);
});

function errorReq(req, res, err) {
  logger.error(err)

  res.statusCode = 500;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ message: 'Internal Server Error' }));
}

function proxyReq(req, res, target) {
  // TODO: flesh out more. is there logging standards?
  logger.info('URL: ' + req.url + ' Target: ' + target);

  proxy.web(req, res, { target: target });
}

function checkKey(key, callback) {
  request(
    GATEWAY_API_BASE_URL + '/keys?key=' + key,
    { auth: { bearer: GATEWAY_API_TOKEN } },
    function (err, res, body) {
      if (err) return callback(err);

      if (res.statusCode != 200)
        return callback(new Error('Error checking key'));

      var data = JSON.parse(body);

      if (data.count > 0)
        callback(null, data.data[0]);

      callback(null, false);
    });
}

function unauthorized(res) {
  res.statusCode = 401;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ message: 'Unauthorized' }));
}

function authenticate(endpoint, req, res, callback) {
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
    return unauthorized(res);

  // TODO: cache key -> id or null response in memory - avoid placing keys in redis.
  //       Use LRU - keeps memory from overflowing. Number of possible fake keys are infinite, not IPs

  checkKey(key, function (err, key) {
    if (err) return callback(err);

    if (key === false) return unauthorized(res);

    callback(null, key.id);
  });
}

function getUserIp(req) {
  var addresses = forwarded(req);
  return addresses[addresses.length - 1]
}

function getKey(endpoint, tokenId, req) {
  var user;
  if (tokenId)
    user = tokenId;
  else
    user = getUserIp(req);

  return user + ':' + endpoint.name;
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

function rateLimit(endpoint, tokenId, req, res, callback) {
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
    res.setHeader('Content-Type', 'application/json');
    res.statusCode = 429;
    res.end(JSON.stringify({ message: 'Too many requests, retry in ' + ms(delta, { long: true }) }));
  });
}

function checkBan(req, res, callback) {
  var ip = getUserIp(req); // TODO: add this to request for use by getKey?
  request( // TODO: cache in redis
    GATEWAY_API_BASE_URL + '/bans/cidr-blocks?cidr__contains=' + ip,
    { auth: { bearer: GATEWAY_API_TOKEN } },
    function (err, banRes, body) {
      if (err) return callback(err);

      if (banRes.statusCode != 200)
        return callback(new Error('Error checking bans'));

      var data = JSON.parse(body);

      if (data.count === 0)
        return callback();

      res.statusCode = 403;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ message: 'Your IP has been banned.' }));
    });
}

http.createServer(function(req, res) {
  // TODO: try/catch with 500?

  // TODO: set common proxy headers - is this done by the proxy lib? - http://docs.aws.amazon.com/elasticloadbalancing/latest/classic/x-forwarded-headers.html
  // TODO: create global limit?
  // TODO: blow away existing X-Forwarded-For ? could be a security issue
  // TODO: allow case insentive patterns? just pass an options key/value?
  // TODO: header injections? - like CORS

  checkBan(req, res, function (err) {
    if (err) return errorReq(req, res, err);

    var endpoint = getEndpoint(req.url);
    var target = req.url.replace(endpoint.pattern, endpoint.target);

    authenticate(endpoint, req, res, function (err, tokenId) {
      if (err) return errorReq(req, res, err);

      rateLimit(endpoint, tokenId, req, res, function () {
        proxyReq(req, res, target);
      });
    });
  });
})
.listen(process.env.GATEWAY_HTTP_PORT || 8080, function () {
  logger.info('Gateway up...');
});
