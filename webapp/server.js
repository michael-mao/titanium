'use strict';

var koa = require('koa');
var router = require('koa-router')();
var send = require('koa-send');

var app = koa();

var config = {
  port: 3000,
  sendOptions: {
    root: __dirname + '/app'
  }
};

app.use(router.routes());

app.use(function* (){
  if (yield send(this, this.path, config.sendOptions)) {
    // file exists and request successfully served so do nothing
    return;
  } else if (this.path.indexOf('.') !== -1) {
    // file does not exist so do nothing and koa will return 404 by default
    // we treat any path with a dot '.' in it as a request for a file
    return;
  } else {
    // let angular handle routing
    yield send(this, '/index.html', config.sendOptions);
  }
});

app.listen(config.port);
console.log('listening on port ' + config.port);