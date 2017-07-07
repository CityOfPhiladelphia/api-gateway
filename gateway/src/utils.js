const fs = require('fs'),
      util = require('util');

const yaml = require('js-yaml'),
      forwarded = require('forwarded'),
      winston = require('winston'),
      AWS = require('aws-sdk'),
      Address6 = require('ip-address').Address6,
      Address4 = require('ip-address').Address4;

module.exports.GATEWAY_API_BASE_URL = process.env.GATEWAY_API_BASE_URL || 'http://localhost:5000';

module.exports.GATEWAY_API_TOKEN = process.env.GATEWAY_KEY;

module.exports.GATEWAY_REDIS_URL = process.env.GATEWAY_REDIS_URL || 'redis://127.0.0.1:6379';

module.exports.GATEWAY_TIMEOUT = parseInt(((process.env.GATEWAY_TIMEOUT || 300) * 1000) + '') ;

module.exports.GATEWAY_HTTP_PORT = parseInt((process.env.GATEWAY_HTTP_PORT || 8080) + '');

const SQS_QUEUE_URL = process.env.SQS_QUEUE_URL;

const logger = new (winston.Logger)({
  transports: [
    new (winston.transports.Console)({ handleExceptions: true })
  ]
});

module.exports.logger = logger;

AWS.config.update({ region:'us-east-1' });

var sqs;
if (SQS_QUEUE_URL) {
  sqs = new AWS.SQS();
} else {
  logger.warn('Not using SQS logging');
}

module.exports.getUserIp = function (req) {
  var ips = forwarded(req);
  var rawIP = ips[ips.length - 1];
  var address = new Address6(rawIP);
  if (address.isValid()) {
    if (address.is4())
      return address.to4().address; // normalize to ipv4 if in range
  } else {
    address = new Address4(rawIP);
    if (!address.isValid()) {
      logger.error(rawIP + ' is not a valid IPv4 or IPv6 address');
      return null;
    }
  }
  return address.address;
}

module.exports.getConfig = function () {
  const configPath = process.env.GATEWAY_CONFIG_PATH || '../config/config.yml';

  const config = yaml.safeLoad(fs.readFileSync(configPath, 'utf8'));

  // compile regexs
  for (var i in config.endpoints) {
    var endpoint = config.endpoints[i];
    config.endpoints[i].pattern = new RegExp(endpoint.pattern, endpoint.patternFlags);
  }

  return config;
}

const keyRegex = /(.*gatekeeper=)([0-9a-f]+)(.*)/i;

function removeKey(input) {
  if (input)
    return input.replace(keyRegex, '$1REDACTED$3');
}

module.exports.logRequest = logRequest = function (req, res) {
  const elapsedTime = (new Date()) - req.startTime;
  const startTime = req.startTime.toISOString();

  const path = removeKey(req.url)
  const proxiedPath = removeKey(req.proxyUrl);
  const contentLength = res.headers &&
      res.headers['content-length'] &&
      parseInt(res.headers['content-length']);
  const userAgent = res.headers && res.headers['user-agent'];

  logger.info(util.format(
    '%s %s %s %s %s %s %s %s %s %s %s',
    req.userIP,
    req.tokenId || '-',
    startTime,
    req.requestId || '-',
    req.endpoint || '-',
    req.method,
    res.statusCode,
    path,
    proxiedPath || '-',
    elapsedTime,
    contentLength || '-',
    userAgent && util.format('"%s"', userAgent) || '-'));

  if (SQS_QUEUE_URL) {
    const message = {
      user_ip: req.userIP,
      token_id: req.tokenId || null,
      start_time: startTime,
      request_id: req.requestId || null,
      endpoint_name: req.endpoint || null,
      method: req.method,
      status_code: res.statusCode,
      path: path,
      proxied_path: proxiedPath || null,
      elapsed_time: elapsedTime,
      content_length: contentLength || null,
      user_agent: userAgent || null
    };

    sqs.sendMessage({
      MessageBody: JSON.stringify(message),
      QueueUrl: SQS_QUEUE_URL
    }, function(err, data) {
      if (err) logger.error(err);
    });
  }
}

module.exports.abort = function (req, res, statusCode, body) {
  res.statusCode = statusCode;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(body));

  logRequest(req, res);
}
