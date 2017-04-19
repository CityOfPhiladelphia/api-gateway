'use strict';

const yaml = require('js-yaml'),
      fs = require('fs'),
      http = require('http'),
      httpProxy = require('http-proxy'),
      winston = require('winston'),
      RateLimit = require('express-rate-limit');

const logger = new (winston.Logger)({
  transports: [
    new (winston.transports.Console)({ handleExceptions: true })
  ]
});

const configPath = process.env.GATEWAY_CONFIG_PATH || '../config.yml';

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

var rateLimitOptions = {
  windowMs: 15*60*1000, // 15 minutes
  max: 2, // limit each IP to 100 requests per windowMs
  delayMs: 0, // disable delaying - full speed until the max limit is reached
  keyGenerator: function (req) {
    return req.ip;
    // TODO: chain order
    // - Bearer token
    // - gatekeeper query param
    // - X-Proxy header IP
    // - req.ip
  },
  handler: function (req, res) {
    res.statusCode = 429;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ message: 'Too many requests, please try again later.' }));
  }
}

var defaultRateLimiter = new RateLimit(rateLimitOptions);

// create rate limiters
for (var i in config.endpoints) {
  if (config.endpoints[i].rateLimit) {
    var options = config.endpoints[i].rateLimit;
    config.endpoints[i].rateLimiter = Object.assign({}, rateLimitOptions, {
      windowMs: options.windowMs || rateLimitOptions.windowMs,
      max: options.max || rateLimitOptions.max,
      delayMs: options.delayMs || rateLimitOptions.delayMs
    });
  }
}

http.createServer(function(req, res) {
  // TODO: try/catch with 500?

  // TODO: check ban
  // TODO: check api key

  var endpoint = getEndpoint(req.url);
  var target = req.url.replace(endpoint.pattern, endpoint.target);

  function nextWrapper(err) { // simulates express style next()
    if (err) return errorReq(req, res, err);

    proxyReq(req, res, target);
  }

  (endpoint.rateLimiter || defaultRateLimiter)(req, res, nextWrapper);
})
.listen(process.env.GATEWAY_HTTP_PORT || 8080);
