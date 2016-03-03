'use strict';

var koa = require('koa');
var router = require('koa-router')();
var send = require('koa-send');
var bodyParser = require('koa-bodyparser');
var config = require('./config');
var utils = require('./lib/utils');
var db = require('./lib/db');


var app = koa();


app.use(bodyParser());

router.get('/ping', function*() {
  this.body = Date();
});

router
  .post('/authenticate', function*() {
    var data = this.request.body;
    var user, hash, salt;

    this.status = 401;
    if(data.email && data.password) {
      user = yield db.getUser(data.email);
      if(user) {
        salt = utils.extractSalt(user.password);
        hash = yield utils.hashPassword(data.password, salt);
        if(utils.appendSalt(hash, salt) === user.password) {
          this.status = 201;
        }
      }
    }
  });

router
  .post('/api/user', function*() {
    var data = this.request.body;
    var user, hash, salt;

    if(data.email && data.password) {
      salt = utils.generateSalt();
      hash = yield utils.hashPassword(data.password, salt);
      user = yield db.insertUser(data.email, utils.appendSalt(hash, salt));
      this.body = {
        email: user.email
      };
    } else {
      this.status = 400;
    }
  })
  .put('/api/user', function*() {

  });

app.use(router.routes());

app.use(function*() {
  if (yield send(this, this.path, config.SEND_OPTIONS)) {
    // file exists and request successfully served so do nothing
    return;
  } else if (this.path.indexOf('.') !== -1) {
    // file does not exist so do nothing and koa will return 404 by default
    // we treat any path with a dot '.' in it as a request for a file
    return;
  } else {
    // let angular handle routing
    yield send(this, '/index.html', config.SEND_OPTIONS);
  }
});

app.listen(config.PORT);
console.log('listening on port ' + config.PORT);