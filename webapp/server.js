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

// error handler
app.use(function*(next) {
  try {
    yield next;
  } catch(error) {
    this.status = error.status || 500;
    this.body = {
      message: error.message || 'Server Error'
    };
    this.app.emit('error', error, this);
  }
});

app.use(function*(next) {
  if (this.path.indexOf('/api') !== -1) {
    // api call
    yield next;
  } else if (yield send(this, this.path, config.SEND_OPTIONS)) {
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

router.get('/ping', function*() {
  this.body = Date();
});

router
  .post('/api/authenticate', function*() {
    var data = this.request.body;
    var user, hash, salt;

    if(data.email && data.password) {
      user = yield db.getUser(data.email);
      if(user) {
        salt = utils.extractSalt(user.password);
        hash = yield utils.hashPassword(data.password, salt);
        if(utils.appendSalt(hash, salt) === user.password) {
          this.status = 201;
          this.body = {
            email: user.email,
            thermostat_id: user.thermostatId
          };
          return;
        }
      }
      this.throw('Invalid email and/or password', 401);
    }
    this.throw('Missing fields', 400);
  });

router
  .get('/api/user', function*() {
    var query = this.request.query;
    var user;

    if(query.email) {
      user = yield db.getUser(decodeURIComponent(query.email));
      if(user) {
        this.body = {
          email: user.email
        };
        return;
      }
      this.throw('User not found', 404);
    }
    this.throw('Invalid query', 400);
  })
  .post('/api/user', function*() {
    var data = this.request.body;
    var user, hash, salt, thermostat;

    if(data.email && data.password && data.thermostat_id) {
      // validate thermostat id
      thermostat = yield db.getThermostat(data.thermostat_id);
      if(!thermostat) {
        this.throw('Invalid thermostat id', 400);
      } else if(thermostat.registered) {
        this.throw('Thermostat ID already registered', 400);
      }

      // create user
      user = yield db.getUser(data.email);
      if(!user) {
        salt = utils.generateSalt();
        hash = yield utils.hashPassword(data.password, salt);
        user = yield db.insertUser(data.email, utils.appendSalt(hash, salt), data.thermostat_id);
        yield db.registerThermostat(data.thermostat_id);
        this.body = {
          email: user.email
        };
        this.status = 201;
        return;
      }
      this.throw('Email already in use', 400);
    }
    this.throw('Missing fields', 400);
  })
  .put('/api/user', function*() {
    // TODO
  });

router
  .post('/api/thermostat', function*() {
    var data = this.request.body;
    var thermostat;

    if(data.id) {
      thermostat = yield db.getThermostat(data.id);
      if(thermostat) {
        this.throw('Thermostat already exists', 400);
      }
      thermostat = yield db.insertThermostat(data.id);
      this.body = thermostat;
      this.status = 201;
      return;
    }
    this.throw('Missing fields', 400);
  })
  .get('/api/thermostat/:id', function*() {
    var thermostatId = this.params.id;
    var thermostat = yield db.getThermostat(thermostatId);
    if(thermostat) {
      this.body = thermostat;
      return;
    }
    this.throw('Thermostat not found', 404);
  });

app.use(router.routes());


app.listen(config.PORT);
console.log('listening on port ' + config.PORT);