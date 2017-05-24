'use strict';

const http = require('http');

const httpProxy = require('http-proxy'),
      redis = require('redis'),
      uuid = require('node-uuid');

const authentication = require('./lib/authentication'),
      bans = require('./lib/bans'),
      rateLimiting = require('./lib/rateLimiting'),
      utils = require('./lib/utils');

const redisclient = redis.createClient({
  url: process.env.GATEWAY_REDIS_URL || 'redis://127.0.0.1:6379'
});

const config = utils.getConfig();

function getEndpoint(url) {
  for (var i in config.endpoints) {
    if (config.endpoints[i].pattern.test(url))
      return config.endpoints[i];
  }
}

const proxy = httpProxy.createProxyServer({});

proxy.on('error', function(err) {
  utils.logger.error(err);
});

proxy.on('proxyReq', function(proxyReq, req, res, options) {
  req.proxyUrl = proxyReq.path;
  proxyReq.setHeader('X-Request-ID', req.requestId);
  res.setHeader('X-Request-ID', req.requestId);
});

proxy.on('proxyRes', function (proxyRes, req, res) {
  utils.logRequest(req, proxyRes);
});

function errorReq(req, res, err) {
  utils.logger.error(err)

  utils.abort(req, res, 500, { message: 'Internal Server Error' });
}

http.createServer(function(req, res) {
  // TODO: try/catch with 500?

  // TODO: header injections? - like CORS

  req.startTime = new Date();
  req.userIP = utils.getUserIp(req);

  bans.checkBan(req, res, function (err) {
    if (err) return errorReq(req, res, err);

    req.requestId = uuid.v4();

    const endpoint = getEndpoint(req.url);

    if (!endpoint)
      return utils.abort(req, res, 404, { message: 'Route not found' });

    var target = req.url.replace(endpoint.pattern, endpoint.target);

    authentication.authenticate(endpoint, req, res, function (err, tokenId) {
      if (err) return errorReq(req, res, err);

      req.tokenId = tokenId;

      rateLimiting.rateLimit(redisclient, endpoint, tokenId, req, res, function () {
        req.endpoint = endpoint.name;
        
        proxy.web(req, res, {
          target: target,
          ignorePath: true,
          xfwd: true,
          preserveHeaderKeyCase: true
        });
      });
    });
  });
})
.listen(process.env.GATEWAY_HTTP_PORT || 8080, function () {
  utils.logger.info('Gateway up...');
});
