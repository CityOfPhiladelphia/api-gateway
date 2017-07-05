const http = require('http'),
      chai = require('chai'),
      chaiHttp = require('chai-http'),
      should = chai.should();

process.env.GATEWAY_CONFIG_PATH = '../config/test_config.yml'

const server = require('../gateway').server

chai.use(chaiHttp);

var mockResponse = {
  statusCode: 200,
  body: {
    foo: 'bar'
  }
}

http.createServer(function (req, res) {
  res.statusCode = mockResponse.statusCode;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(mockResponse.body));
}).listen(8085)

describe('API Gateway', function () {
  it('should proxy requests', function (callback) {
      chai.request(server)
        .get('/myapi/v1/foo')
        .end(function (err, res){
          res.should.have.status(200);
          callback();
        });
  });
});
