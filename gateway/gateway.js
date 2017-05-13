'use strict';

const fs = require('fs'),
      http = require('http'),
      querystring = require('querystring');

const yaml = require('js-yaml'),
      httpProxy = require('http-proxy'),
      winston = require('winston'),
      forwarded = require('forwarded'),
      Limiter = require('ratelimiter'),
      redis = require('redis');

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
  throw new Error('No endpoint pattern matches: ' + url);
}

const proxy = httpProxy.createProxyServer({});

proxy.on('error', function(err) {
  logger.error('Error proxying request: ' + err);
});

function errorReq(req, res, err) {
  res.statusCode = 500;
  res.end();
}

function proxyReq(req, res, target) {
  logger.info('URL: ' + req.url + ' Target: ' + target);

  proxy.web(req, res, { target: target });
}

function authenticate(endpoint, req, callback) {
  var key = null;

  var splitUrl = req.url.split('?');
  if (splitUrl.length > 1) {
    var qs = querystring.parse(splitUrl[1]);
    if (qs.gatekeeper)
      key = qs.gatekeeper;
  }

  // TODO: validate using regex

  if (key === null)
    return process.nextTick(callback);

  // TODO: auth against /keys?key={key}
  // TODO: cache key -> id or null response in memory - avoid placing keys in redis.
  //       Use LRU - keeps memory from overflowing. Number of possible fake keys are infinite, not IPs

  callback(null, key); // TODO: return key id instead
}

function getKey(endpoint, tokenId, req) {
  var user;
  if (tokenId)
    user = tokenId;
  else {
    var addresses = forwarded(req);
    user = addresses[addresses.length - 1]
  }

  return user + ':' + endpoint.name;
}

function rateLimit(endpoint, tokenId, req, res, callback) {
  var limitKey = getKey(endpoint, tokenId, req)

  var limit = new Limiter({
    id: limitKey,
    db: redisclient,
    duration: endpoint.windowMs || 900000, // default 15 minutes
    max: endpoint.max || 100 // default 100 per window
  });

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

http.createServer(function(req, res) {
  // TODO: try/catch with 500?

  // TODO: check ban

  var endpoint = getEndpoint(req.url);
  var target = req.url.replace(endpoint.pattern, endpoint.target);

  authenticate(endpoint, req, function (err, tokenId) {
    if (err) return errorReq(req, res, err);

    rateLimit(endpoint, tokenId, req, res, function () {
      proxyReq(req, res, target);
    });
  })
})
.listen(process.env.GATEWAY_HTTP_PORT || 8080);
