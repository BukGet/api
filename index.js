 //Include the cluster module
var cluster = require('cluster');
var config = require('./config');
  
// Code to run if we're in the master process
if (cluster.isMaster) {
  var MiniOps = require('miniops');
  var restify = require('restify');
  var miniOps = new MiniOps(24);

  var stats = restify.createServer();
  stats.use(restify.jsonp());
  stats.get('/ops', miniOps.dataHub());
  stats.listen(9133);
  // Count the machine's CPU cores
  var cpuCount = require('os').cpus().length - 1;
  if (cpuCount < 1) {
    cpuCount = 1;
  }

  // Create a worker for each cpu core - 1
  for (var i = 0, il=cpuCount; i < il; i++) {
    var worker = cluster.fork();
    worker.on('message', function (msg) {
      miniOps.recorder()(msg.req, msg.res, msg.route, msg.error);
    });
  }

  // Listen for dying workers
  cluster.on('exit', function (worker) {
    // Replace the dead worker, we're not sentimental
    console.log('Worker ' + worker.id + ' died');

    var worker = cluster.fork();
    worker.on('message', function (msg) {
      miniOps.recorder()(msg.req, msg.res, msg.route, msg.error);
    });
  });

} else {
  require('./server')(config.database.host + config.database.name, function (callback) {
    //Start webserver
    callback.listen(config.port, config.address);
  });
  console.log('Worker ' + cluster.worker.id + ' running!');
}